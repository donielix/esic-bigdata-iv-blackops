import json
from pathlib import Path
from typing import Any, Dict, Union


def save_json(obj: Dict[str, Any], path: Union[str, Path], **kwargs) -> None:
    """
    Save a Python object to a JSON file. If the specified path doesn't exist,
    it will be created.
    """
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as file:
        json.dump(obj, file, ensure_ascii=False, **kwargs)
