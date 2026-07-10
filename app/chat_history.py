from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_chat_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(content, list):
        return []
    return [item for item in content if isinstance(item, dict)]


def save_chat_history(path: Path, messages: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def clear_chat_history(path: Path) -> None:
    if path.exists():
        path.unlink()
