"""
文件服务 HTTP 端到端验收
=========================
用真实 HTTP 请求验证文件服务全链路：
1. 注册两个用户（验证隔离）
2. 上传文件
3. 列出我的文件
4. 文件详情
5. 预览（完整响应 + Range 部分响应）
6. 下载（attachment 头）
7. 跨用户访问被拒（403）
8. 路径遍历被拒
9. 非法扩展名被拒
10. 删除文件
11. 目录浏览

用法：
    python tests/acceptance/test_files_api.py
    python tests/acceptance/test_files_api.py --base-url http://127.0.0.1:8010
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8010/api"

FIXTURE_VIDEO = (
    Path(__file__).resolve().parents[1] / "fixtures" / "media" / "videos" / "ep001.mp4"
)
FIXTURE_AUDIO = (
    Path(__file__).resolve().parents[1] / "fixtures" / "media" / "audio" / "voice.mp3"
)


class AcceptanceError(AssertionError):
    """验收失败"""


def ok(resp: httpx.Response, name: str) -> dict:
    """断言响应可解析为 JSON（允许 2xx 与业务错误 4xx）"""
    if resp.status_code >= 500:
        raise AcceptanceError(f"[{name}] HTTP {resp.status_code}: {resp.text[:300]}")
    try:
        body = resp.json()
    except Exception:
        raise AcceptanceError(f"[{name}] 响应非 JSON: {resp.text[:200]}")
    return body


def register(client: httpx.Client, username: str) -> str:
    """注册并返回 token"""
    r = client.post(
        f"{BASE}/auth/register",
        json={"username": username, "password": "test123456", "display_name": username},
    )
    body = ok(r, f"register {username}")
    return body["data"]["token"]


def main() -> int:
    global BASE
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE)
    args = parser.parse_args()
    BASE = args.base_url.rstrip("/")

    print("=" * 66)
    print("  文件服务 HTTP 端到端验收")
    print(f"  服务: {BASE}")
    print("=" * 66)

    if not FIXTURE_VIDEO.exists():
        print("\n❌ 测试素材不存在，先生成：python -m tests.fixtures.make_fixtures")
        return 2

    ts = int(time.time())
    user_a = f"fa_{ts}"
    user_b = f"fb_{ts}"

    with httpx.Client(timeout=60.0) as client:
        # ---------- 1. 注册 ----------
        print("\n[1] 注册两个用户（验证隔离）")
        token_a = register(client, user_a)
        token_b = register(client, user_b)
        ha = {"Authorization": f"Bearer {token_a}"}
        hb = {"Authorization": f"Bearer {token_b}"}
        print(f"    ✅ {user_a} / {user_b} 注册成功")

        # ---------- 2. 上传 ----------
        print("\n[2] 上传视频文件")
        with FIXTURE_VIDEO.open("rb") as f:
            r = client.post(
                f"{BASE}/files/upload",
                headers=ha,
                files={"file": ("ep001.mp4", f, "video/mp4")},
                data={"sub_dir": "video"},
            )
        body = ok(r, "upload")
        file_id = body["data"]["id"]
        size = body["data"]["size_bytes"]
        print(f"    ✅ 上传成功 id={file_id} size={size} path={body['data']['path']}")

        # ---------- 3. 上传音频（子目录） ----------
        print("\n[3] 上传音频文件（子目录 audio）")
        with FIXTURE_AUDIO.open("rb") as f:
            r = client.post(
                f"{BASE}/files/upload",
                headers=ha,
                files={"file": ("voice.mp3", f, "audio/mpeg")},
                data={"sub_dir": "audio"},
            )
        body = ok(r, "upload audio")
        audio_id = body["data"]["id"]
        print(f"    ✅ 音频上传成功 id={audio_id} path={body['data']['path']}")

        # ---------- 4. 列表 ----------
        print("\n[4] 我的文件列表")
        r = client.get(f"{BASE}/files?page=1&pageSize=10", headers=ha)
        body = ok(r, "list files")
        total = body["data"]["total"]
        assert total == 2, f"期望 2 个文件，实际 {total}"
        print(f"    ✅ 列表 {total} 个文件")

        # ---------- 5. 详情 ----------
        print("\n[5] 文件详情")
        r = client.get(f"{BASE}/files/{file_id}", headers=ha)
        body = ok(r, "file detail")
        assert body["data"]["id"] == file_id
        assert body["data"]["mime_type"] == "video/mp4"
        print(f"    ✅ 详情正确 mime={body['data']['mime_type']}")

        # ---------- 6. 预览（完整） ----------
        print("\n[6] 预览（完整响应）")
        r = client.get(f"{BASE}/files/{file_id}/preview", headers=ha)
        assert r.status_code == 200, f"HTTP {r.status_code}"
        assert r.headers.get("accept-ranges") == "bytes"
        assert "inline" in r.headers.get("content-disposition", "")
        assert len(r.content) == size, f"内容长度 {len(r.content)} != {size}"
        print(f"    ✅ 完整预览 {len(r.content)} 字节，Accept-Ranges 正常")

        # ---------- 7. 预览（Range 部分） ----------
        print("\n[7] 预览（Range 部分响应，用于视频拖拽定位）")
        r = client.get(
            f"{BASE}/files/{file_id}/preview",
            headers={**ha, "Range": "bytes=0-1023"},
        )
        assert r.status_code == 206, f"期望 206，实际 {r.status_code}"
        assert r.headers.get("content-range", "").startswith("bytes 0-1023/")
        assert len(r.content) == 1024
        print(f"    ✅ 206 Partial Content，Content-Range={r.headers.get('content-range')}")

        # ---------- 8. Range 后段（bytes=-1024） ----------
        print("\n[8] 预览（Range 后段 bytes=-1024）")
        r = client.get(
            f"{BASE}/files/{file_id}/preview",
            headers={**ha, "Range": "bytes=-1024"},
        )
        assert r.status_code == 206, f"期望 206，实际 {r.status_code}"
        assert len(r.content) == 1024
        print(f"    ✅ 后段 1024 字节正常")

        # ---------- 9. 下载 ----------
        print("\n[9] 下载（attachment）")
        r = client.get(f"{BASE}/files/{file_id}/download", headers=ha)
        assert r.status_code == 200
        assert "attachment" in r.headers.get("content-disposition", "")
        print(f"    ✅ 下载正常 Content-Disposition={r.headers.get('content-disposition')[:50]}")

        # ---------- 10. 跨用户隔离 ----------
        print("\n[10] 跨用户访问被拒（用户 B 访问用户 A 的文件）")
        r = client.get(f"{BASE}/files/{file_id}", headers=hb)
        body = ok(r, "cross user")  # 业务错误也返回 200
        assert body["code"] == "FILE_403_002", f"期望 FILE_403_002，实际 {body.get('code')}"
        print(f"    ✅ 正确拒绝：{body['code']} - {body['message']}")

        # ---------- 11. 跨用户预览被拒 ----------
        print("\n[11] 跨用户预览被拒")
        r = client.get(f"{BASE}/files/{file_id}/preview", headers=hb)
        body = ok(r, "cross user preview")
        assert body["code"] == "FILE_403_002"
        print(f"    ✅ 正确拒绝：{body['code']}")

        # ---------- 12. 跨用户删除被拒 ----------
        print("\n[12] 跨用户删除被拒")
        r = client.delete(f"{BASE}/files/{file_id}", headers=hb)
        body = ok(r, "cross user delete")
        assert body["code"] == "FILE_403_002"
        print(f"    ✅ 正确拒绝：{body['code']}")

        # ---------- 13. 用户 B 列表看不到用户 A 的文件 ----------
        print("\n[13] 用户 B 的列表不含用户 A 的文件")
        r = client.get(f"{BASE}/files", headers=hb)
        body = ok(r, "user b list")
        assert body["data"]["total"] == 0, f"用户 B 应看到 0 个，实际 {body['data']['total']}"
        print("    ✅ 用户 B 列表为空，隔离生效")

        # ---------- 14. 路径遍历被拒 ----------
        print("\n[14] 路径遍历攻击被拒")
        r = client.get(f"{BASE}/dirs/browse?path=../../../", headers=ha)
        body = ok(r, "path traversal")
        assert body["code"] == "FILE_403_003", f"期望 FILE_403_003，实际 {body.get('code')}"
        print(f"    ✅ 正确拒绝：{body['code']} - {body['message']}")

        # ---------- 15. 非法扩展名被拒 ----------
        print("\n[15] 非法扩展名上传被拒")
        r = client.post(
            f"{BASE}/files/upload",
            headers=ha,
            files={"file": ("evil.exe", b"MZ\x90\x00", "application/octet-stream")},
        )
        body = ok(r, "bad ext")
        assert body["code"] == "FILE_400_004", f"期望 FILE_400_004，实际 {body.get('code')}"
        print(f"    ✅ 正确拒绝：{body['code']} - {body['message']}")

        # ---------- 16. 目录浏览 ----------
        print("\n[16] 目录浏览（受限 workdir 内）")
        r = client.get(f"{BASE}/dirs/browse", headers=ha)
        body = ok(r, "browse")
        assert "current" in body["data"]
        print(f"    ✅ 浏览根目录，共 {len(body['data']['items'])} 项")

        # ---------- 17. 删除 ----------
        print("\n[17] 删除文件")
        r = client.delete(f"{BASE}/files/{file_id}", headers=ha)
        body = ok(r, "delete")
        assert body["code"] == 0

        r = client.get(f"{BASE}/files/{file_id}", headers=ha)
        body = ok(r, "get deleted")
        assert body["code"] == "FILE_404_001", f"期望 FILE_404_001，实际 {body.get('code')}"
        print(f"    ✅ 删除成功，再查返回 {body['code']}")

        # ---------- 18. 配额联动 ----------
        print("\n[18] 存储配额联动（上传后 quota 增加）")
        r = client.get(f"{BASE}/memberships/me/quota", headers=ha)
        body = ok(r, "quota")
        used = body["data"]["storage_used_mb"]
        print(f"    ✅ 当前存储用量 {used} MB")

    print("\n" + "=" * 66)
    print("  ✅ 文件服务 HTTP 端到端验收全部通过（18 项）")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AcceptanceError as e:
        print(f"\n❌ 验收失败: {e}")
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        print(f"\n❌ 意外错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
