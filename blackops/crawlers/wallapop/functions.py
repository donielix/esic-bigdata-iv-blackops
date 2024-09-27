import json
from pathlib import Path
from typing import Any, Dict, Union

import requests

from blackops.core.decorators import retry_n_times
from blackops.crawlers.wallapop.config import WALLAPOP_API_URL


@retry_n_times(n=3)
def fetch_api(product: str) -> Dict[str, Any]:
    """
    Retrieve data from Wallapop API.

    Params
    ------
    `product`: `str`
        The product we want to search for

    Returns
    -------
    `Dict`:
        The raw response JSON data from the API.
    """
    with requests.get(
        url=WALLAPOP_API_URL, params={"keywords": product, "source": "search_box"}
    ) as req:
        req.raise_for_status()
        data = req.json()

    return data


def save_json(obj: Dict[str, Any], path: Union[str, Path], **kwargs) -> None:
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as file:
        json.dump(obj, file, ensure_ascii=False, **kwargs)
