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
            # 设置val的值，防止任务超时后执行完任务，finally删除当前正在被锁住的任务的key
            # 使用lua脚本，原子化get and del 操作，避免任务执行完删除别人任务的锁的情况
            self.__rc.eval(self.LOCKER_RELEASE_LOCAL_LUA_SCRIPT, 1, locker_key, value)
