from functools import wraps
from typing import Callable
from warnings import warn


def retry_n_times(n: int = 1) -> Callable:

    def outer(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for trial in range(n):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    warn(f"Error during trial {trial+1}:\n{e}")
                    continue
            raise Exception(f"Function didn't return after {n} trials")

        return wrapper

    return outer
