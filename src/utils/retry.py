import time
from functools import wraps
from typing import Callable, Type

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator per retry con exponential backoff"""
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= backoff_factor
                        print(f"⚠️ Retry {attempt + 1}/{max_retries} dopo {delay:.1f}s...")
                    else:
                        raise last_exception
            
        return wrapper
    return decorator
