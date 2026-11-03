"""
接口契约一致性测试（对照 docs/openapi.yaml）
===========================================
用 TestClient 跑真实请求，校验：
- 路径与契约一致
- 统一响应结构 {code, msg, data, traceId}
- 错误码与 HTTP 状态码语义
"""
from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import bindparam, text

from app.core.database import SessionLocal
from app.main import app

client = TestClient(app)

TS = int(time.time())
USERNAME = f"contract_{TS}"
PASSWORD = "test123456"


@pytest.fixture(scope="module", autouse=True)
def cleanup_test_users():
    """用例结束后清除本模块创建的账号，避免污染管理后台用户列表。"""
    yield
    with SessionLocal() as db:
        ids = [
            row[0]
            for row in db.execute(
                text(
                    "SELECT id FROM users "
                    "WHERE username LIKE 'contract_%' OR username LIKE 'other_%'"
                )
            )
        ]
        if not ids:
            return

        def run(sql: str, params: dict) -> None:
            db.execute(
                text(sql).bindparams(bindparam("ids", expanding=True)), params
            )

        creation_ids = [
            row[0]
            for row in db.execute(
                text(
                    "SELECT id FROM creations WHERE user_id IN :ids"
                ).bindparams(bindparam("ids", expanding=True)),
                {"ids": ids},
            )
        ]
        if creation_ids:
            for table in ("outputs", "generation_history", "step_results"):
                db.execute(
                    text(
                        f"DELETE FROM {table} WHERE creation_id IN :ids"
                    ).bindparams(bindparam("ids", expanding=True)),
                    {"ids": creation_ids},
                )
        for table in (
            "creations",
            "episodes",
            "projects",
            "tasks",
            "files",
            "memberships",
            "usage_records",
            "audit_logs",
        ):
            column = "admin_user_id" if table == "audit_logs" else "user_id"
            run(f"DELETE FROM {table} WHERE {column} IN :ids", {"ids": ids})
        run("DELETE FROM users WHERE id IN :ids", {"ids": ids})
        db.commit()


@pytest.fixture(scope="module")
def token() -> str:
    """注册并返回 token"""
    r = client.post(
        "/api/auth/register",
        json={"username": USERNAME, "password": PASSWORD},
    )
    assert r.status_code == 200, r.text
    return r.json()["data"]["token"]


@pytest.fixture(scope="module")
def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class TestResponseFormat:
    """统一响应格式（跨端协作约定 §2）"""

    def test_success_has_trace_id(self, headers):
        r = client.get("/api/users/me", headers=headers)
        body = r.json()
        assert r.status_code == 200
        assert body["code"] == 0
        assert body["msg"] == "success"
        assert body["traceId"]
        assert "data" in body

    def test_trace_id_echoes_request_header(self, headers):
        r = client.get("/api/users/me", headers={**headers, "X-Trace-Id": "my-trace-123"})
        assert r.json()["traceId"] == "my-trace-123"
        assert r.headers["X-Trace-Id"] == "my-trace-123"

    def test_error_format(self):
        r = client.get("/api/projects")
        body = r.json()
        assert r.status_code == 401
        assert set(body) >= {"code", "message", "detail", "timestamp", "traceId", "data"}
        assert body["code"] == "AUTH_401_001"
        assert body["data"] is None


class TestErrorCodes:
    """错误码与 HTTP 状态码语义"""

    def test_unauthorized_is_401(self):
        assert client.get("/api/projects").status_code == 401

    def test_bad_credentials_is_401(self):
        r = client.post("/api/auth/login", json={"username": USERNAME, "password": "wrong"})
        assert r.status_code == 401
        assert r.json()["code"] == "AUTH_401_005"

    def test_not_found_is_404(self, headers):
        r = client.get("/api/projects/p_nonexistent", headers=headers)
        assert r.status_code == 404
        assert r.json()["code"] == "PROJ_404_001"

    def test_validation_error_is_422(self, headers):
        r = client.post("/api/projects", headers=headers, json={"title": ""})
        assert r.status_code == 422
        assert r.json()["code"] == "COMMON_422_001"

    def test_forbidden_is_403(self, headers):
        """用另一个用户访问不属于自己的项目"""
        other = client.post(
            "/api/auth/register",
            json={"username": f"other_{TS}", "password": PASSWORD},
        ).json()["data"]["token"]
        pid = client.post(
            "/api/projects",
            headers=headers,
            json={"title": "项目A", "author": "作者", "intro": "这是一段足够长的项目简介内容"},
        ).json()["data"]["id"]

        r = client.get(f"/api/projects/{pid}", headers={"Authorization": f"Bearer {other}"})
        assert r.status_code == 403
        assert r.json()["code"] == "PROJ_403_001"


class TestStepEndpoints:
    """三步流程接口存在性与鉴权"""

    def test_step1_outline_requires_auth(self):
        assert client.post("/api/step1/outline", json={"creation_id": "x"}).status_code == 401

    def test_step2_generate_requires_auth(self):
        assert client.post("/api/step2/generate", json={"creation_id": "x"}).status_code == 401

    def test_step3_compose_requires_auth(self):
        assert client.post("/api/step3/compose", json={"creation_id": "x"}).status_code == 401

    def test_step1_load_requires_auth(self):
        assert client.get("/api/step1/load", params={"creation_id": "x"}).status_code == 401

    def test_step_result_step_no_range(self, headers):
        """step_no 只允许 1~3"""
        r = client.get(
            "/api/projects/p_x/creations/c_x/step-results/7", headers=headers
        )
        assert r.status_code in (403, 404, 422)

    def test_history_requires_auth(self):
        assert client.get("/api/projects/p_x/creations/c_x/history/1").status_code == 401

    def test_rollback_requires_auth(self):
        assert client.post("/api/projects/p_x/creations/c_x/rollback/1/1").status_code == 401

    def test_rollback_missing_creation(self, headers):
        r = client.post(
            "/api/projects/p_x/creations/c_nonexistent/rollback/1/1", headers=headers
        )
        assert r.status_code == 404
        assert r.json()["code"] == "CREAT_404_001"


class TestOutputs:
    """完成页接口"""

    def test_outputs_requires_auth(self):
        assert client.get("/api/creations/c_x/outputs").status_code == 401

    def test_output_file_requires_auth(self):
        assert client.get("/api/creations/c_x/outputs/o_x/file").status_code == 401

    def test_outputs_not_found_for_missing_creation(self, headers):
        r = client.get("/api/creations/c_nonexistent/outputs", headers=headers)
        assert r.status_code == 404
        assert r.json()["code"] == "CREAT_404_001"

    def test_output_file_not_found_for_missing_creation(self, headers):
        r = client.get("/api/creations/c_nonexistent/outputs/o_x/file", headers=headers)
        assert r.status_code == 404
        assert r.json()["code"] == "CREAT_404_001"


class TestProjectVideoBinding:
    """上传本地视频并绑定为项目视频源"""

    @staticmethod
    def _fixture_video():
        import pathlib

        return (
            pathlib.Path(__file__).resolve().parents[1]
            / "fixtures"
            / "media"
            / "videos"
            / "ep001.mp4"
        )

    def test_bind_uploaded_video_and_unbind(self, headers):
        video = self._fixture_video()
        assert video.is_file(), f"缺少测试素材: {video}"

        with video.open("rb") as f:
            upload = client.post(
                "/api/files/upload",
                headers=headers,
                files={"file": (video.name, f, "video/mp4")},
                data={"sub_dir": "video"},
            )
        assert upload.status_code == 200, upload.text
        file_id = upload.json()["data"]["id"]
        assert file_id

        created = client.post(
            "/api/projects",
            headers=headers,
            json={
                "title": "视频绑定测试",
                "author": "测试",
                "intro": "这是一段足够长的项目简介内容",
                "video_file_ids": [file_id],
            },
        )
        assert created.status_code == 200, created.text
        project_id = created.json()["data"]["id"]

        detail = client.get(f"/api/projects/{project_id}", headers=headers).json()["data"]
        assert detail["video_dir"], "上传视频后应自动写入 video_dir"

        updated = client.put(
            f"/api/projects/{project_id}",
            headers=headers,
            json={"video_file_ids": []},
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["data"]["video_dir"] is None

        # 清理
        client.delete(f"/api/projects/{project_id}", headers=headers)
        client.delete(f"/api/files/{file_id}", headers=headers)


class TestTasks:
    """任务接口"""

    def test_task_not_found(self, headers):
        r = client.get("/api/tasks/t_nonexistent", headers=headers)
        assert r.status_code == 404
        assert r.json()["code"] == "TASK_404_001"

    def test_retry_not_found(self, headers):
        r = client.post("/api/tasks/t_nonexistent/retry", headers=headers)
        assert r.status_code == 404
        assert r.json()["code"] == "TASK_404_001"

    def test_retry_requires_auth(self):
        assert client.post("/api/tasks/t_nonexistent/retry").status_code == 401

    def test_task_list_pagination(self, headers):
        # 契约字段为 pageSize（docs/00-跨端协作约定.md §10）
        r = client.get("/api/tasks", headers=headers, params={"page": 1, "pageSize": 10})
        body = r.json()
        assert body["code"] == 0
        assert body["data"]["page"] == 1
        assert body["data"]["pageSize"] == 10
        assert isinstance(body["data"]["items"], list)

    def test_task_list_pagination_legacy_param(self, headers):
        # 旧参数 page_size 仍兼容（不进 OpenAPI 文档）
        r = client.get("/api/tasks", headers=headers, params={"page": 1, "page_size": 5})
        body = r.json()
        assert body["code"] == 0
        assert body["data"]["pageSize"] == 5


class TestConfigs:
    """配置接口（用户级 + 管理员全局）"""

    def test_configs_require_auth(self):
        assert client.get("/api/configs").status_code == 401

    def test_user_config_crud(self, headers):
        key = f"test_cfg_{TS}"
        put = client.put(
            f"/api/configs/{key}",
            headers=headers,
            json={"key": key, "value": {"foo": "bar"}, "description": "测试配置"},
        )
        assert put.status_code == 200, put.text
        assert put.json()["data"]["user_id"]

        listed = client.get("/api/configs", headers=headers).json()["data"]
        assert any(c["key"] == key for c in listed)

        got = client.get(f"/api/configs/{key}", headers=headers).json()["data"]
        assert got["value"] == {"foo": "bar"}

        deleted = client.delete(f"/api/configs/{key}", headers=headers)
        assert deleted.status_code == 200

        missing = client.get(f"/api/configs/{key}", headers=headers)
        assert missing.status_code == 404
        assert missing.json()["code"] == "CONF_404_001"

    def test_admin_configs_forbidden_for_normal_user(self, headers):
        r = client.get("/api/admin/configs", headers=headers)
        assert r.status_code == 403

    def test_connection_requires_auth(self):
        assert client.post("/api/configs/test", json={"provider": "minimax"}).status_code == 401


class TestOpenApiContract:
    """契约与运行时一致性"""

    @staticmethod
    def _contract_path() -> str:
        """定位仓库根的 docs/openapi.yaml"""
        import pathlib

        root = pathlib.Path(__file__).resolve().parents[3]
        return str(root / "docs" / "openapi.yaml")

    def test_runtime_paths_match_contract(self):
        """运行时暴露的路径应存在于 docs/openapi.yaml"""
        import yaml

        with open(self._contract_path(), encoding="utf-8") as f:
            contract = yaml.safe_load(f)

        contract_paths = set(contract["paths"].keys())
        runtime_paths = set(app.openapi()["paths"].keys())

        # 运行时的路径必须在契约中定义
        missing = runtime_paths - contract_paths
        assert not missing, f"运行时存在契约未定义的路径: {sorted(missing)}"

    def test_contract_has_three_step_tags(self):
        import yaml

        with open(self._contract_path(), encoding="utf-8") as f:
            contract = yaml.safe_load(f)

        tag_names = [t["name"] for t in contract["tags"]]
        assert "Step1" in tag_names
        assert "Step2" in tag_names
        assert "Step3" in tag_names
        assert "Outputs" in tag_names
        assert "Step4" not in tag_names
        assert "Step5" not in tag_names
        assert "Step6" not in tag_names
        assert "Step7" not in tag_names
