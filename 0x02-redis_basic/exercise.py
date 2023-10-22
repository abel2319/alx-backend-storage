#!/usr/bin/env python3
"""0. Writing strings to Redis
"""
import redis
from functools import wraps
from typing import Union, Optional, Callable
import uuid


    
def count_calls(method: Callable) -> Callable:
    """Decorator to count the number call of methods
    """
    key = method.__qualname__
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper function
        """
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

class Cache:
    """Class Cache for saving
    """
    def __init__(self):
        """initialization
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data to redis data base
        with an uuid as key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self,
            key: str,
            fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float]:
        """Get method for cache
        """
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_int(data: bytes) -> int:
        """convert byte to integer
        """
        return int.from_bytes(data)

    def get_str(self, data: bytes) -> str:
        """convert byte to string
        """
        return data.decode('utf-8')

