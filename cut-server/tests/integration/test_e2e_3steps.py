"""
端到端验证脚本（3 步流程）
=========================
用法：先启动服务，再执行本脚本。

流程：注册 → 创建项目 → 创建剧集 → 创建创作
     → Step1 生成大纲 → Step1 保存
     → Step2 生成口播长文 → Step2 保存（TTS 异步）
     → Step3 素材列表 → Step3 随机标记 → 创作详情 → 完成页

依赖真实 AI（MiniMax）与 ffmpeg，无 Key 时相关步骤会失败并跳过断言。
"""
from __future__ import annotations

import json
import sys
import time

import httpx

BASE = "http://127.0.0.1:8010/api"

TS = int(time.time())
USERNAME = f"e2e_{TS}"
PASSWORD = "test123456"

# 测试用视频目录（需含 mp4 文件）
VIDEO_DIR = sys.argv[1] if len(sys.argv) > 1 else ""

_failures: list[str] = []
client = httpx.Client(timeout=240)


def check(condition: bool, name: str, detail: str = "") -> bool:
    """记录断言结果"""
    if condition:
        print(f"  [PASS] {name}")
        return True
    print(f"  [FAIL] {name} {detail}")
    _failures.append(name)
    return False


def step(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> int:
    step("1. 注册")
    r = client.post(
        f"{BASE}/auth/register",
        json={"username": USERNAME, "password": PASSWORD, "display_name": "E2E"},
    )
    body = r.json()
    check(r.status_code == 200, "注册 HTTP 200", f"got {r.status_code}")
    check(body.get("code") == 0, "注册 code=0", str(body)[:200])
    check(bool(body.get("traceId")), "traceId 已回填 body", str(body.get("traceId")))
    token = body["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    step("2. 健康检查")
    r = client.get(f"{BASE}/health")
    h = r.json()
    check(h["data"]["postgres_available"], "PostgreSQL 可用")
    check(h["data"]["ffmpeg_available"], "ffmpeg 可用")

    step("3. 创建项目")
    r = client.post(
        f"{BASE}/projects",
        headers=headers,
        json={
            "title": "斗破苍穹",
            "author": "天蚕土豆",
            "intro": "少年萧炎从废柴到斗帝的逆袭之路",
            "video_dir": VIDEO_DIR or None,
            "intro_dir": None,
        },
    )
    body = r.json()
    check(body.get("code") == 0, "创建项目", str(body)[:200])
    project_id = body["data"]["id"]

    step("4. 创建剧集")
    r = client.post(
        f"{BASE}/projects/{project_id}/episodes",
        headers=headers,
        json={"title": "第一集 陨落的天才", "description": "萧炎少年时期，测定无属性"},
    )
    body = r.json()
    check(body.get("code") == 0, "创建剧集", str(body)[:200])
    episode_id = body["data"]["id"]

    step("5. 创建创作")
    r = client.post(
        f"{BASE}/projects/{project_id}/creations",
        headers=headers,
        json={"episode_id": episode_id, "title": "萧炎逆袭路"},
    )
    body = r.json()
    check(body.get("code") == 0, "创建创作", str(body)[:200])
    creation_id = body["data"]["id"]

    step("6. Step1 生成大纲（调用 MiniMax）")
    r = client.post(
        f"{BASE}/step1/outline",
        headers=headers,
        json={
            "creation_id": creation_id,
            "form": {
                "title": "斗破苍穹",
                "author": "天蚕土豆",
                "intro": "少年萧炎从废柴到斗帝的逆袭之路",
                "style": "热血安利",
                "target_duration": 70,
                "episode_ids": [episode_id],
                "goals": ["intro_episode"],
            },
        },
    )
    body = r.json()
    check(body.get("code") == 0, "Step1 大纲生成", str(body)[:300])
    outline = {}
    if body.get("code") == 0:
        outline = body["data"]["outline"]
        check(len(outline.get("core_keywords", [])) > 0, "大纲含 core_keywords")
        check(len(outline.get("ref_titles", [])) > 0, "大纲含 ref_titles")
        check(bool(outline.get("main_task")), "大纲含 main_task")
        print("     预览:", json.dumps(outline, ensure_ascii=False)[:300])

        step("7. Step1 保存")
        r = client.post(
            f"{BASE}/step1/save",
            headers=headers,
            json={
                "creation_id": creation_id,
                "form": {
                    "title": "斗破苍穹",
                    "author": "天蚕土豆",
                    "intro": "少年萧炎从废柴到斗帝的逆袭之路",
                    "style": "热血安利",
                    "target_duration": 70,
                    "episode_ids": [episode_id],
                    "goals": ["intro_episode"],
                },
                "outline": outline,
            },
        )
        body = r.json()
        check(body.get("code") == 0, "Step1 保存", str(body)[:200])
        check(body["data"]["current_step"] == 2, "current_step 推进到 2", str(body["data"]))

    step("8. Step2 生成口播长文")
    r = client.post(
        f"{BASE}/step2/generate",
        headers=headers,
        json={"creation_id": creation_id},
    )
    body = r.json()
    check(body.get("code") == 0, "Step2 长文生成", str(body)[:300])
    if body.get("code") == 0:
        article = body["data"]
        check(article["word_count"] > 50, "长文字数 > 50", str(article["word_count"]))
        check(len(article["content"]) > 100, "长文正文长度足够")
        print("     预览:", article["content"][:200].replace("\n", " / "))

        step("9. Step2 保存（触发异步 TTS）")
        r = client.post(
            f"{BASE}/step2/save",
            headers=headers,
            json={
                "creation_id": creation_id,
                "title": article["title"],
                "content": article["content"],
                "word_count": article["word_count"],
                "skip_tts": False,
            },
        )
        body = r.json()
        check(body.get("code") == 0, "Step2 保存", str(body)[:200])
        tts_task_id = body["data"].get("tts_task_id")
        check(bool(tts_task_id), "返回 tts_task_id")

        if tts_task_id:
            step("10. 轮询 TTS 任务")
            final = None
            for _ in range(45):
                time.sleep(2)
                r = client.get(f"{BASE}/tasks/{tts_task_id}", headers=headers)
                task = r.json()["data"]
                print(f"     状态={task['status']} 进度={task['progress']}%")
                if task["status"] in ("completed", "failed"):
                    final = task
                    break
            check(
                final is not None and final["status"] == "completed",
                "TTS 任务完成",
                final["error"] if final else "timeout",
            )
            if final and final["status"] == "completed":
                print("     结果:", json.dumps(final.get("result"), ensure_ascii=False)[:300])

    step("11. Step3 素材列表")
    r = client.get(f"{BASE}/step3/media-list", headers=headers, params={"creation_id": creation_id})
    body = r.json()
    check(body.get("code") == 0, "Step3 素材列表", str(body)[:200])
    media = body.get("data", {})
    print(
        f"     系统音频={len(media.get('system_audios', []))} "
        f"自定义音频={len(media.get('custom_audios', []))} "
        f"视频={len(media.get('video_files', []))}"
    )

    step("12. Step3 随机标记")
    r = client.post(
        f"{BASE}/step3/remark",
        headers=headers,
        json={"creation_id": creation_id, "video_files": [], "target_duration": 30},
    )
    body = r.json()
    check(body.get("code") == 0, "Step3 标记", str(body)[:300])
    if body.get("code") == 0:
        marks = body["data"]["markers"]
        check(len(marks) > 0, "生成了标记", str(len(marks)))
        check(body["data"]["total_duration"] > 0, "标记总时长 > 0")
        print(f"     标记数={len(marks)} 总时长={body['data']['total_duration']}s")

    step("13. 创作详情（含各 Step 结果）")
    r = client.get(
        f"{BASE}/projects/{project_id}/creations/{creation_id}",
        headers=headers,
    )
    body = r.json()
    check(body.get("code") == 0, "创作详情", str(body)[:200])
    step_results = body["data"].get("step_results", {})
    check(isinstance(step_results, dict), "step_results 是对象（按 step_no 索引）")
    print(f"     已完成的步骤: {sorted(step_results.keys())}")

    step("14. 完成页 outputs")
    r = client.get(f"{BASE}/creations/{creation_id}/outputs", headers=headers)
    body = r.json()
    check(body.get("code") == 0, "完成页查询", str(body)[:200])
    check(isinstance(body.get("data"), list), "outputs 是数组")

    step("15. 错误路径：无 Token")
    r = client.get(f"{BASE}/projects")
    check(r.status_code == 401, "无 Token 返回 HTTP 401", f"got {r.status_code}")
    check(r.json().get("code") == "AUTH_401_001", "错误码 AUTH_401_001", str(r.json())[:120])

    step("16. 错误路径：错误密码")
    r = client.post(f"{BASE}/auth/login", json={"username": USERNAME, "password": "wrongpassword"})
    check(r.status_code == 401, "错误密码 HTTP 401", f"got {r.status_code}")
    check(r.json().get("code") == "AUTH_401_005", "错误码 AUTH_401_005", str(r.json())[:120])

    step("17. 错误路径：不存在的项目")
    r = client.get(f"{BASE}/projects/p_notexist", headers=headers)
    check(r.status_code == 404, "不存在项目 HTTP 404", f"got {r.status_code}")
    check(r.json().get("code") == "PROJ_404_001", "错误码 PROJ_404_001", str(r.json())[:120])

    print("\n" + "=" * 60)
    if _failures:
        print(f"失败 {len(_failures)} 项：")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("全部通过 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
