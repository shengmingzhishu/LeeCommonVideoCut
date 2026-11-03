"""
TTS 语音合成管理器
==================
引擎优先级：edge-tts（微软神经网络语音，音质最好）→ pyttsx3 → PowerShell SAPI。
任一引擎失败自动降级到下一个，全部失败抛 ExternalServiceError。

多音色能力：
- 14 个中文风格预设（覆盖 9 个微软神经网络发音人：浑厚/磁性/年轻男声，
  甜美/亲和/成熟/知性女声，方言，电商带货、口播解说、促销叫卖、温柔种草）。
- 支持 rate（语速 %）、pitch（音调 Hz）、volume（音量 %）；预设语调收敛在
  自然区间（语速 ±15%、音调 ±6Hz、音量 ±5%），避免机械感与破音。
- 支持按段落分配音色与段后停顿，逐段合成后用 ffmpeg 拼接。
- 合成前清洗 Markdown/表情/中文间空格，避免念出符号或异常停顿。

产物校验：ffprobe 复核时长，且要求总时长不短于文本所需（防止无效音频被标记完成）。

字幕时间轴：edge-tts 的 WordBoundary 事件优先；不可用时按字数比例估算。
"""
from __future__ import annotations

import asyncio
import json
import random
import re
import shutil
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logger import get_logger
from app.managers.edge_tts_patch import apply_edge_patch

logger = get_logger()

# 启动即修补 edge-tts 端点（旧端点在本机返回 WSS 403）
apply_edge_patch()

DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_VOICE_ID = "female_sweet"

# 中文口播速度：字/秒（仅用于时长估算）
CHARS_PER_SECOND = 3.5

# 音色目录：14 个风格预设，底层使用 9 个微软神经网络发音人
# 语调默认值收敛在自然区间：语速 ±15%、音调 ±6Hz、音量 ±5%
VOICE_CATALOG: list[dict[str, Any]] = [
    {
        "id": "male_deep", "name": "浑厚男声", "gender": "male",
        "style": "口播解说", "voice": "zh-CN-YunyangNeural",
        "rate": -4, "pitch": -2, "volume": 0,
        "description": "沉稳浑厚，适合纪录片旁白、专业口播",
    },
    {
        "id": "male_magnetic", "name": "磁性男声", "gender": "male",
        "style": "磁性叙事", "voice": "zh-CN-YunjianNeural",
        "rate": -2, "pitch": -1, "volume": 0,
        "description": "低沉有磁性，适合剧情解说、悬疑旁白",
    },
    {
        "id": "male_young", "name": "年轻男声", "gender": "male",
        "style": "年轻活力", "voice": "zh-CN-YunxiNeural",
        "rate": 3, "pitch": 0, "volume": 0,
        "description": "清爽年轻，适合日常分享、Vlog 口播",
    },
    {
        "id": "male_youth", "name": "少年男声", "gender": "male",
        "style": "少年轻松", "voice": "zh-CN-YunxiaNeural",
        "rate": 6, "pitch": 1, "volume": 0,
        "description": "少年感强，适合轻松搞笑、二次元内容",
    },
    {
        "id": "female_sweet", "name": "甜美女声", "gender": "female",
        "style": "甜美亲和", "voice": "zh-CN-XiaoxiaoNeural",
        "rate": 0, "pitch": 0, "volume": 0,
        "description": "甜美自然，通用性最强，适合大多数推广素材",
    },
    {
        "id": "female_warm", "name": "亲和女声", "gender": "female",
        "style": "亲和自然", "voice": "zh-CN-XiaoyiNeural",
        "rate": 3, "pitch": 0, "volume": 0,
        "description": "活泼亲和，适合种草、生活类内容",
    },
    {
        "id": "female_mature", "name": "成熟女声", "gender": "female",
        "style": "成熟稳重", "voice": "zh-CN-XiaoxiaoNeural",
        "rate": -6, "pitch": -1, "volume": 0,
        "description": "语速从容，适合知识讲解、情感叙事",
    },
    {
        "id": "female_elegant", "name": "知性女声", "gender": "female",
        "style": "知性温柔", "voice": "zh-CN-XiaoxuanNeural",
        "rate": -2, "pitch": 0, "volume": 0,
        "description": "温柔知性、吐字流畅，适合品牌旁白与情感故事",
    },
    {
        "id": "female_northeast", "name": "东北女声", "gender": "female",
        "style": "幽默方言", "voice": "zh-CN-liaoning-XiaobeiNeural",
        "rate": 2, "pitch": 0, "volume": 0,
        "description": "东北口音，幽默接地气，适合搞笑剧情",
    },
    {
        "id": "female_shaanxi", "name": "陕西女声", "gender": "female",
        "style": "方言亲切", "voice": "zh-CN-shaanxi-XiaoniNeural",
        "rate": 0, "pitch": 0, "volume": 0,
        "description": "陕西方言，地域特色鲜明",
    },
    {
        "id": "style_ecommerce", "name": "电商带货", "gender": "female",
        "style": "电商带货", "voice": "zh-CN-XiaoxiaoNeural",
        "rate": 10, "pitch": 2, "volume": 0,
        "description": "节奏明快、情绪饱满，适合商品卖点口播",
    },
    {
        "id": "style_hardsell", "name": "促销叫卖", "gender": "male",
        "style": "促销叫卖", "voice": "zh-CN-YunjianNeural",
        "rate": 15, "pitch": 2, "volume": 0,
        "description": "高亢有力，适合限时促销、福利播报",
    },
    {
        "id": "style_gentle", "name": "温柔种草", "gender": "female",
        "style": "温柔种草", "voice": "zh-CN-XiaoxiaoNeural",
        "rate": -6, "pitch": 0, "volume": 0,
        "description": "轻声细语，适合美妆、好物分享",
    },
    {
        "id": "style_news", "name": "新闻口播", "gender": "male",
        "style": "新闻口播", "voice": "zh-CN-YunyangNeural",
        "rate": 0, "pitch": 0, "volume": 0,
        "description": "正式规范，适合资讯播报、知识科普",
    },
]

VOICE_MAP: dict[str, dict[str, Any]] = {v["id"]: v for v in VOICE_CATALOG}


class TTSManager:
    """TTS 合成（多音色 + 多引擎降级）"""

    async def synthesize(
        self,
        *,
        script: str,
        output_path: Path,
        voice: str = DEFAULT_VOICE,
        engine: str | None = None,
        segments: list[Any] | None = None,
        provider: str | None = None,
    ) -> dict[str, object]:
        """合成 TTS 音频

        Args:
            script: 口播文案（未提供 segments 时按空行/换行拆段）
            output_path: 输出文件路径（.mp3）
            voice: 音色 ID（如 female_sweet）或 edge-tts 发音人名
            engine: 指定引擎（edge-tts / pyttsx3 / sapi）
            segments: 段落配置列表，元素含 text / voice_id / rate / pitch /
                volume / pause_after_ms；提供时优先于 script
            provider: 首选 provider（等价于 engine）

        Returns:
            {"engine_used", "provider", "provider_label", "voice_id",
             "voices_used", "duration", "timestamps", "warning"}

        Raises:
            ExternalServiceError: 所有引擎均失败
        """
        seg_list = self._normalize_segments(segments, script, voice)
        if not seg_list:
            raise ExternalServiceError("口播文案为空，无法合成", code="TTS_422_001")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        preferred = provider or engine or settings.tts_provider or settings.tts_default_engine
        chain = self._build_chain(preferred)

        errors: list[str] = []
        for name, fn in chain:
            try:
                if name == "edge-tts":
                    timestamps, used = await self._synthesize_edge_segments(seg_list, output_path)
                else:
                    text = "\n".join(s["text"] for s in seg_list)
                    timestamps = await fn(text, output_path, voice)
                    used = [seg_list[0].get("voice_id") or DEFAULT_VOICE_ID]

                duration = self._probe_duration(output_path)
                self._validate_duration(name, duration, seg_list)

                logger.info(
                    "TTS 合成完成",
                    extra={
                        "engine": name,
                        "output": str(output_path),
                        "duration": duration,
                        "voices": used,
                    },
                )
                return {
                    "engine_used": name,
                    "provider": name,
                    "provider_label": self._provider_label(name),
                    "voice_id": used[0] if used else DEFAULT_VOICE_ID,
                    "voices_used": used,
                    "duration": round(duration, 1),
                    "timestamps": timestamps,
                    "warning": "; ".join(errors) if errors else None,
                }
            except Exception as e:
                errors.append(f"{name}: {type(e).__name__}: {str(e)[:120]}")
                logger.warning(
                    f"TTS 引擎 {name} 失败，降级到下一个",
                    extra={"engine": name, "error": str(e)[:200]},
                )

        raise ExternalServiceError(
            "TTS 合成全部失败",
            code="TTS_502_001",
            detail="; ".join(errors),
        )

    # ---------- 音色目录 ----------

    @staticmethod
    def list_voices() -> list[dict[str, Any]]:
        """返回音色目录（含默认 prosody）"""
        return [dict(v) for v in VOICE_CATALOG]

    @staticmethod
    def resolve_profile(voice_id: str | None, voice: str | None = None) -> dict[str, Any]:
        """把音色 ID / 发音人名解析为合成参数"""
        if voice_id and voice_id in VOICE_MAP:
            prof = dict(VOICE_MAP[voice_id])
        else:
            prof = dict(VOICE_MAP[DEFAULT_VOICE_ID])
            if voice_id and "Neural" in voice_id:
                prof["voice"] = voice_id
        if voice and "Neural" in voice:
            prof["voice"] = voice
        return prof

    # ---------- 内部工具 ----------

    @staticmethod
    def _normalize_text(text: str) -> str:
        """清洗待朗读文本，避免念出 Markdown 符号或出现异常停顿"""
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"[*_`#>|~]+", "", text)
        text = re.sub(r"(?m)^\s*[-+]\s+", "", text)
        text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]", "", text)
        text = text.replace("\u3000", " ").replace("...", "…")
        text = re.sub(r"[ \t]+", " ", text)
        # 去掉中文字符之间的水平空格，避免逐字停顿（保留换行作为自然停顿）
        text = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[\u4e00-\u9fff])", "", text)
        return text.strip()

    @staticmethod
    def _normalize_segments(
        segments: list[Any] | None, script: str, voice: str
    ) -> list[dict[str, Any]]:
        """把入参统一为段落字典列表"""
        if segments:
            result: list[dict[str, Any]] = []
            for i, seg in enumerate(segments):
                data = seg if isinstance(seg, dict) else (
                    seg.model_dump() if hasattr(seg, "model_dump") else dict(seg)
                )
                text = TTSManager._normalize_text(str(data.get("text") or ""))
                if not text:
                    continue
                data["text"] = text
                data.setdefault("index", i)
                result.append(data)
            return result

        paragraphs = [
            TTSManager._normalize_text(p)
            for p in re.split(r"\n+", script or "")
        ]
        paragraphs = [p for p in paragraphs if p]
        return [{"index": i, "text": p, "voice_id": voice} for i, p in enumerate(paragraphs)]

    @staticmethod
    def _provider_label(name: str) -> str:
        return {
            "edge-tts": "微软神经网络语音（高质量）",
            "pyttsx3": "Windows 离线语音（降级）",
            "sapi": "Windows SAPI（降级）",
        }.get(name, name)

    @staticmethod
    def _build_chain(preferred: str) -> list[tuple[str, object]]:
        """按偏好构建引擎降级链"""
        handlers = {
            "edge-tts": ("edge-tts", None),
            "pyttsx3": ("pyttsx3", TTSManager._synthesize_pyttsx3),
            "sapi": ("sapi", TTSManager._synthesize_sapi),
        }
        order: list[str] = []
        if preferred:
            order.append(preferred)
        for name in (settings.tts_fallbacks or "").split(","):
            name = name.strip()
            if name and name not in order:
                order.append(name)

        chain: list[tuple[str, object]] = []
        for name in order:
            if name not in handlers:
                continue
            _, fn = handlers[name]
            chain.append((name, fn))
        return chain or [("edge-tts", None)]

    async def _synthesize_edge_segments(
        self,
        segments: list[dict[str, Any]],
        output_path: Path,
    ) -> tuple[list[dict[str, object]], list[str]]:
        """逐段合成（可分别指定音色），再拼接为一条音频"""
        import edge_tts

        tmp_dir = output_path.parent / f".tts_{output_path.stem}"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)
        tmp_dir.mkdir(parents=True, exist_ok=True)

        parts: list[Path] = []
        timestamps: list[dict[str, object]] = []
        used_voices: list[str] = []
        cursor = 0.0

        try:
            for i, seg in enumerate(segments):
                text = seg["text"]
                prof = self.resolve_profile(seg.get("voice_id"), seg.get("voice"))
                rate = int(seg.get("rate", prof.get("rate", 0)))
                pitch = int(seg.get("pitch", prof.get("pitch", 0)))
                volume = int(seg.get("volume", prof.get("volume", 0)))

                # 微软边缘服务有短时频率限制（429），逐段重试并指数退避
                audio_chunks: list[bytes] = []
                boundaries: list[dict[str, object]] = []
                last_error: Exception | None = None
                for attempt in range(6):
                    try:
                        communicate = edge_tts.Communicate(
                            text,
                            prof["voice"],
                            rate=self._signed(rate, "%"),
                            pitch=self._signed(pitch, "Hz"),
                            volume=self._signed(volume, "%"),
                        )
                        audio_chunks.clear()
                        boundaries.clear()
                        async for chunk in communicate.stream():
                            if chunk["type"] == "audio":
                                audio_chunks.append(chunk["data"])
                            elif chunk["type"] == "WordBoundary":
                                offset = chunk.get("offset", 0) / 10_000_000
                                span = chunk.get("duration", 0) / 10_000_000
                                boundaries.append(
                                    {
                                        "text": chunk.get("text", ""),
                                        "start": cursor + offset,
                                        "end": cursor + offset + span,
                                    }
                                )

                        if not audio_chunks:
                            raise RuntimeError(f"第 {i + 1} 段未返回音频数据")
                        last_error = None
                        break
                    except Exception as e:
                        last_error = e
                        message = str(e)
                        retryable = any(
                            keyword in message
                            for keyword in ("429", "Invalid response status", "503", "timed out", "Timeout")
                        )
                        if attempt < 5 and retryable:
                            await asyncio.sleep(1.0 * (2 ** attempt) + random.uniform(0, 0.5))
                            continue
                        raise

                if last_error is not None:
                    raise last_error

                if i > 0:
                    # 段间轻微节流，降低连续连接被限流的概率
                    await asyncio.sleep(0.5)

                seg_path = tmp_dir / f"seg_{i + 1:03d}.mp3"
                seg_path.write_bytes(b"".join(audio_chunks))
                parts.append(seg_path)
                used_voices.append(prof["voice"])

                seg_duration = self._probe_duration(seg_path)
                if seg_duration <= 0.2:
                    raise RuntimeError(f"第 {i + 1} 段音频无效（{seg_duration:.2f}s）")
                self._validate_duration("edge-tts", seg_duration, [seg])

                if not boundaries:
                    boundaries = self._estimate_timestamps(
                        text, offset=cursor, duration=seg_duration
                    )
                timestamps.extend(boundaries)
                cursor += seg_duration

                pause_ms = int(seg.get("pause_after_ms") or 0)
                if pause_ms > 0 and i < len(segments) - 1:
                    pause_path = tmp_dir / f"pause_{i + 1:03d}.mp3"
                    await asyncio.to_thread(self._make_silence, pause_ms, pause_path)
                    parts.append(pause_path)
                    cursor += pause_ms / 1000.0

            await asyncio.to_thread(self._concat_mp3, parts, output_path)
            return timestamps, used_voices
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def _validate_duration(self, engine: str, duration: float, segments: list[dict[str, Any]]) -> None:
        """校验音频时长不短于文本所需（防止无效音频被标记完成）"""
        if duration <= 0.5:
            raise RuntimeError(f"{engine} 产出的音频无效（时长 {duration:.2f}s）")
        chars = sum(len(re.sub(r"\s", "", s["text"])) for s in segments)
        min_required = chars / max(settings.tts_min_chars_per_sec, 1.0)
        if duration + 0.3 < min_required:
            raise RuntimeError(
                f"{engine} 音频时长 {duration:.2f}s 短于文本所需 {min_required:.2f}s"
            )

    @staticmethod
    def _signed(value: int, unit: str) -> str:
        return f"{value:+d}{unit}"

    @staticmethod
    def _make_silence(pause_ms: int, path: Path) -> None:
        """生成静音 mp3（用于段后停顿）"""
        import subprocess

        seconds = max(pause_ms, 0) / 1000.0
        result = subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                "-t", f"{seconds:.3f}", "-c:a", "libmp3lame", "-b:a", "48k", str(path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"静音生成失败: {result.stderr[-200:]}")

    @staticmethod
    def _concat_mp3(parts: list[Path], output_path: Path) -> None:
        """拼接多段音频（统一重编码为 24kHz 单声道 192kbps）"""
        import subprocess

        if len(parts) == 1:
            shutil.copyfile(parts[0], output_path)
            return
        list_file = output_path.parent / f".{output_path.stem}_concat.txt"
        list_file.write_text(
            "\n".join(f"file '{p.as_posix()}'" for p in parts), encoding="utf-8"
        )
        try:
            result = subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
                    "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "24000", "-ac", "1",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )
        finally:
            list_file.unlink(missing_ok=True)
        if result.returncode != 0:
            raise RuntimeError(f"音频拼接失败: {result.stderr[-200:]}")

    @staticmethod
    async def _synthesize_pyttsx3(script: str, output_path: Path, voice: str) -> list[dict[str, object]]:
        """pyttsx3：Windows 离线 SAPI，先出 wav 再转 mp3"""
        import pyttsx3

        wav_path = output_path.with_suffix(".wav")
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        engine.save_to_file(script, str(wav_path))
        engine.runAndWait()

        if not wav_path.exists():
            raise RuntimeError("pyttsx3 未生成 wav 文件")

        await asyncio.to_thread(TTSManager._wav_to_mp3, wav_path, output_path)
        wav_path.unlink(missing_ok=True)
        return TTSManager._estimate_timestamps(script)

    @staticmethod
    async def _synthesize_sapi(script: str, output_path: Path, voice: str) -> list[dict[str, object]]:
        """PowerShell SAPI：Windows 内置语音合成器，零第三方依赖"""
        wav_path = output_path.with_suffix(".wav")
        ps_script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.Rate = 2; "
            f"$s.SetOutputToWaveFile('{wav_path}'); "
            f"$s.Speak('{script.replace(chr(39), chr(39) * 2)}'); "
            "$s.Dispose();"
        )
        proc = await asyncio.create_subprocess_exec(
            "powershell",
            "-NoProfile",
            "-Command",
            ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"SAPI 失败: {stderr.decode('utf-8', errors='ignore')[:200]}")

        if not wav_path.exists():
            raise RuntimeError("SAPI 未生成 wav 文件")

        await asyncio.to_thread(TTSManager._wav_to_mp3, wav_path, output_path)
        wav_path.unlink(missing_ok=True)
        return TTSManager._estimate_timestamps(script)

    @staticmethod
    def _wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
        """ffmpeg 转码 wav → mp3"""
        import subprocess

        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-b:a", "192k", "-ac", "1", str(mp3_path)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg 转码失败: {result.stderr[-200:]}")

    @staticmethod
    def _probe_duration(path: Path) -> float:
        """用 ffprobe 读取音频实际时长（失败返回 0）"""
        import subprocess

        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return 0.0
            return float(result.stdout.strip())
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            return 0.0

    @staticmethod
    def _estimate_duration(script: str) -> float:
        """按字数估算时长（秒）"""
        chars = len(re.sub(r"\s", "", script))
        return round(chars / CHARS_PER_SECOND, 1)

    @staticmethod
    def _estimate_timestamps(
        script: str,
        *,
        offset: float = 0.0,
        duration: float | None = None,
    ) -> list[dict[str, object]]:
        """按句子长度比例分配时间轴（字幕兜底估算）"""
        sentences = [s for s in re.split(r"[。！？!?\n]+", script) if s.strip()]
        if not sentences:
            return []

        total_chars = sum(len(re.sub(r"\s", "", s)) for s in sentences)
        if total_chars == 0:
            return []

        total = duration if duration and duration > 0 else TTSManager._estimate_duration(script)
        result: list[dict[str, object]] = []
        cursor = offset
        for sentence in sentences:
            chars = len(re.sub(r"\s", "", sentence))
            seg = round(total * chars / total_chars, 2)
            result.append(
                {
                    "text": sentence.strip(),
                    "start": round(cursor, 2),
                    "end": round(cursor + seg, 2),
                }
            )
            cursor += seg
        return result


def dump_timestamps(timestamps: list[dict[str, object]]) -> str:
    """时间轴序列化（便于落盘与排查）"""
    return json.dumps(timestamps, ensure_ascii=False, indent=2)
