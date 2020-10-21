from time import sleep

from open_box.redis import get_redis_client

startup_nodes = [
    {'host': '192.168.100.52', 'port': '7000'},
    {'host': '192.168.100.52', 'port': '7001'},
    {'host': '192.168.100.52', 'port': '7002'},
]


def redis_basic():
    rc = get_redis_client(startup_nodes)

    print(rc.set('hnf', 100, 3))
    print(rc.get('hnf') == 100)
    print(rc.set('hnf', 20, 3))
    sleep(3)
    print(rc.get('hnf') == 3)


if __name__ == '__main__':
    redis_basic()
    from uuid import uuid4
    a = uuid4()
    print(str(a), type(str(a)))