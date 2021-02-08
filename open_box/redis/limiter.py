import abc
from typing import List

from rediscluster import RedisCluster

from open_box.datetime import timestamp

SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
MONTH = DAY * 30
YEAR = DAY * 365


class LimitRate:
    def __init__(self, intervals: int, times: int):
        """
        :param intervals: durations, seconds
        :param times: hit count
        """
        self.__times = times
        self.__intervals = intervals
        self.__rate = self.cal_rate(times, intervals)

    @property
    def times(self):
        return self.__times

    @property
    def intervals(self):
        return self.__intervals

    @property
    def rate(self):
        return self.__rate

    def __str__(self):
        return '<LimitRate: {} times/s>'.format(self.__rate)

    @staticmethod
    def cal_rate(times: int, intervals: int):
        if intervals == 0:
            return times
        return times / intervals

    def __mul__(self, other):
        return self.__rate * other


class Limiter(metaclass=abc.ABCMeta):
    def __init__(self, rc: RedisCluster, rates: List[LimitRate]):
        self.__rc = rc
        self.__rates = rates
        self.__limiter_key_map = {}

    @property
    def rc(self):
        return self.__rc

    @property
    def rates(self):
        return self.__rates

    def get_limiter_keys(self, key: str) -> List[str]:
        return self.__limiter_key_map.get(key, [])

    def set_limiter_keys(self, key: str, limiter_key):
        if key not in self.__limiter_key_map:
            self.__limiter_key_map[key] = []

        if limiter_key not in self.__limiter_key_map[key]:
            self.__limiter_key_map[key].append(limiter_key)

    def clear(self, key: str):
        for limiter_key in self.__limiter_key_map.get(key, []):
            self.__rc.delete(limiter_key)

    @abc.abstractmethod
    def build_limiter_key(self, key: str, rate: LimitRate) -> str:
        pass

    @abc.abstractmethod
    def limit(self, key: str) -> bool:
        pass

    @abc.abstractmethod
    def remaining_times(self, key: str):
        pass


class FixedWindowLimiter(Limiter):
    """fixed window limiter"""
    LIMITER_LUA_SCRIPT = '''
        local key = KEYS[1]
        local times = tonumber(ARGV[1])
        local timeout = tonumber(ARGV[2])     
        
        if redis.call('EXISTS', key) == 0 then
            redis.call('SET', key, 0, 'EX', timeout)
        end
        
        local count = tonumber(redis.call('GET', key))
        if count < times then
            redis.call('INCR', key)
            return 1
        else
            return 0
        end
    '''

    def build_limiter_key(self, key: str, rate: LimitRate) -> str:
        limiter_key = 'FWL:{}/{}/{}'.format(key, rate.intervals, rate.times)
        self.set_limiter_keys(key, limiter_key)
        return limiter_key

    def limit(self, key: str):
        for rate in self.rates:
            limiter_key = self.build_limiter_key(key, rate)
            code = self.rc.eval(self.LIMITER_LUA_SCRIPT, 1, limiter_key, rate.times, rate.intervals)
            if not code:
                return False
        return True

    def remaining_times(self, key: str):
        rt = {}
        for limiter_key in self.get_limiter_keys(key):
            current_times = self.rc.get(limiter_key) or 0
            rt[limiter_key] = current_times
        return rt

    def remaining_seconds(self, key: str):
        rs = {}
        for limiter_key in self.get_limiter_keys(key):
            ttl = self.rc.ttl(limiter_key) or 0
            rs[limiter_key] = ttl
        return rs


class SlideWindowLimiter(Limiter):
    """slide window limiter"""
    LIMITER_LUA_SCRIPT = '''
        local key = KEYS[1]
        local currentTimestamp = tonumber(ARGV[1])
        local times = tonumber(ARGV[2])
        local intervals = tonumber(ARGV[3])
        
        local spanFirst = currentTimestamp - intervals * 1000
        redis.call('ZREMRANGEBYSCORE', key, 0, spanFirst)
        redis.call('ZADD', key, currentTimestamp, currentTimestamp)
        if redis.call('ZCOUNT', key, spanFirst, currentTimestamp) > times then
            return 0
        else
            return 1
        end 
    '''

    def build_limiter_key(self, key: str, rate: LimitRate) -> str:
        limiter_key = 'SWL:{}/{}/{}'.format(key, rate.intervals, rate.times)
        self.set_limiter_keys(key, limiter_key)
        return limiter_key

    def limit(self, key: str):
        current_timestamp = int(timestamp() * 1000)
        for rate in self.rates:
            limiter_key = self.build_limiter_key(key, rate)
            code = self.rc.eval(self.LIMITER_LUA_SCRIPT, 1, limiter_key, current_timestamp, rate.times, rate.intervals)
            if not code:
                return False
        return True

    def remaining_times(self, key: str):
        rt = {}
        for limiter_key in self.get_limiter_keys(key):
            current_timestamp = int(timestamp() * 1000)
            current_times = self.rc.zcount(limiter_key, 0, current_timestamp) or 0
            rt[limiter_key] = current_times
        return rt


class LeakyBucketLimiter(Limiter):
    """leaky limiter"""
    LIMITER_LUA_SCRIPT = '''
        local key = KEYS[1]
        local currentTimestamp = tonumber(ARGV[1])
        local times = tonumber(ARGV[2])
        local intervals = tonumber(ARGV[3])
        local rate = times / (intervals * 1000)
        local lastTimeKey = 'lastTime'
        local currentTokenKey = 'currentToken'
        local lastTime = tonumber(redis.call('HGET', key, lastTimeKey))
        local currentToken = tonumber(redis.call('HGET', key, currentTokenKey))
    
        if lastTime then
        else
            lastTime = currentTimestamp
        end
    
        if currentToken then
        else
            currentToken = 0
        end
    
        local deltaToken = (currentTimestamp - lastTime) * rate
        currentToken = currentToken - deltaToken
        if currentToken < 0 then
            currentToken = 0
        end
    
        if currentToken + 1 < times then
            currentToken = currentToken + 1
            redis.call('HSET', key, lastTimeKey, currentTimestamp)
            redis.call('HSET', key, currentTokenKey, currentToken)
            return 1
        else
            return 0
        end
    '''

    def build_limiter_key(self, key: str, rate: LimitRate) -> str:
        limiter_key = 'LBL:{}/{}/{}'.format(key, rate.intervals, rate.times)
        self.set_limiter_keys(key, limiter_key)
        return limiter_key

    def limit(self, key: str):
        current_timestamp = int(timestamp() * 1000)
        for rate in self.rates:
            limiter_key = self.build_limiter_key(key, rate)
            code = self.rc.eval(self.LIMITER_LUA_SCRIPT, 1, limiter_key, current_timestamp, rate.times, rate.intervals)
            if not code:
                return False
        return True

    def remaining_times(self, key: str):
        rt = {}
        for limiter_key in self.get_limiter_keys(key):
            current_times = self.rc.hget(limiter_key, 'currentToken') or 0
            rt[limiter_key] = current_times
        return rt


class TokenBucketLimiter(Limiter):
    """token limiter"""

    LIMITER_LUA_SCRIPT = '''
        local key = KEYS[1]
        local currentTimestamp = tonumber(ARGV[1])
        local times = tonumber(ARGV[2])
        local intervals = tonumber(ARGV[3])
        local rate = times / (intervals * 1000)
        local lastTimeKey = 'lastTime'
        local currentTokenKey = 'currentToken'
        local lastTime = tonumber(redis.call('HGET', key, lastTimeKey))
        local currentToken = tonumber(redis.call('HGET', key, currentTokenKey))
    
        if lastTime then
        else
            lastTime = currentTimestamp
        end
    
        if currentToken then
        else
            currentToken = times
        end
    
        local deltaToken = (currentTimestamp - lastTime) * rate
        currentToken = currentToken + deltaToken
        if currentToken > times then
            currentToken = times
        end
    
        if currentToken - 1 > 0 then
            currentToken = currentToken - 1
            redis.call('HSET', key, lastTimeKey, currentTimestamp)
            redis.call('HSET', key, currentTokenKey, currentToken)
            return 1
        else
            return 0
        end
    '''

    def build_limiter_key(self, key: str, rate: LimitRate) -> str:
        limiter_key = 'TBL:{}/{}/{}'.format(key, rate.intervals, rate.times)
        self.set_limiter_keys(key, limiter_key)
        return limiter_key

    def limit(self, key: str):
        current_timestamp = int(timestamp() * 1000)
        for rate in self.rates:
            limiter_key = self.build_limiter_key(key, rate)
            code = self.rc.eval(self.LIMITER_LUA_SCRIPT, 1, limiter_key, current_timestamp, rate.times, rate.intervals)
            if not code:
                return False
        return True

    def remaining_times(self, key: str):
        rt = {}
        for limiter_key in self.get_limiter_keys(key):
            current_times = self.rc.hget(limiter_key, 'currentToken') or 0
            rt[limiter_key] = current_times
        return rt
