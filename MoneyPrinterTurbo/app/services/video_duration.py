"""Build a bounded video timeline without modifying user-supplied media."""

import os
from pathlib import Path

from app.models.const import MAX_VIDEO_DURATION
from app.services import voice
from app.utils.subtitle_reader import moviepy_subtitles
from app.utils.subtitle_writer import staged_subtitle_file


def _timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def prepare_timeline(task_dir: str, audio_file: str, subtitle_path: str, seconds: int):
    """Keep timing intact, pad/trim narration, and clip captions to the export."""
    if not 1 <= seconds <= MAX_VIDEO_DURATION:
        raise ValueError(f"video duration must be between 1 and {MAX_VIDEO_DURATION}")
    output_audio = str(Path(task_dir) / "video-audio.wav")
    if not voice.fit_audio_duration(audio_file, output_audio, seconds):
        raise RuntimeError("Failed to fit narration to the selected video duration")

    output_subtitles = ""
    if subtitle_path and os.path.isfile(subtitle_path):
        cues = []
        for (start, end), text in moviepy_subtitles(subtitle_path):
            start, end = max(0, start), min(seconds, end)
            if end > start:
                cues.append(f"{len(cues) + 1}\n{_timestamp(start)} --> {_timestamp(end)}\n{text}\n")
        if cues:
            output_subtitles = str(Path(task_dir) / "video-subtitles.srt")
            with staged_subtitle_file(output_subtitles) as staged:
                Path(staged).write_text("\n".join(cues) + "\n", encoding="utf-8")
                os.replace(staged, output_subtitles)
    return output_audio, output_subtitles
