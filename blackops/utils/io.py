import json
from pathlib import Path
from typing import Any, Dict, Union


def save_json(obj: Dict[str, Any], path: Union[str, Path], **kwargs) -> None:
    """
    Save a Python object to a JSON file. If the specified path doesn't exist,
    it will be created.

    Parameters
    ----------
    `obj`: `Dict[str, Any]`
        The corresponding Python object (dict or list) what we want to save as a JSON
        file
    `path`: `Union[str, Path]`
        The path where the JSON file will be saved.

    Example
    -------
    >>> obj = {"name": "Marta", "age": 32}
    >>> save_json(obj=obj, "data/users.json")
    """
    kwargs.setdefault("indent", 4)
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as file:
        json.dump(obj, file, ensure_ascii=False, **kwargs)
