"""Small, explicit configuration surface for the desktop app."""

import json
import os
import sys
from typing import Any


def get_app_dir() -> str:
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(get_app_dir(), "config.json")

DEFAULT_CONFIG = {
    "output_dir": "music",
    "audio_format": "mp3",
    "parallel_downloads": 3,
    "enable_metadata_embedding": True,
    "enable_musicbrainz_lookup": True,
    "ytdlp_path": "",
    "ffmpeg_path": "",
    "ytdlp_extra_args": "",
}

CONFIG_SCHEMA = {
    "output_dir": {"type": str},
    "audio_format": {"type": str, "choices": {"mp3", "m4a", "flac", "aac", "ogg", "wav"}},
    "parallel_downloads": {"type": int, "min": 1, "max": 8},
    "enable_metadata_embedding": {"type": bool},
    "enable_musicbrainz_lookup": {"type": bool},
    "ytdlp_path": {"type": str},
    "ffmpeg_path": {"type": str},
    "ytdlp_extra_args": {"type": str},
}


def load_config() -> dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config file {CONFIG_PATH} not found.")
    with open(CONFIG_PATH, encoding="utf-8") as file:
        stored = json.load(file)
    return {**DEFAULT_CONFIG, **{key: stored[key] for key in DEFAULT_CONFIG if key in stored}}


def save_config(config: dict[str, Any]) -> bool:
    clean_config = {key: config[key] for key in DEFAULT_CONFIG if key in config}
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(clean_config, file, indent=2)
        file.write("\n")
    return True


def validate_config(config: dict[str, Any]) -> tuple[bool, list[str]]:
    errors = []
    for key, rules in CONFIG_SCHEMA.items():
        value = config.get(key)
        if not isinstance(value, rules["type"]):
            errors.append(f"{key} must be a {rules['type'].__name__}.")
            continue
        if "choices" in rules and value not in rules["choices"]:
            errors.append(f"{key} must be one of: {', '.join(sorted(rules['choices']))}.")
        if ("min" in rules and value < rules["min"]) or ("max" in rules and value > rules["max"]):
            errors.append(f"{key} is outside the allowed range.")
    return not errors, errors


def reset_to_defaults() -> tuple[bool, str]:
    save_config(DEFAULT_CONFIG)
    return True, "Settings reset."


def get_config_value(key: str, default: Any = None) -> Any:
    return load_config().get(key, default)
