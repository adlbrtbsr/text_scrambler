import os
import logging
from typing import List, Optional


_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}

logger = logging.getLogger(__name__)


def get_str(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in _TRUTHY:
        return True
    if value in _FALSY:
        return False
    return default


def get_int(name: str, default: int = 0) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        logger.error(
            "Invalid int for env var %s=%r; using default %s", name, raw, default, exc_info=True
        )
        return default


def get_list(name: str, default: Optional[List[str]] = None, sep: str = ",") -> List[str]:
    raw = os.getenv(name)
    if not raw:
        return list(default or [])
    return [item.strip() for item in raw.split(sep) if item.strip()]


