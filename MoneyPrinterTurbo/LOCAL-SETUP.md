# Local setup

This repository preserves the MoneyPrinterTurbo source history and the local
Ollama setup. Upstream source: https://github.com/harry0703/MoneyPrinterTurbo

## Install and start

1. Install Python 3.11, uv, and Ollama.
2. From this repository directory, run `uv sync --frozen`.
3. Run `ollama pull qwen2.5:1.5b`.
4. Run `.venv\Scripts\python.exe setup_local.py` to create the local configuration.
   This command leaves an existing configuration unchanged.
5. Double-click `Start-MoneyPrinterTurbo.cmd`.

The launcher starts services in the background and opens the web interface:

- WebUI: http://127.0.0.1:8501
- API documentation: http://127.0.0.1:8080/docs
- Ollama: http://127.0.0.1:11434

Closing the browser does not stop the services. All services bind to localhost.

## Configured workflow

- Scripts and keywords: local Ollama, `qwen2.5:1.5b`.
- Footage: upload local images or downloaded video clips.
- Narration: Edge TTS; requires internet, no API key.
- Subtitles: Edge timestamps.
- Rendering: bundled imageio FFmpeg.

Configuration is stored in `config.toml`; generated videos are in `storage/tasks/`.
Logs are in `logs/`. These directories, credentials, and the virtual environment
are intentionally excluded from Git. Add footage separately through the WebUI.

The initial local setup was verified with script and keyword API calls, narration,
subtitles, H.264/AAC video exports, and the launcher health checks.
