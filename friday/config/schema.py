"""FRIDAY configuration schema and loader."""

from typing import Any, Dict

DEFAULT_CONFIG = {
    "agent": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 4096,
        "context_window": 128000,
    },
    "memory": {
        "db_path": "friday_memory.db",
        "max_chunks": 10000,
        "default_ttl_hours": 168,  # 7 days
    },
    "sync": {
        "interval_minutes": 20,
        "connectors": [],
    },
    "gateway": {
        "channels": ["telegram"],
        "web_ui": {
            "enabled": False,
            "host": "0.0.0.0",
            "port": 8080,
        },
    },
    "compression": {
        "enabled": True,
        "max_chunk_size": 3000,
        "html_to_markdown": True,
        "url_shortening": True,
    },
    "voice": {
        "enabled": False,
        "stt_provider": "whisper",
        "tts_provider": "elevenlabs",
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    },
}


def load_config(path: str = "friday.yaml") -> Dict[str, Any]:
    """Load config from YAML or return defaults."""
    try:
        import yaml
        with open(path) as f:
            user = yaml.safe_load(f)
        config = DEFAULT_CONFIG.copy()
        config.update(user)
        return config
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except ImportError:
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any], path: str = "friday.yaml"):
    """Save config to YAML."""
    import yaml
    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
