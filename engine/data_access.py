"""Utility helpers for accessing context data structures."""
from __future__ import annotations

from typing import Any, Dict


def resolve_data_path(context: Dict[str, Any], path: str) -> Any:
    """Resolve a dotted path from the provided context data.

    Parameters
    ----------
    context:
        The hierarchical data structure storing business information.
    path:
        Dotted path (e.g., ``"device.name"``) to be resolved.

    Returns
    -------
    Any
        The value found at the path, or ``None`` if any part of the
        path is missing.
    """

    current: Any = context
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def resolve_bindings(context: Dict[str, Any], bindings: Dict[str, str]) -> Dict[str, Any]:
    """Return a dictionary mapping placeholder names to resolved values."""

    return {placeholder: resolve_data_path(context, path) for placeholder, path in bindings.items()}
