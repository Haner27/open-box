from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from time import sleep

from open_box.redis import get_redis_client
from open_box.redis.locker import Locker

startup_nodes = [
    {'host': '192.168.100.52', 'port': '7000'},
    {'host': '192.168.100.52', 'port': '7001'},
    {'host': '192.168.100.52', 'port': '7002'},
]
rc = get_redis_client(startup_nodes)
locker = Locker(rc)


def func(locker_name, i):
    with locker.lock(locker_name) as loc:
        if loc:
            sleep(1)
            print('[{}]handle {}'.format(i, locker_name))
        else:
            print('[{}]miss {}'.format(i, locker_name))
            sleep(1)
            func(locker_name, i)


def test_locker():
    with ThreadPoolExecutor(max_workers=3) as exe:
        exe.map(partial(func, 'job'), [1, 2, 3])


if __name__ == '__main__':
    test_locker()
