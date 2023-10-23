import os
from typing import Any, Optional, List, Dict
from pathlib import Path

from tosser.types import TossPathT
from tosser.exceptions import TosserException

def resolve_config(env_var: str, val: Any, default: Any) -> Any:
    """Resolve a configuration value using passed value, environment variable, and default"""

    # (default -> env -> arg)
    if val is not None:
        return val
    test_env = os.getenv(env_var)
    if test_env is not None:
        return test_env
    return default


def resolve_path_ref(path: TossPathT, check: bool = True) -> Optional[Path]:
    """Resolve a TossPathT to a Path object"""

    if path is None:
        raise TosserException('Cannot resolve path ref that is None')
    if check and not os.path.exists(path):
        raise TosserException(f'Path does not exist: {str(path)}')
    if not os.path.exists(path):
        return None
    if isinstance(path, str):
        return Path(path)
    return path


def get_field(
        obj: Dict[str, Any], 
        field: str, 
        path: Optional[List[str]] = None, 
        alias: Optional[List[str]] = None,
        optional: bool = True,
        default: Optional[Any] = None
    ):
    """Get a field from a dictionary using case insensitive keys"""

    if path is not None and len(path) > 0:
        obj = get_field(obj, path[0], path[1:] if len(path) > 1 else None)
    fields = [field.lower()] + (alias if alias is not None else [])
    for k in obj.keys():
        if any([field == k.lower() for field in fields]):
            return obj[k]
    else:
        if not optional:
            raise TosserException(f'Field not found: {field}')
        return default
    