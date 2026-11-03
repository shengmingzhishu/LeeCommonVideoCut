"""
Step3 转场与主持人人像单元测试
==============================
覆盖：
- TransitionConfig / AvatarConfig 契约约束
- xfade 滤镜参数（类型映射、时长夹取、offset 累计）
- 直切分组（组内 xfade、组间 concat）
- 人像圆形蒙版滤镜（四角定位、尺寸、描边、阴影、时间段）
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import ExternalServiceError
from app.managers.ffmpeg_manager import FFMPEG_TIMEOUT, XFADE_MAP, FFmpegManager
from app.schemas import AvatarConfig, TransitionConfig


def _fake_run_factory(commands: list[list[str]]):
    """生成写空文件的 _run 替身，并记录完整命令"""

    def fake_run(cmd: list[str], timeout: int = FFMPEG_TIMEOUT) -> subprocess.CompletedProcess[str]:
        commands.append(cmd)
        Path(cmd[-1]).parent.mkdir(parents=True, exist_ok=True)
        Path(cmd[-1]).write_bytes(b"stub")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    return fake_run


def _filter_complex(cmd: list[str]) -> str:
    return cmd[cmd.index("-filter_complex") + 1]


class TestTransitionConfig:
    """转场配置契约"""

    def test_default_is_direct_cut(self):
        cfg = TransitionConfig()
        assert cfg.type == "none"
        assert cfg.duration == pytest.approx(0.5)

    @pytest.mark.parametrize("kind", ["none", "fade", "slide", "zoom"])
    def test_accepts_supported_types(self, kind: str):
        assert TransitionConfig(type=kind).type == kind

    def test_rejects_unknown_type(self):
        with pytest.raises(PydanticValidationError):
            TransitionConfig(type="wipe")

    @pytest.mark.parametrize("duration", [0.2, 0.6, 1.5])
    def test_accepts_duration_in_range(self, duration: float):
        assert TransitionConfig(type="fade", duration=duration).duration == pytest.approx(duration)

    @pytest.mark.parametrize("duration", [0.19, 1.51])
    def test_rejects_duration_out_of_range(self, duration: float):
        with pytest.raises(PydanticValidationError):
            TransitionConfig(type="fade", duration=duration)

    def test_xfade_map_covers_all_non_cut_types(self):
        assert XFADE_MAP == {"fade": "fade", "slide": "slideleft", "zoom": "zoomin"}


class TestXfadeGroup:
    """xfade 滤镜链参数"""

    def test_maps_type_and_accumulates_offset(self, tmp_path: Path, monkeypatch):
        commands: list[list[str]] = []
        monkeypatch.setattr(FFmpegManager, "_run", staticmethod(_fake_run_factory(commands)))
        clips = [tmp_path / f"c{i}.mp4" for i in range(3)]
        for clip in clips:
            clip.write_bytes(b"x")

        FFmpegManager._xfade_group(
            clips,
            [4.0, 6.0, 3.0],
            [{"type": "fade", "duration": 0.5}, {"type": "zoom", "duration": 1.0}],
            tmp_path / "out.mp4",
            crf=23,
            preset="medium",
        )

        graph = _filter_complex(commands[0])
        # 第 1 个转场：fade，offset = 4.0 - 0.5
        assert "xfade=transition=fade:duration=0.500:offset=3.500" in graph
        # 第 2 个转场：zoom → zoomin，offset = (4+6-0.5) - 1.0
        assert "xfade=transition=zoomin:duration=1.000:offset=8.500" in graph
        assert graph.count("xfade=") == 2

    def test_clamps_duration_to_45_percent_of_shorter_clip(self, tmp_path: Path, monkeypatch):
        commands: list[list[str]] = []
        monkeypatch.setattr(FFmpegManager, "_run", staticmethod(_fake_run_factory(commands)))
        clips = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
        for clip in clips:
            clip.write_bytes(b"x")

        FFmpegManager._xfade_group(
            clips,
            [2.0, 1.0],
            [{"type": "slide", "duration": 1.5}],
            tmp_path / "out.mp4",
            crf=23,
            preset="medium",
        )

        graph = _filter_complex(commands[0])
        # min(1.5, 2.0*0.45, 1.0*0.45) = 0.45
        assert "xfade=transition=slideleft:duration=0.450:offset=1.550" in graph

    def test_keeps_minimum_duration(self, tmp_path: Path, monkeypatch):
        commands: list[list[str]] = []
        monkeypatch.setattr(FFmpegManager, "_run", staticmethod(_fake_run_factory(commands)))
        clips = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
        for clip in clips:
            clip.write_bytes(b"x")

        FFmpegManager._xfade_group(
            clips,
            [0.05, 0.05],
            [{"type": "fade", "duration": 0.2}],
            tmp_path / "out.mp4",
            crf=23,
            preset="medium",
        )

        assert "duration=0.050" in _filter_complex(commands[0])

    def test_unknown_type_falls_back_to_fade(self, tmp_path: Path, monkeypatch):
        commands: list[list[str]] = []
        monkeypatch.setattr(FFmpegManager, "_run", staticmethod(_fake_run_factory(commands)))
        clips = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
        for clip in clips:
            clip.write_bytes(b"x")

        FFmpegManager._xfade_group(
            clips,
            [3.0, 3.0],
            [{"type": "wipe", "duration": 0.5}],
            tmp_path / "out.mp4",
            crf=23,
            preset="medium",
        )

        assert "xfade=transition=fade:" in _filter_complex(commands[0])


class TestMergeGrouping:
    """直切边界分组"""

    def test_splits_groups_on_direct_cut(self, tmp_path: Path, monkeypatch):
        calls: dict[str, object] = {}
        clips = [tmp_path / f"c{i}.mp4" for i in range(3)]
        for clip in clips:
            clip.write_bytes(b"x")

        monkeypatch.setattr(FFmpegManager, "probe_duration", staticmethod(lambda _p: 4.0))

        def fake_xfade(clip_list, durations, transitions, output, *, crf, preset):
            calls["xfade"] = {
                "clips": list(clip_list),
                "durations": list(durations),
                "transitions": list(transitions),
            }
            output.write_bytes(b"group")
            return output

        def fake_concat(paths, output):
            calls["concat"] = list(paths)
            output.write_bytes(b"merged")
            return output

        def fake_safe_move(src, dst):
            Path(dst).write_bytes(Path(src).read_bytes())
            return Path(dst)

        monkeypatch.setattr(FFmpegManager, "_xfade_group", staticmethod(fake_xfade))
        monkeypatch.setattr(FFmpegManager, "concat_segments", staticmethod(fake_concat))
        monkeypatch.setattr(FFmpegManager, "safe_move", staticmethod(fake_safe_move))

        out = tmp_path / "final.mp4"
        FFmpegManager.merge_clips_with_transitions(
            clips,
            [{"type": "fade", "duration": 0.6}, {"type": "none"}],
            out,
        )

        xfade = calls["xfade"]
        assert xfade["clips"] == clips[:2]  # type: ignore[index]
        assert xfade["transitions"] == [{"type": "fade", "duration": 0.6}]  # type: ignore[index]
        assert calls["concat"] == [tmp_path / ".group_01.mp4", clips[2]]  # type: ignore[comparison-overlap]
        assert out.exists()
        assert not (tmp_path / ".group_01.mp4").exists()

    def test_single_clip_copies_without_transition(self, tmp_path: Path, monkeypatch):
        calls: list[tuple[Path, Path]] = []
        clip = tmp_path / "only.mp4"
        clip.write_bytes(b"x")

        def fake_copy(src, dst):
            calls.append((Path(src), Path(dst)))
            Path(dst).write_bytes(b"copy")
            return Path(dst)

        monkeypatch.setattr(FFmpegManager, "probe_duration", staticmethod(lambda _p: 5.0))
        monkeypatch.setattr(FFmpegManager, "_copy", staticmethod(fake_copy))

        out = tmp_path / "out.mp4"
        FFmpegManager.merge_clips_with_transitions([clip], [], out)
        assert calls == [(clip, out)]

    def test_single_clip_pads_to_audio_duration(self, tmp_path: Path, monkeypatch):
        calls: dict[str, float] = {}
        clip = tmp_path / "only.mp4"
        clip.write_bytes(b"x")

        def fake_pad(src, pad, dst, *, crf, preset):
            calls["pad"] = pad
            Path(dst).write_bytes(b"padded")
            return Path(dst)

        monkeypatch.setattr(FFmpegManager, "probe_duration", staticmethod(lambda _p: 5.0))
        monkeypatch.setattr(FFmpegManager, "_pad_clip", staticmethod(fake_pad))

        FFmpegManager.merge_clips_with_transitions([clip], [], tmp_path / "out.mp4", pad_to=7.0)
        assert calls["pad"] == pytest.approx(2.0)

    def test_rejects_empty_clip_list(self):
        with pytest.raises(ExternalServiceError):
            FFmpegManager.merge_clips_with_transitions([], [], Path("out.mp4"))


class TestAvatarConfigSchema:
    """人像配置契约"""

    def test_defaults(self):
        cfg = AvatarConfig()
        assert cfg.position == "bottom_right"
        assert cfg.size_ratio == pytest.approx(0.18)
        assert cfg.border_color == "#FFFFFF"
        assert cfg.border_width == 4
        assert cfg.shadow is True

    @pytest.mark.parametrize(
        "position", ["top_left", "top_right", "bottom_left", "bottom_right"]
    )
    def test_accepts_four_corners(self, position: str):
        assert AvatarConfig(position=position).position == position

    def test_rejects_unknown_position(self):
        with pytest.raises(PydanticValidationError):
            AvatarConfig(position="center")

    @pytest.mark.parametrize("size_ratio", [0.05, 0.18, 0.5])
    def test_accepts_size_ratio_in_range(self, size_ratio: float):
        assert AvatarConfig(size_ratio=size_ratio).size_ratio == pytest.approx(size_ratio)

    @pytest.mark.parametrize("size_ratio", [0.04, 0.51])
    def test_rejects_size_ratio_out_of_range(self, size_ratio: float):
        with pytest.raises(PydanticValidationError):
            AvatarConfig(size_ratio=size_ratio)

    @pytest.mark.parametrize("border_width", [0, 20])
    def test_accepts_border_width_in_range(self, border_width: int):
        assert AvatarConfig(border_width=border_width).border_width == border_width

    @pytest.mark.parametrize("border_width", [-1, 21])
    def test_rejects_border_width_out_of_range(self, border_width: int):
        with pytest.raises(PydanticValidationError):
            AvatarConfig(border_width=border_width)


class TestAvatarFilters:
    """圆形头像滤镜链"""

    def test_bottom_right_geometry_and_shadow(self):
        filters = FFmpegManager._avatar_filters(1080, 1920, {}, "[sub]")
        # short_side=1080 → size=194，border=4 → outer=202，margin=27
        assert "color=c=#FFFFFF:s=202x202" in filters[0]
        assert "scale=194:194" in filters[1]
        assert f"[ring][av]overlay=4:4[avc]" in filters

        # 右下角：x=1080-202-27=851，y=1920-202-27=1691；阴影偏移 +6
        assert "[sub][sh]overlay=857:1697:enable='gte(t,0.00)'[b1]" in filters
        assert "[b1][avc]overlay=851:1691:enable='gte(t,0.00)'[outv]" in filters
        assert any("boxblur=8:8" in item for item in filters)
        assert len(filters) == 6

    def test_top_left_with_time_range(self):
        filters = FFmpegManager._avatar_filters(
            1080,
            1920,
            {
                "position": "top_left",
                "size_ratio": 0.2,
                "border_width": 6,
                "border_color": "#FFAA00",
                "shadow": False,
                "start": 1.5,
                "end": 5,
            },
            "[sub]",
        )
        # size=216，outer=228，margin=27
        assert "color=c=#FFAA00:s=228x228" in filters[0]
        assert "geq=r=255:g=170:b=0" in filters[0]
        assert "[sub][avc]overlay=27:27:enable='between(t,1.50,5.00)'[outv]" in filters
        assert not any("boxblur" in item for item in filters)
        assert len(filters) == 4

    def test_size_has_48px_floor(self):
        filters = FFmpegManager._avatar_filters(
            200, 300, {"size_ratio": 0.05, "border_width": 0}, "[0:v]"
        )
        assert "scale=48:48" in filters[1]
        assert "s=48x48" in filters[0]

    def test_open_ended_time_range(self):
        filters = FFmpegManager._avatar_filters(
            720, 1280, {"start": 3.0, "shadow": False}, "[0:v]"
        )
        assert "enable='gte(t,3.00)'" in filters[-1]

    def test_hex_to_rgb(self):
        assert FFmpegManager._hex_to_rgb("#FFAA00") == (255, 170, 0)
        assert FFmpegManager._hex_to_rgb("#0f0") == (0, 255, 0)
        assert FFmpegManager._hex_to_rgb("bad-color") == (255, 255, 255)


class TestFinalizeVideo:
    """字幕/人像组合入口"""

    def test_copies_when_no_effect(self, tmp_path: Path, monkeypatch):
        calls: list[tuple[Path, Path]] = []
        video = tmp_path / "v.mp4"
        video.write_bytes(b"x")

        def fake_copy(src, dst):
            calls.append((Path(src), Path(dst)))
            Path(dst).write_bytes(b"copy")
            return Path(dst)

        monkeypatch.setattr(FFmpegManager, "_copy", staticmethod(fake_copy))
        out = tmp_path / "out.mp4"
        FFmpegManager.finalize_video(video, out)
        assert calls == [(video, out)]

    def test_avatar_requires_file_id(self, tmp_path: Path, monkeypatch):
        calls: list[tuple[Path, Path]] = []
        video = tmp_path / "v.mp4"
        avatar = tmp_path / "a.png"
        video.write_bytes(b"x")
        avatar.write_bytes(b"x")

        def fake_copy(src, dst):
            calls.append((Path(src), Path(dst)))
            Path(dst).write_bytes(b"copy")
            return Path(dst)

        monkeypatch.setattr(FFmpegManager, "_copy", staticmethod(fake_copy))
        FFmpegManager.finalize_video(
            video,
            tmp_path / "out.mp4",
            avatar_path=avatar,
            avatar={"position": "bottom_right"},
        )
        assert calls  # 无 file_id 时忽略人像