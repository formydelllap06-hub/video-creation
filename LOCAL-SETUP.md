# MoneyPrinterTurbo local setup

Double-click `Start-MoneyPrinterTurbo.cmd` to start Ollama, the WebUI, and the API.
The services run in the background. Closing the browser does not stop them.

- WebUI: http://127.0.0.1:8501
- API documentation: http://127.0.0.1:8080/docs
- Source checkout: `MoneyPrinterTurbo/`
- Configuration: `MoneyPrinterTurbo/config.toml` (ignored by Git)
- Generated videos: `MoneyPrinterTurbo/storage/tasks/`
- Logs: `MoneyPrinterTurbo/logs/`

The configured script model is `qwen2.5:1.5b` through local Ollama at
`http://127.0.0.1:11434/v1`. It is a small model selected for this laptop's
8 GB RAM and 4 GB GPU. Larger models can produce better scripts but need more memory.

To create a video:

1. Enter a topic and generate the script, or paste your own script.
2. With Video Source set to Local file, upload your images or video clips.
3. Keep Edge TTS for free narration, then select Generate Video.

For automatic stock-footage searches, add your own Pexels or Pixabay API key in
Settings and change Video Source accordingly. Ollama generates scripts and search
keywords; it does not generate the footage. Edge TTS requires internet access,
although it needs no API key. No paid provider is configured.

Dependencies were installed from the repository's locked environment using
`uv sync --frozen` with Python 3.11. The bundled imageio FFmpeg is used for rendering.
All three services listen on localhost.

The file `storage/local_videos/setup-test-pattern.mp4` inside the repository is
synthetic test footage used to verify rendering, not a stock-footage example.

A real web-sourced sample is available at
`MoneyPrinterTurbo/storage/local_videos/nasa-earth-rotation.webm`.
Upload it under Local file to try the app without a stock-footage API key.
Its source and credit are recorded in the adjacent `SOURCES.md`.
Direct downloadable video links can also be saved and uploaded using this workflow.

Verified during setup: WebUI loads, API responds, dependency compatibility passes,
Ollama generates scripts and keyword lists through the app API, and FFmpeg exports
H.264/AAC video with Edge narration and burned-in subtitles. Ollama reports the
Qwen model running entirely on the NVIDIA GPU.

Sample outputs:

- NASA Earth clip with a Qwen-generated script:
  `MoneyPrinterTurbo/storage/tasks/bfa221fa-cca1-4e14-8fee-fec4493596cd/final-1.mp4`
- Synthetic rendering check:
  `MoneyPrinterTurbo/storage/tasks/6c9c0b64-b1a9-4ea7-806d-f314ef4bcbb6/final-1.mp4`
