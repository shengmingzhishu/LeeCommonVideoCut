"""
异步任务队列
============
基于 asyncio + 内存 worker 的轻量任务系统：
- 提交任务立即返回 task_id（符合"耗时 >3 秒必须异步化"约束）
- 任务状态持久化到 tasks 表（重启后可查历史）
- 支持进度回调、取消、失败原因记录
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

from app.core.database import session_scope
from app.core.logger import get_logger
from app.models.task import Task
from app.utils.safe_path import gen_id

logger = get_logger()

# 任务类型
TYPE_TTS = "tts"
TYPE_COMPOSE = "compose"

# 任务状态
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"


class TaskQueue:
    """单进程任务调度器"""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._workers: list[asyncio.Task] = []
        self._handlers: dict[str, Callable[[TaskContext], Awaitable[dict[str, Any]]]] = {}
        self._cancelled: set[str] = set()
        self._started = False

    def register(
        self,
        task_type: str,
        handler: Callable[[TaskContext], Awaitable[dict[str, Any]]],
    ) -> None:
        """注册任务类型的处理器"""
        self._handlers[task_type] = handler

    async def start(self, worker_count: int = 2) -> None:
        """启动 worker（应用启动时调用）"""
        if self._started:
            return
        self._started = True
        for i in range(worker_count):
            self._workers.append(asyncio.create_task(self._worker_loop(f"worker-{i}")))

        logger.info("任务队列已启动", extra={"worker_count": worker_count})

    async def stop(self) -> None:
        """停止 worker（应用关闭时调用）"""
        self._started = False
        for w in self._workers:
            w.cancel()
        self._workers.clear()

    def submit(self, *, task_type: str, user_id: str, payload: dict[str, Any]) -> str:
        """提交任务，返回 task_id

        Args:
            task_type: 任务类型（需先 register）
            user_id: 提交者
            payload: 任务参数

        Returns:
            task_id

        Raises:
            ValueError: 任务类型未注册
        """
        if task_type not in self._handlers:
            raise ValueError(f"未注册的任务类型: {task_type}")

        task_id = gen_id("t")
        with session_scope() as db:
            db.add(
                Task(
                    id=task_id,
                    user_id=user_id,
                    type=task_type,
                    status=STATUS_PENDING,
                    progress=0,
                    payload=payload,
                )
            )

        self._queue.put_nowait(task_id)
        logger.info(
            "任务已提交",
            extra={"task_id": task_id, "task_type": task_type, "user_id": user_id},
        )
        return task_id

    def cancel(self, task_id: str) -> bool:
        """标记任务取消（worker 执行到检查点时退出）"""
        self._cancelled.add(task_id)
        with session_scope() as db:
            task = db.get(Task, task_id)
            if task and task.status in (STATUS_PENDING, STATUS_RUNNING):
                task.status = STATUS_CANCELLED
                task.finished_at = datetime.now(timezone.utc)
        return True

    def is_cancelled(self, task_id: str) -> bool:
        """任务是否已被取消"""
        return task_id in self._cancelled

    async def _worker_loop(self, name: str) -> None:
        """worker 主循环"""
        while self._started:
            try:
                task_id = await self._queue.get()
            except asyncio.CancelledError:
                break

            try:
                await self._execute(task_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"任务执行异常: {type(e).__name__}",
                    extra={"task_id": task_id, "worker": name},
                    exc_info=e,
                )
            finally:
                self._queue.task_done()

    async def _execute(self, task_id: str) -> None:
        """执行单个任务"""
        with session_scope() as db:
            task = db.get(Task, task_id)
            if not task:
                return
            if task.status == STATUS_CANCELLED:
                return
            task.status = STATUS_RUNNING
            task_type = task.type

        handler = self._handlers[task_type]
        ctx = TaskContext(task_id=task_id, queue=self)

        try:
            result = await handler(ctx)
        except Exception as e:
            logger.error(
                f"任务失败: {type(e).__name__}",
                extra={"task_id": task_id, "task_type": task_type},
                exc_info=e,
            )
            with session_scope() as db:
                task = db.get(Task, task_id)
                if task:
                    task.status = STATUS_FAILED
                    task.error = f"{type(e).__name__}: {e}"[:500]
            return

        with session_scope() as db:
            task = db.get(Task, task_id)
            if task:
                task.status = STATUS_COMPLETED
                task.progress = 100
                task.result = result


class TaskContext:
    """任务执行上下文（供 handler 更新进度）"""

    def __init__(self, task_id: str, queue: TaskQueue):
        self.task_id = task_id
        self._queue = queue

    def update_progress(self, progress: int, *, result: dict[str, Any] | None = None) -> None:
        """更新任务进度

        Args:
            progress: 0~100
            result: 阶段性结果（可选，会写入 tasks.result）
        """
        with session_scope() as db:
            task = db.get(Task, self.task_id)
            if task:
                task.progress = max(0, min(100, progress))
                if result is not None:
                    task.result = result

    def is_cancelled(self) -> bool:
        """是否已被取消"""
        return self._queue.is_cancelled(self.task_id)

    def get_payload(self) -> dict[str, Any]:
        """读取任务参数"""
        with session_scope() as db:
            task = db.get(Task, self.task_id)
            return (task.payload or {}) if task else {}


# 全局单例
task_queue = TaskQueue()
