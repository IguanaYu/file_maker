"""访问业务数据结构的实用工具。"""
from __future__ import annotations

from typing import Any, Dict


def resolve_data_path(context: Dict[str, Any], path: str) -> Any:
    """根据点号路径（如 ``device.name``）从上下文中取值，任一层缺失则返回 ``None``。"""

    current: Any = context
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def resolve_bindings(context: Dict[str, Any], bindings: Dict[str, str]) -> Dict[str, Any]:
    """根据绑定配置批量解析数据路径，返回占位符到实际值的映射。"""

    return {placeholder: resolve_data_path(context, path) for placeholder, path in bindings.items()}
