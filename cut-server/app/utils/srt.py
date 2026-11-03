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

# 单行字幕默认最大字数（ASS PlayRes 384 宽、FontSize 18 时的安全值）
DEFAULT_MAX_SUBTITLE_CHARS = 18

# 断句优先级：句读 > 空格
_CUE_BREAK_CHARS = "，,、；;：:。！？!?… "
# 硬切后可能落在行首的标点，需并回上一行
_CUE_LEADING_PUNCT = "，,、；;：:。！？!?…"


def format_srt_time(seconds: float) -> str:
    """秒 → HH:MM:SS,mmm"""
    if seconds < 0:
        seconds = 0
    total_ms = round(seconds * 1000)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _normalize_cue_text(text: str) -> str:
    """字幕文本归一化为单行：换行/制表符转空格并折叠连续空白。"""
    return re.sub(r"\s+", " ", text.replace("\u3000", " ")).strip()


def _split_cue_text(text: str, max_chars: int) -> list[str]:
    """把过长字幕切成若干单行片段，优先在标点或空格处断开。"""
    if max_chars < 4:
        max_chars = 4

    chunks: list[str] = []
    remaining = text
    while len(remaining) > max_chars:
        window = remaining[:max_chars]
        cut = 0
        for i in range(len(window) - 1, 0, -1):
            if window[i] in _CUE_BREAK_CHARS:
                cut = i + 1
                break
        if cut == 0:
            cut = max_chars

        chunk = remaining[:cut].strip()
        remaining = remaining[cut:].lstrip()

        # 硬切落在标点前时，把标点并入上一行，避免下一行以标点开头
        while remaining and remaining[0] in _CUE_LEADING_PUNCT:
            chunk += remaining[0]
            remaining = remaining[1:].lstrip()

        if chunk:
            chunks.append(chunk)

    if remaining:
        chunks.append(remaining)
    return chunks


def _distribute_times(
    start: float, end: float, chunks: list[str]
) -> list[tuple[float, float]]:
    """按各片段字数比例分配起止时间，保证首尾与原始时间轴一致。"""
    total_chars = sum(len(chunk) for chunk in chunks)
    if total_chars == 0:
        return []

    span = max(end - start, 0.0)
    times: list[tuple[float, float]] = []
    cursor = start
    consumed = 0
    for index, chunk in enumerate(chunks):
        consumed += len(chunk)
        chunk_end = end if index == len(chunks) - 1 else start + span * consumed / total_chars
        times.append((cursor, chunk_end))
        cursor = chunk_end
    return times


def generate_srt(
    timestamps: list[dict[str, Any]],
    *,
    offset: float = 0.0,
    max_chars: int = DEFAULT_MAX_SUBTITLE_CHARS,
) -> str:
    """由时间轴生成 SRT 文本

    字幕必须单行展示：先去除文本中的换行，再按 ``max_chars`` 把过长句子
    拆成多条字幕（优先在标点处断开），时长按字数比例分摊。

    Args:
        timestamps: [{"text": str, "start": float, "end": float}, ...]
        offset: 整体时间偏移（秒），用于片头字卡占据开头时对齐字幕
        max_chars: 单行字幕最大字数，按字幕样式的字号由调用方传入

    Returns:
        SRT 文本（空时间轴返回空串）
    """
    blocks: list[str] = []
    index = 0

    for item in timestamps:
        text = _normalize_cue_text(str(item.get("text", "")))
        if not text:
            continue

        start = float(item.get("start", 0)) + max(offset, 0.0)
        end = float(item.get("end", 0)) + max(offset, 0.0)
        if end <= start:
            end = start + 1.5

        chunks = _split_cue_text(text, max_chars)
        for chunk, (chunk_start, chunk_end) in zip(
            chunks, _distribute_times(start, end, chunks), strict=True
        ):
            index += 1
            blocks.append(
                f"{index}\n"
                f"{format_srt_time(chunk_start)} --> {format_srt_time(chunk_end)}\n"
                f"{chunk}\n"
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
