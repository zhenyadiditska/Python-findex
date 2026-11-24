
import logging
import time
from collections.abc import Callable
from functools import wraps

logger = logging.getLogger(__name__)


def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.debug(
                "%s виконано за %.2f ms",
                func.__name__,
                elapsed * 1000,
            )

    return wrapper
