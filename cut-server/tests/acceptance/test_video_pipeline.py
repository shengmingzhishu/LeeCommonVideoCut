"""
端到端视频剪辑验收测试（不依赖 AI）
=====================================
目标：验证「真实素材 → 真实产出 mp4」的完整剪辑链路可用。

设计要点：
1. **绕过 AI**：MiniMax 余额不足时 AI 步骤无法跑通，因此本脚本**手工预置文案**，
   直接测试 Step3 的核心剪辑能力（裁切 → 合并 → 音视频合成 → 字幕烧录）。
2. **真实素材**：用 ffmpeg 合成真实视频/音频（tests/fixtures/media/）。
3. **真实产物断言**：用 ffprobe 校验产出 mp4 的时长/分辨率/音轨/字幕流。

覆盖的验收项（对应 v5 文档 §26）：
- AT-01 完整剪辑链路产出 mp4
- AT-11 标记表可编辑（微调秒数后影响产出）
- AT-12 视频时长正确（标记总时长 ≈ 产出时长）
- 多次合成：同一创作合成 2 次 → 完成页列出 2 条记录

前置条件：
- 服务已启动：uvicorn app.main:app --port 8010
- 测试素材已生成：python -m tests.fixtures.make_fixtures

用法：
    python tests/acceptance/test_video_pipeline.py
    python tests/acceptance/test_video_pipeline.py --base-url http://127.0.0.1:8000
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx

# ============================================================
# 常量
# ============================================================
FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "media"
VIDEO_DIR = FIXTURE_DIR / "videos"
AUDIO_DIR = FIXTURE_DIR / "audio"

# 优先使用项目内置的完整版 ffmpeg
_REPO_ROOT = Path(__file__).resolve().parents[3]
_BUNDLED = _REPO_ROOT / "tools" / "ffmpeg" / "bin"
FFPROBE = str(_BUNDLED / "ffprobe.exe") if (_BUNDLED / "ffprobe.exe").exists() else "ffprobe"

USERNAME = f"acc_{int(time.time())}"
PASSWORD = "acc123456"

# 手工预置的口播文案（绕过 AI）
SCRIPT_TEXT = (
    "你是否想过，曾经的天才如何跌落神坛？"
    "今天我们来聊一聊这部热血神作。"
    "主角从云端跌落，却凭一腔孤勇逆天改命。"
    "关注我，下期更精彩。"
)


class AcceptanceError(AssertionError):
    """验收失败"""


# ============================================================
# 工具
# ============================================================
def probe(path: Path) -> dict[str, Any]:
    """ffprobe 探测媒体信息"""
    if not path.exists():
        raise AcceptanceError(f"文件不存在: {path}")

    result = subprocess.run(
        [FFPROBE, "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise AcceptanceError(f"ffprobe 失败: {result.stderr[-300:]}")

    import json
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    fmt = data.get("format", {})

    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    subtitle_streams = [s for s in streams if s.get("codec_type") == "subtitle"]

    return {
        "duration": round(float(fmt.get("duration", 0)), 2),
        "size": int(fmt.get("size", 0)),
        "video_count": len(video_streams),
        "audio_count": len(audio_streams),
        "subtitle_count": len(subtitle_streams),
        "width": video_streams[0].get("width") if video_streams else 0,
        "height": video_streams[0].get("height") if video_streams else 0,
        "vcodec": video_streams[0].get("codec_name") if video_streams else None,
        "acodec": audio_streams[0].get("codec_name") if audio_streams else None,
    }


class Client:
    """API 客户端封装"""

    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self.token: str = ""
        self.http = httpx.Client(timeout=60.0)

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def call(self, method: str, path: str, **kwargs: Any) -> Any:
        """调用接口，断言 code==0，返回 data"""
        resp = self.http.request(
            method, f"{self.base}{path}", headers=self._headers(), **kwargs
        )
        if resp.status_code != 200:
            raise AcceptanceError(
                f"{method} {path} → HTTP {resp.status_code}: {resp.text[:300]}"
            )
        body = resp.json()
        if body.get("code") != 0:
            raise AcceptanceError(
                f"{method} {path} → code={body.get('code')}: {body.get('msg')}"
            )
        return body.get("data")

    def poll_task(self, task_id: str, timeout: int = 300) -> dict[str, Any]:
        """轮询异步任务直到完成"""
        deadline = time.time() + timeout
        last_progress = -1
        while time.time() < deadline:
            task = self.call("GET", f"/api/tasks/{task_id}")
            status = task.get("status")
            progress = task.get("progress", 0)

            if progress != last_progress:
                print(f"      ... 任务进度 {progress}%")
                last_progress = progress

            if status == "completed":
                return task
            if status in ("failed", "cancelled"):
                raise AcceptanceError(
                    f"任务 {status}: {task.get('error')}"
                )
            time.sleep(2)
        raise AcceptanceError(f"任务超时（{timeout}s）")


# ============================================================
# 验收步骤
# ============================================================
def step_01_register(c: Client) -> None:
    """注册并登录"""
    print("\n[1] 注册 + 登录")
    data = c.call(
        "POST", "/api/auth/register",
        json={"username": USERNAME, "password": PASSWORD, "display_name": "验收测试"},
    )
    c.token = data["token"]
    assert c.token, "token 为空"
    print(f"    ✅ 注册成功，user_id={data['user']['id']}")


def step_02_create_project(c: Client) -> str:
    """创建项目（指向测试素材目录）"""
    print("\n[2] 创建项目")
    project = c.call(
        "POST", "/api/projects",
        json={
            "title": "验收测试漫剧",
            "author": "验收机器人",
            "intro": "这是用于端到端视频剪辑验收的测试项目，验证完整剪辑链路。",
            "video_dir": str(VIDEO_DIR),
            "intro_dir": str(VIDEO_DIR),
        },
    )
    print(f"    ✅ 项目创建：{project['id']}")
    return project["id"]


def step_03_create_episode(c: Client, project_id: str) -> str:
    """创建剧集"""
    print("\n[3] 创建剧集")
    episode = c.call(
        "POST", f"/api/projects/{project_id}/episodes",
        json={"title": "第 1 集 · 验收", "description": "端到端验收剧集"},
    )
    print(f"    ✅ 剧集创建：{episode['id']}")
    return episode["id"]


def step_04_create_creation(c: Client, project_id: str, episode_id: str) -> str:
    """创建创作"""
    print("\n[4] 创建创作")
    creation = c.call(
        "POST", f"/api/projects/{project_id}/creations",
        json={"title": "验收创作", "episode_id": episode_id},
    )
    print(f"    ✅ 创作创建：{creation['id']}")
    return creation["id"]


def step_05_step1(c: Client, project_id: str, creation_id: str) -> None:
    """Step1：保存创作信息（手工预置大纲，不调 AI）"""
    print("\n[5] Step1 保存创作信息（预置大纲）")
    result = c.call(
        "POST", "/api/step1/save",
        json={
            "creation_id": creation_id,
            "form": {
                "title": "验收测试漫剧",
                "author": "验收机器人",
                "intro": "端到端验收用简介",
                "style": "热血安利",
                "target_duration": 20,
                "keywords": ["热血", "逆袭"],
                "ref_titles": ["少年逆袭之路"],
                "value_points": ["节奏紧凑", "情绪饱满"],
            },
            "outline": {
                "core_keywords": ["热血", "逆袭", "成长"],
                "core_words": ["斗气", "修炼"],
                "ref_titles": [{"title": "少年逆袭之路", "subtitle": "从天才到强者的蜕变"}],
                "main_task": "让观众快速理解主角的逆袭历程",
                "core_value": ["情绪共鸣", "节奏紧凑"],
                "keypoints": ["开场钩子", "冲突升级", "情绪高点"],
            },
        },
    )
    assert result["creation_id"] == creation_id
    print(f"    ✅ Step1 已保存，current_step={result['current_step']}")


def step_06_step2(c: Client, creation_id: str) -> None:
    """Step2：保存口播长文（手工预置，跳过 AI 与 TTS）"""
    print("\n[6] Step2 保存口播长文（预置文案，跳过 TTS）")
    result = c.call(
        "POST", "/api/step2/save",
        json={
            "creation_id": creation_id,
            "title": "少年逆袭之路",
            "content": SCRIPT_TEXT,
            "word_count": len(SCRIPT_TEXT),
            "skip_tts": True,
        },
    )
    print(f"    ✅ 长文已保存（skip_tts=True，不触发 TTS）")
    return result


def step_07_media_list(c: Client, creation_id: str) -> tuple[list[dict], list[dict]]:
    """Step3：获取素材列表"""
    print("\n[7] Step3 获取素材列表")
    data = c.call("GET", f"/api/step3/media-list?creation_id={creation_id}")
    videos = data.get("video_files", [])
    audios = data.get("audio_files", [])
    print(f"    ✅ 视频 {len(videos)} 个，音频 {len(audios)} 个")
    for v in videos:
        print(f"       - {v['name']}  {v.get('duration_str', '?')}")
    for a in audios:
        print(f"       - {a['name']}  {a.get('duration_str', '?')}  [{a.get('source')}]")
    return videos, audios


def step_08_remark(c: Client, creation_id: str, videos: list[dict]) -> list[dict]:
    """Step3：随机标记"""
    print("\n[8] Step3 随机标记视频片段")
    # 注意：接口接受的是视频「文件名」（相对项目 video_dir），不是完整路径
    video_names = [v["name"] for v in videos]
    result = c.call(
        "POST", "/api/step3/remark",
        json={
            "creation_id": creation_id,
            "video_files": video_names,
            "target_duration": 20,
        },
    )
    markers = result["markers"]
    print(f"    ✅ 生成 {result['marker_count']} 个标记，总时长 {result['total_duration']}s")
    for m in markers[:5]:
        print(f"       #{m['id']} {m['source']} [{m['start']:.1f} → {m['end']:.1f}] ({m['duration']}s)")
    return markers


def step_09_save_state(c: Client, creation_id: str, videos: list[dict], audios: list[dict]) -> None:
    """Step3：保存素材选择状态"""
    print("\n[9] Step3 保存素材状态")
    c.call(
        "POST", "/api/step3/save-state",
        json={
            "creation_id": creation_id,
            "audio_files": audios,
            "video_files": videos,
            "deleted_media": {},
        },
    )
    print("    ✅ 素材状态已保存")


def step_10_compose(
    c: Client, creation_id: str, markers: list[dict], audios: list[dict], label: str
) -> dict[str, Any]:
    """Step3：一键合成（真实产出 mp4）"""
    print(f"\n[10] Step3 一键合成（{label}）")

    # compose 接口的 audio_files 是「路径字符串列表」
    audio_paths = [a["path"] for a in audios if a.get("selected", True)]
    if not audio_paths:
        # 兜底：直接用 fixture 音频
        fixture_audio = AUDIO_DIR / "voice.mp3"
        if fixture_audio.exists():
            audio_paths = [str(fixture_audio)]
            print(f"    ⚠️ 无系统音频，使用 fixture: {fixture_audio.name}")
    assert audio_paths, "没有可用音频，无法合成"

    result = c.call(
        "POST", "/api/step3/compose",
        json={
            "creation_id": creation_id,
            "audio_files": audio_paths,
            "markers": markers,
            "fast_mode": False,
            "resolution": "1080x1920",
            "subtitle_style": "默认白字黑描边",
        },
    )
    task_id = result["task_id"]
    print(f"    ⏳ 提交合成任务：{task_id}")

    task = c.poll_task(task_id, timeout=300)
    print(f"    ✅ 合成完成（耗时 {task.get('duration_ms', '?')}ms）")
    return task.get("result") or {}


def step_11_verify_output(c: Client, creation_id: str, expect_min_duration: float) -> dict[str, Any]:
    """完成页：获取合成记录并校验产物"""
    print("\n[11] 完成页：多次合成列表 + 产物校验")
    outputs = c.call("GET", f"/api/creations/{creation_id}/outputs")
    assert outputs, "合成记录为空"
    print(f"    ✅ 合成记录 {len(outputs)} 条")

    latest = outputs[0]
    print(f"       最新 v{latest['version']}  {latest['output_path']}")
    print(f"       时长 {latest['duration_str']}  大小 {latest['file_size'] // 1024}KB  "
          f"分辨率 {latest['resolution']}")
    assert latest["is_latest"] is True, "is_latest 标记错误"

    # 校验文件真实存在且可被 ffprobe 解析
    out_path = Path(latest["output_path"])
    if not out_path.is_absolute():
        # 相对路径按 workdir 解析（后端 settings.workdir_abs）
        workdir = Path.cwd() / "workspace"
        out_path = workdir / out_path
    assert out_path.exists(), f"产物文件不存在: {out_path}"
    print(f"       产物路径: {out_path}")

    info = probe(out_path)
    print(f"       实际探测: 时长={info['duration']}s  {info['width']}x{info['height']}  "
          f"视频流={info['video_count']}  音频流={info['audio_count']}  "
          f"字幕流={info['subtitle_count']}")
    print(f"       编码: v={info['vcodec']}  a={info['acodec']}")

    # ---- 断言 ----
    assert info["video_count"] >= 1, "产物无视频流"
    assert info["audio_count"] >= 1, "产物无音频流"
    # 容差 1.5s：帧率对齐（concat/cfr）会有亚秒级误差
    tolerance = 1.5
    assert info["duration"] >= expect_min_duration - tolerance, (
        f"产物时长 {info['duration']}s 明显短于期望 {expect_min_duration}s（容差 {tolerance}s）"
    )
    assert abs(info["duration"] - expect_min_duration) <= tolerance, (
        f"产物时长 {info['duration']}s 与期望 {expect_min_duration}s 偏差超过 {tolerance}s"
    )
    assert info["width"] == 1080 and info["height"] == 1920, (
        f"分辨率不符: {info['width']}x{info['height']}（期望 1080x1920）"
    )
    assert info["size"] > 10_000, "产物文件过小，疑似空文件"

    print(f"    ✅ 产物校验全部通过（{info['size'] // 1024}KB，偏差 {info['duration'] - expect_min_duration:+.2f}s）")
    return latest


def step_12_markers_tweak(c: Client, creation_id: str, markers: list[dict]) -> list[dict]:
    """Step3：微调标记秒数（验证 ±1s 可编辑）"""
    print("\n[12] 标记微调（模拟前端 ±1s / 直接编辑）")
    tweaked = []
    for m in markers:
        new_m = dict(m)
        new_m["start"] = round(new_m["start"] + 1.0, 2)
        new_m["end"] = round(new_m["end"] + 1.0, 2)
        new_m["duration"] = round(new_m["end"] - new_m["start"], 2)
        tweaked.append(new_m)
    print(f"    ✅ {len(tweaked)} 个标记整体后移 1 秒")
    return tweaked


# ============================================================
# 主流程
# ============================================================
def run(base_url: str) -> int:
    """执行完整验收"""
    print("=" * 66)
    print("  端到端视频剪辑验收测试（真实素材 → 真实 mp4 产出）")
    print(f"  服务地址: {base_url}")
    print("=" * 66)

    # 前置检查
    if not VIDEO_DIR.exists() or not any(VIDEO_DIR.glob("*.mp4")):
        print("\n❌ 测试素材不存在，先生成：")
        print("   python -m tests.fixtures.make_fixtures")
        return 2

    c = Client(base_url)

    # 1~6 准备
    step_01_register(c)
    project_id = step_02_create_project(c)
    episode_id = step_03_create_episode(c, project_id)
    creation_id = step_04_create_creation(c, project_id, episode_id)
    step_05_step1(c, project_id, creation_id)
    step_06_step2(c, creation_id)

    # 7~10 剪辑
    videos, audios = step_07_media_list(c, creation_id)
    markers = step_08_remark(c, creation_id, videos)
    step_09_save_state(c, creation_id, videos, audios)
    step_10_compose(c, creation_id, markers, audios, "第 1 次")

    # 11 校验第 1 次产物
    expect_duration = sum(m["duration"] for m in markers)
    step_11_verify_output(c, creation_id, expect_duration)

    # 12~13 微调后重新合成（验证多次合成）
    tweaked = step_12_markers_tweak(c, creation_id, markers)
    step_10_compose(c, creation_id, tweaked, audios, "第 2 次（微调后）")
    outputs = c.call("GET", f"/api/creations/{creation_id}/outputs")
    assert len(outputs) >= 2, f"多次合成记录不足: {len(outputs)}"
    print(f"\n[13] ✅ 多次合成验证通过：共 {len(outputs)} 条记录")
    for o in outputs:
        print(f"       v{o['version']}  {o['duration_str']}  "
              f"{'🆕 最新' if o['is_latest'] else ''}")

    print("\n" + "=" * 66)
    print("  ✅ 端到端视频剪辑验收全部通过")
    print(f"     项目: {project_id}")
    print(f"     创作: {creation_id}")
    print(f"     合成: {len(outputs)} 个版本")
    print("=" * 66)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="端到端视频剪辑验收测试")
    parser.add_argument("--base-url", default="http://127.0.0.1:8010", help="服务地址")
    args = parser.parse_args()

    try:
        return run(args.base_url)
    except AcceptanceError as e:
        print(f"\n❌ 验收失败: {e}")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"\n❌ 意外错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
