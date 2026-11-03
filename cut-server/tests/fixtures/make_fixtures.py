"""
测试素材生成器
================
使用项目内置的完整版 ffmpeg（tools/ffmpeg/bin/），通过 lavfi 合成真实素材。

产物（写入 tests/fixtures/media/）：
├── videos/ep001.mp4   12 秒 · 320x240 · 有声（440Hz）
├── videos/ep002.mp4   10 秒 · 320x240 · 无声
└── audio/voice.mp3     8 秒 · 300Hz（模拟口播）

用法：
    python -m tests.fixtures.make_fixtures
"""
from __future__ import annotations

import math
import struct
import subprocess
import wave
from pathlib import Path

# 优先使用项目内置的完整版 ffmpeg
_REPO_ROOT = Path(__file__).resolve().parents[3]
_BUNDLED = _REPO_ROOT / "tools" / "ffmpeg" / "bin"
FFMPEG = str(_BUNDLED / "ffmpeg.exe") if (_BUNDLED / "ffmpeg.exe").exists() else "ffmpeg"
FFPROBE = str(_BUNDLED / "ffprobe.exe") if (_BUNDLED / "ffprobe.exe").exists() else "ffprobe"

FIXTURE_DIR = Path(__file__).parent / "media"
VIDEO_DIR = FIXTURE_DIR / "videos"
AUDIO_DIR = FIXTURE_DIR / "audio"

W, H, FPS = 320, 240, 25


def _run(cmd: list[str], stdin_data: bytes | None = None) -> None:
    """执行命令，失败时抛出带 stderr 的异常"""
    result = subprocess.run(
        cmd, input=stdin_data, capture_output=True, timeout=180
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"命令失败: {' '.join(cmd[:5])}...\n"
            f"stderr: {result.stderr.decode('utf-8', 'ignore')[-600:]}"
        )


def _write_raw_frames(path: Path, seconds: int, with_sound: bool) -> None:
    """用 ffmpeg lavfi 合成测试视频

    画面内容：随时间变化的彩色测试图 + 时间戳，便于肉眼确认裁切位置。
    """
    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"testsrc=size={W}x{H}:rate={FPS}:duration={seconds}",
    ]
    if with_sound:
        cmd += [
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}:sample_rate=44100",
        ]
    cmd += [
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30", "-pix_fmt", "yuv420p",
    ]
    if with_sound:
        cmd += ["-c:a", "aac", "-b:a", "64k", "-shortest"]
    else:
        cmd += ["-an"]
    cmd += [str(path)]

    _run(cmd)


def _write_tone_wav(path: Path, seconds: int, freq: float) -> None:
    """生成 WAV 纯音（模拟口播）"""
    sample_rate = 44100
    frames = bytearray()
    total = sample_rate * seconds
    for i in range(total):
        t = i / sample_rate
        # 基频 + 轻微谐波，接近人声频谱
        value = (
            0.35 * math.sin(2 * math.pi * freq * t)
            + 0.15 * math.sin(2 * math.pi * freq * 2 * t)
            + 0.08 * math.sin(2 * math.pi * freq * 3 * t)
        )
        # 音节包络（每 0.35 秒一次起伏）
        envelope = 0.5 + 0.5 * math.sin(2 * math.pi * t / 0.35)
        sample = int(max(-1.0, min(1.0, value * envelope)) * 24000)
        frames += struct.pack("<h", sample)

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(frames))


def make_videos() -> list[Path]:
    """生成 2 个测试视频（有声 + 无声）"""
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    ep1 = VIDEO_DIR / "ep001.mp4"
    if not ep1.exists():
        print("    生成 ep001.mp4（12 秒 · 有声）...")
        _write_raw_frames(ep1, seconds=12, with_sound=True)
    created.append(ep1)

    ep2 = VIDEO_DIR / "ep002.mp4"
    if not ep2.exists():
        print("    生成 ep002.mp4（10 秒 · 无声）...")
        _write_raw_frames(ep2, seconds=10, with_sound=False)
    created.append(ep2)

    return created


def make_audio() -> Path:
    """生成 8 秒口播音频（模拟）"""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    mp3 = AUDIO_DIR / "voice.mp3"
    if not mp3.exists():
        print("    生成 voice.mp3（8 秒）...")
        # 直接用 lavfi 生成（避免 WAV 中间环节）
        _run([
            FFMPEG, "-y",
            "-f", "lavfi", "-i", "sine=frequency=300:duration=8:sample_rate=44100",
            "-c:a", "libmp3lame", "-b:a", "128k",
            str(mp3),
        ])
    return mp3


def probe_duration(path: Path) -> float:
    """探测时长"""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    try:
        return round(float(out.stdout.strip()), 2)
    except ValueError:
        return 0.0


def main() -> None:
    """生成全部素材并打印清单"""
    print("=== 生成测试素材 ===")

    videos = make_videos()
    for v in videos:
        print(f"  视频: {v.name}  时长={probe_duration(v)}s  大小={v.stat().st_size // 1024}KB")

    audio = make_audio()
    print(f"  音频: {audio.name}  时长={probe_duration(audio)}s  大小={audio.stat().st_size // 1024}KB")

    print(f"\n✅ 素材已生成于: {FIXTURE_DIR}")


if __name__ == "__main__":
    main()
