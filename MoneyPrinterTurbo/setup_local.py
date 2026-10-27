from pathlib import Path

import toml

path = Path(__file__).parent / "config.toml"
if path.exists():
    raise SystemExit("Configuration already exists; leaving it unchanged.")
config = toml.load(path.with_name("config.example.toml"))
config["listen_host"] = "127.0.0.1"
config["app"].update(
    llm_provider="ollama",
    ollama_base_url="http://127.0.0.1:11434/v1",
    ollama_model_name="qwen2.5:1.5b",
    video_source="local",
    subtitle_provider="edge",
    max_concurrent_tasks=1,
)
config["ui"].update(
    language="en",
    video_language="en",
    voice_name="en-US-AriaNeural-Female",
    tts_server="azure-tts-v1",
    voice_mode="tts",
    bgm_type="",
    open_task_folder_on_completion=False,
)
path.write_text(toml.dumps(config), encoding="utf-8")
print("Configured Ollama, local footage, Edge TTS, and English UI.")
