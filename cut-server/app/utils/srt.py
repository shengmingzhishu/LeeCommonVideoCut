"""
SRT 字幕工具
============
- format_srt_time：秒 → HH:MM:SS,mmm（SRT 用逗号分隔毫秒）
- generate_srt：由时间轴生成 SRT 文本
- generate_timestamps_from_script：按字数比例估算时间轴（无对齐数据时的兜底）
"""
from __future__ import annotations

import re
from typing import Any


def format_srt_time(seconds: float) -> str:
    """秒 → HH:MM:SS,mmm"""
    if seconds < 0:
        seconds = 0
    total_ms = round(seconds * 1000)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(timestamps: list[dict[str, Any]], *, offset: float = 0.0) -> str:
    """由时间轴生成 SRT 文本

    Args:
        timestamps: [{"text": str, "start": float, "end": float}, ...]
        offset: 整体时间偏移（秒），用于片头字卡占据开头时对齐字幕

    Returns:
        SRT 文本（空时间轴返回空串）
    """
    blocks: list[str] = []
    index = 0

    for item in timestamps:
        text = str(item.get("text", "")).strip()
        if not text:
            continue

        start = float(item.get("start", 0)) + max(offset, 0.0)
        end = float(item.get("end", 0)) + max(offset, 0.0)
        if end <= start:
            end = start + 1.5

        index += 1
        blocks.append(
            f"{index}\n"
            f"{format_srt_time(start)} --> {format_srt_time(end)}\n"
            f"{text}\n"
        )

    return "\n".join(blocks)


def generate_timestamps_from_script(script: str, total_duration: float) -> list[dict[str, Any]]:
    """按句子字数比例分配时间轴（兜底估算）

    Args:
        script: 口播文案
        total_duration: 音频总时长（秒）

    Returns:
        [{"text": str, "start": float, "end": float}, ...]
    """
    sentences = [s.strip() for s in re.split(r"[。！？!?\n]+", script) if s.strip()]
    if not sentences or total_duration <= 0:
        return []

    lengths = [len(re.sub(r"\s", "", s)) for s in sentences]
    total_chars = sum(lengths)
    if total_chars == 0:
        return []

    result: list[dict[str, Any]] = []
    cursor = 0.0
    for sentence, chars in zip(sentences, lengths, strict=True):
        seg = total_duration * chars / total_chars
        result.append(
            {
                "text": sentence,
                "start": round(cursor, 2),
                "end": round(cursor + seg, 2),
            }
        )
        cursor += seg

    return result
