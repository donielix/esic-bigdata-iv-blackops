from typing import Any, Dict

import requests

from blackops.core.decorators import retry_n_times
from blackops.crawlers.wallapop.config import LATITUDE, LONGITUDE, WALLAPOP_API_URL


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
        url=WALLAPOP_API_URL,
        params={
            "keywords": product,
            "source": "search_box",
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "show_multiple_sections": "true",
        },
        headers={"X-DeviceOS": "0"},
    ) as req:
        req.raise_for_status()
        data = req.json()

    return data
