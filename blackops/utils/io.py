import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import requests

from blackops.core.decorators import retry_n_times


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


def _to_clean_http_url(url: str) -> str:
    return "http://" + url.strip().removeprefix("https://").removeprefix(
        "http://"
    ).removesuffix("/")


@retry_n_times(n=5, exception=requests.RequestException)
def get_token(url: str, username: str, password: str) -> str:
    """
    Retrives a Token for using in future requests.

    Parameters
    ----------
    `url`: `str`
        The URL endpoint for login. Ex: "http://example.com/api/login"
    `username`: `str`
        The username that we want to login as.
    `password`: `str`
        The user's corresponding password.

    Returns
    -------
    `token`: `str`
        The token to use in future requests. (Ex: "eyJ1c2VybmFtZSI6ImVzaWMifQ.Zvxd2Q.RvF3YjXO34LTDuglifmTsvKxGG4")
    """
    url = _to_clean_http_url(url)
    req = requests.post(url, json=dict(username=username, password=password))
    req.raise_for_status()
    return req.json()["token"]


@retry_n_times(n=5, exception=requests.RequestException)
def get_api_data(url: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch data from a specified API endpoint, optionally using an authorization token.

    This function makes a GET request to the provided `url`. If a token is provided, it
    will be included in the request headers for authentication purposes. The function
    retries the request up to 5 times in case of a `requests.RequestException`.

    Parameters
    ----------
    `url`: `str`
        The API endpoint URL to send the GET request to.
    `token`: `Optional[str]`, default `None`
        The authorization token to include in the request headers. If `None`, no
        authorization will be used.

    Returns
    -------
    `Dict`
        A Python dictionary with the response data from the endpoint.

    Example
    -------
    >>> get_api_data("http://example.com/api/data", token="your_token_here")
    {
        "data": [
            {
                "key": "value"
            }
        ]
    }
    """
    url = _to_clean_http_url(url)
    headers = dict(Authorization=f"Bearer {token}") if token else None
    return requests.get(url, headers=headers).json()
