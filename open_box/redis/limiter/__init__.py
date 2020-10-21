from abc import ABCMeta, abstractmethod
from threading import Lock
from time import time

from .rate import LimitRate


class Storage(metaclass=ABCMeta):
    @abstractmethod
    def set(self, key, name, value):
        pass

    @abstractmethod
    def get(self, key, name):
        pass


class MemoryStorage(Storage):
    def __init__(self):
        self.__data = {}

    def set(self, key, name, value):
        if key not in self.__data:
            self.__data[key] = {}
        self.__data[key][name] = value

    def get(self, key, name):
        return self.__data.get(key, {}).get(name)


class Limiter(metaclass=ABCMeta):
    @abstractmethod
    def get_current_token(self):
        pass

    @abstractmethod
    def acquire(self, key: str, tokens: int):
        pass


def synchronized(func):
    def _wrapper(*args, **kwargs):
        with Lock():
            return func(*args, **kwargs)
    return _wrapper


class LeakyBucketLimiter(Limiter):
    """漏桶限流器"""
    def __init__(self, capacity: int, rate: LimitRate):
        self.__capacity = capacity
        self.__rate = rate
        self.__last_time = 0
        self.__current_tokens = 0

    @property
    def capacity(self):
        return self.__capacity

    @property
    def rate(self):
        return self.__rate

    @property
    def last_time(self):
        return self.__last_time

    @property
    def current_tokens(self):
        return self.__current_tokens

    @staticmethod
    def timestamp():
        """时间戳:单位毫秒"""
        return int(time() * 1000)

    def set_last_time(self, last_time):
        self.__last_time = last_time

    def set_current_tokens(self, current_tokens):
        self.__current_tokens = current_tokens

    def get_current_token(self):
        timestamp = self.timestamp()
        delta = self.rate * (timestamp - self.last_time)
        self.set_current_tokens(max(0, self.current_tokens - delta))
        self.set_last_time(timestamp)
        return self.current_tokens

    @synchronized
    def acquire(self, key: str, tokens: int):
        current_tokens = self.get_current_token()
        if current_tokens + tokens <= self.capacity:
            self.set_current_tokens(current_tokens + tokens)
            return True
        else:
            return False


class TokenBucketLimiter(Limiter):
    """令牌桶限流器"""

    def __init__(self, capacity: int, rate: LimitRate):
        self.__capacity = capacity
        self.__rate = rate
        self.__last_time = 0
        self.__current_tokens = 0

    @property
    def capacity(self):
        return self.__capacity

    @property
    def rate(self):
        return self.__rate

    @property
    def last_time(self):
        return self.__last_time

    @property
    def current_tokens(self):
        return self.__current_tokens

    @staticmethod
    def timestamp():
        """时间戳:单位毫秒"""
        return int(time() * 1000)

    def set_last_time(self, last_time):
        self.__last_time = last_time

    def set_current_tokens(self, current_tokens):
        self.__current_tokens = current_tokens

    def get_current_token(self):
        timestamp = self.timestamp()
        delta = self.rate * (timestamp - self.last_time)
        self.set_current_tokens(min(self.current_tokens + delta, self.capacity))
        self.set_last_time(timestamp)
        return self.current_tokens

    @synchronized
    def acquire(self, key: str, tokens: int):
        current_tokens = self.get_current_token()
        if  tokens <= current_tokens:
            self.set_current_tokens(current_tokens - tokens)
            return True
        else:
            return False
