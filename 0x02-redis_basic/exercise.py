#!/usr/bin/env python3
"""0. Writing strings to Redis
"""
import redis
from functools import wraps
from typing import Union, Optional, Callable
import uuid


def replay(method: Callable):
    """display the history of calls of a particular function.
    """
    key = method.__qualname__
    inputs = f'{key}:inputs'
    outputs = f'{key}:outputs'

    number = method.__self__.get(key)
    input_list = method.__self__._redis.lrange(inputs, 0, -1)
    output_list = method.__self__._redis.lrange(outputs, 0, -1)

    queue = list(zip(i_list, o_list))
    print(f"{key} was called {number.decode('utf-8')} times:")
    for i, o in zip(input_list, output_list):
        print('{}(*{}) -> {}'.format(
            key,
            i.decode("utf-8"),
            o,
        ))


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


def call_history(method: Callable) -> Callable:
    """decorator to store the history of inputs and outputs
    """
    inputs = f'{method.__qualname__}:inputs'
    outputs = f'{method.__qualname__}:outputs'

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper
        """
        self._redis.rpush(inputs, str(args))
        retrieve_out = method(self, *args, **kwargs)
        self._redis.rpush(outputs, retrieve_out)
        return retrieve_out
    return wrapper


class Cache:
    """Class Cache for saving
    """
    def __init__(self):
        """initialization
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
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
