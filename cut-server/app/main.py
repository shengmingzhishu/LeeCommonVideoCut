"""
FastAPI 应用入口
================
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import AppError
from app.core.logger import get_logger, setup_logging

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    setup_logging()
    logger.info(
        "🚀 cut-server 启动中...",
        extra={"version": settings.app_version, "database": settings.database_url.split("@")[-1]},
    )

    # 数据库表结构由 Alembic 管理（alembic upgrade head）
    # 开发模式兜底：表不存在时自动创建并给出提示（生产请先跑迁移）
    if settings.debug:
        try:
            from sqlalchemy import inspect

            inspector = inspect(engine)
            existing = set(inspector.get_table_names())
            expected = set(Base.metadata.tables.keys())
            missing = expected - existing

            if missing:
                Base.metadata.create_all(bind=engine)
                logger.warning(
                    f"⚠️ 检测到缺失表（{len(missing)} 个）已自动创建，建议执行 alembic upgrade head",
                    extra={"missing_tables": sorted(missing)},
                )
            else:
                logger.info("✅ 数据库表结构正常（Alembic 已迁移）")
        except Exception as e:
            logger.error(f"❌ 数据库检查失败: {e}")
            raise

    # 首次启动引导：users 表为空时按 BOOTSTRAP_ADMIN_* 配置创建首个管理员
    try:
        from sqlalchemy import func, select

        from app.core.database import session_scope
        from app.core.security import hash_password
        from app.models.user import User
        from app.utils.safe_path import gen_id

        with session_scope() as db:
            user_count = db.execute(select(func.count()).select_from(User)).scalar_one()
            if user_count == 0:
                db.add(
                    User(
                        id=gen_id("u"),
                        username=settings.bootstrap_admin_username,
                        password_hash=hash_password(settings.bootstrap_admin_password),
                        display_name="管理员",
                        is_admin=True,
                        membership_tier="free",
                        is_active=True,
                    )
                )
                db.commit()
                logger.info(
                    "👑 已创建首个管理员",
                    extra={"username": settings.bootstrap_admin_username},
                )
    except Exception as e:
        # 引导失败不阻塞启动（如表已存在但结构不符时仍能服务已有用户）
        logger.error(f"❌ 引导管理员创建失败: {e}")

    # 检测外部依赖
    from app.utils.ffmpeg import ffmpeg_available, ffprobe_available

    logger.info(
        f"📦 依赖检测: ffmpeg={'✅' if ffmpeg_available() else '❌'}, "
        f"ffprobe={'✅' if ffprobe_available() else '❌'}, "
        f"minimax={'✅' if settings.minimax_api_key != 'sk-cp-PUT-YOUR-REAL-KEY-HERE' else '⚠️未配置'}"
    )

    # 启动异步任务队列
    from app.tasks.task_queue import task_queue
    from app.tasks.task_worker import register_handlers

    register_handlers()
    await task_queue.start(worker_count=2)

    yield

    await task_queue.stop()
    logger.info("👋 cut-server 已关闭")


def create_app() -> FastAPI:
    app = FastAPI(
        title="漫剧推广素材剪辑师 API",
        description="前后端分离的漫剧剪辑师后端 · v4.0",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Trace-Id"],
    )

    # traceId 中间件
    from app.core.trace import TraceIdMiddleware
    app.add_middleware(TraceIdMiddleware)

    # 全局异常处理
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        trace_id = getattr(request.state, "trace_id", None)
        logger.warning(
            f"业务异常: {exc.code}",
            extra={"trace_id": trace_id, "code": exc.code, "detail": exc.detail},
        )
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "code": exc.code,        # 业务错误码（字符串，如 "PROJ_404_001"）
                "message": exc.message,
                "detail": exc.detail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "traceId": trace_id,
                "data": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Pydantic 参数校验失败 → 统一错误格式（422）"""
        trace_id = getattr(request.state, "trace_id", None)
        return JSONResponse(
            status_code=422,
            content={
                "code": "COMMON_422_001",
                "message": "请求参数校验失败",
                "detail": str(exc.errors()[:5]),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "traceId": trace_id,
                "data": None,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        """未预期异常 → 统一错误格式（500），不泄露内部细节"""
        trace_id = getattr(request.state, "trace_id", None)
        logger.error(
            f"未处理异常: {type(exc).__name__}",
            extra={"trace_id": trace_id},
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={
                "code": "COMMON_500_001",
                "message": "服务器内部错误",
                "detail": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "traceId": trace_id,
                "data": None,
            },
        )

    # 路由注册
    from app.controllers import (
        admin,
        auth,
        configs,
        creations,
        episodes,
        files,
        health,
        memberships,
        outputs,
        projects,
        step1,
        step2,
        step3,
        tasks,
        tts,
        users,
    )

    app.include_router(health.router, prefix="/api", tags=["System"])
    app.include_router(auth.router, prefix="/api", tags=["Auth"])
    app.include_router(users.router, prefix="/api", tags=["Users"])
    app.include_router(memberships.router, prefix="/api", tags=["Memberships"])
    app.include_router(projects.router, prefix="/api", tags=["Projects"])
    app.include_router(episodes.router, prefix="/api", tags=["Episodes"])
    app.include_router(creations.router, prefix="/api", tags=["Creations"])
    app.include_router(step1.router, prefix="/api", tags=["Step1"])
    app.include_router(step2.router, prefix="/api", tags=["Step2"])
    app.include_router(step3.router, prefix="/api", tags=["Step3"])
    app.include_router(tts.router, prefix="/api", tags=["TTS"])
    app.include_router(outputs.router, prefix="/api", tags=["Outputs"])
    app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
    app.include_router(files.router, prefix="/api", tags=["Files"])
    app.include_router(configs.router, prefix="/api", tags=["Configs"])
    app.include_router(admin.router, prefix="/api", tags=["Admin"])

    return app


app = create_app()
