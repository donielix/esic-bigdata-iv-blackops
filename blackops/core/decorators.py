from functools import wraps
from typing import Callable


def retry_n_times(n: int = 1, exception=Exception) -> Callable:

    def outer(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for trial in range(n):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    exc = e
                    print(f"Error during trial {trial+1}:\n{e}")
                    continue
            raise Exception(f"Function didn't return after {n} trials: {exc}") from None

        return wrapper

    return outer
