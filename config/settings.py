"""Configuration helpers for the report generation system."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore


@dataclass(slots=True)
class Settings:
    """Application level configuration values."""

    bailian_api_key: Optional[str] = None
    bailian_endpoint: Optional[str] = None
    bailian_model: Optional[str] = None


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Parse extremely small YAML-like ``key: value`` files."""

    result: Dict[str, Any] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def load_settings(path: str | Path | None = None) -> Settings:
    """Load configuration from YAML file and environment variables."""

    settings = Settings(
        bailian_api_key=os.getenv("BAILIAN_API_KEY"),
        bailian_endpoint=os.getenv("BAILIAN_ENDPOINT"),
        bailian_model=os.getenv("BAILIAN_MODEL"),
    )

    if path is None:
        path = Path("config/config.yml")
    else:
        path = Path(path)

    if path.exists():
        text = path.read_text(encoding="utf-8")
        data: Dict[str, Any]
        if yaml is not None:
            data = yaml.safe_load(text) or {}
        else:
            data = _parse_simple_yaml(text)
        bailian_data = data.get("bailian", {})
        if isinstance(bailian_data, dict):
            settings.bailian_api_key = bailian_data.get("api_key", settings.bailian_api_key)
            settings.bailian_endpoint = bailian_data.get("endpoint", settings.bailian_endpoint)
            settings.bailian_model = bailian_data.get("model", settings.bailian_model)

    return settings
