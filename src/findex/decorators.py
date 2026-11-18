import time
from functools import wraps


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            print(
                f"[timed] {func.__name__}: "
                f"{elapsed * 1000:.2f} ms"
            )

    return wrapper
