from contextlib import contextmanager

from bson import ObjectId
from rediscluster import RedisCluster


class Locker:
    LOCKER_RELEASE_LOCAL_LUA_SCRIPT = """
        if redis.call('get', KEYS[1]) == ARGV[1]
            then
                return redis.call('del', KEYS[1])
            else
                return 0
        end
    """

    def __init__(self, rc: RedisCluster):
        self.__rc = rc

    @contextmanager
    def lock(self, key, timeout=10):
        """
        :param key: lock_name
        :param timeout: timeout
        :return:
        """

        locker_key = 'LOCKER::{0}'.format(key)
        value = str(ObjectId())
        try:
            yield self.__rc.set(locker_key, value, nx=True, ex=timeout)
        finally:
            self.__rc.eval(self.LOCKER_RELEASE_LOCAL_LUA_SCRIPT, 1, locker_key, value)
