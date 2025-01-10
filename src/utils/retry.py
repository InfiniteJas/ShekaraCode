# src/utils/retry.py
from functools import wraps
from typing import Callable, Any
import asyncio
from ..utils.logging import get_logger

logger = get_logger(__name__)

def async_retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            delay_time = delay
            
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{retries} failed: {str(e)}"
                    )
                    if attempt < retries - 1:
                        await asyncio.sleep(delay_time)
                        delay_time *= backoff
                        
            raise last_exception
            
        return wrapper
    return decorator