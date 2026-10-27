import subprocess
import wave
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.models.schema import TaskVideoRequest, VideoParams, VideoScriptRequest
from app.services import llm, task, video_duration
from app.utils import utils
from app.utils.subtitle_reader import moviepy_subtitles


@pytest.mark.parametrize("model", [VideoParams, TaskVideoRequest, VideoScriptRequest])
def test_duration_defaults_and_bounds(model):
    assert model(video_subject="History").video_duration == 0
    for value in (1, 47, 90):
        assert model(video_subject="History", video_duration=value).video_duration == value
    for value in (-1, 91, 1.5):
        with pytest.raises(ValidationError):
            model(video_subject="History", video_duration=value)


def test_script_prompt_uses_requested_narration_length():
    prompt = llm.build_script_prompt("Human history", video_duration=90)
    assert "approximately 90 seconds" in prompt
    assert "207 spoken words" in prompt
    assert "# Narration duration" not in llm.build_script_prompt("History")
    with pytest.raises(ValueError):
        llm.build_script_prompt("History", video_duration=91)


def test_pipeline_script_forwards_duration():
    params = VideoParams(video_subject="History", video_duration=90)
    with patch.object(llm, "generate_script", return_value="A complete story.") as generate:
        assert task.generate_script("duration-test", params) == "A complete story."
    assert generate.call_args.kwargs["video_duration"] == 90


@pytest.mark.parametrize("seconds", [1, 47, 90])
def test_real_audio_fit_and_caption_clipping_preserve_source(tmp_path, seconds):
    original = tmp_path / "original.wav"
    subprocess.run(
        [utils.get_ffmpeg_binary(), "-v", "error", "-y", "-f", "lavfi", "-i",
         "sine=frequency=440:duration=2", "-c:a", "pcm_s16le", str(original)],
        check=True, capture_output=True,
    )
    original_bytes = original.read_bytes()
    captions = tmp_path / "original.srt"
    original_captions = "1\n00:00:00,100 --> 00:00:02,000\nOpening\n\n2\n00:01:29,000 --> 00:01:35,000\nEnding\n"
    captions.write_text(original_captions, encoding="utf-8")
    output, subtitle = video_duration.prepare_timeline(
        str(tmp_path), str(original), str(captions), seconds
    )
    with wave.open(output) as audio:
        assert audio.getnframes() / audio.getframerate() == seconds
    cues = list(moviepy_subtitles(subtitle))
    assert cues[0][0] == (0.1, min(2, seconds))
    assert all(0 <= start < end <= seconds for (start, end), _ in cues)
    assert len(cues) == (2 if seconds == 90 else 1)
    assert original.read_bytes() == original_bytes
    assert captions.read_text(encoding="utf-8") == original_captions


def test_audio_conversion_failure_is_reported(tmp_path):
    with patch.object(video_duration.voice, "fit_audio_duration", return_value=False):
        with pytest.raises(RuntimeError, match="Failed to fit narration"):
            video_duration.prepare_timeline(str(tmp_path), "missing.wav", "", 90)


@pytest.mark.parametrize("seconds", [0, 47, 90])
def test_full_pipeline_uses_selected_timeline(tmp_path, seconds):
    params = VideoParams(video_subject="History", video_source="local", video_duration=seconds,
                         bgm_type="", subtitle_enabled=False)
    with (
        patch.object(task.utils, "check_ffmpeg_ready", return_value=True),
        patch.object(task.utils, "task_dir", return_value=str(tmp_path)),
        patch.object(task, "generate_script", return_value="Human history."),
        patch.object(task, "save_script_data"),
        patch.object(task, "generate_audio", return_value=("original.wav", 8, None)),
        patch.object(task, "generate_subtitle", return_value="original.srt"),
        patch.object(task.duration_service, "prepare_timeline", return_value=("fitted.wav", "fitted.srt")) as fit,
        patch.object(task, "get_video_materials", return_value=["clip.mp4"]) as materials,
        patch.object(task, "generate_final_videos", return_value=(["final.mp4"], ["combined.mp4"], [])) as render,
        patch.object(task.upload_post.upload_post_service, "is_configured", return_value=False),
        patch.object(task.sm.state, "update_task"),
    ):
        result = task.start("duration-test", params)
    assert result["videos"] == ["final.mp4"]
    expected_duration = seconds or 8
    assert materials.call_args.args[3] == expected_duration
    assert render.call_args.args[5] == expected_duration
    assert render.call_args.args[3:5] == (("fitted.wav", "fitted.srt") if seconds else ("original.wav", "original.srt"))
    assert fit.call_count == bool(seconds)
