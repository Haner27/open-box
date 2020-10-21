from time import sleep

from open_box.redis import get_redis_client

startup_nodes = [
    {'host': '<host1>', 'port': '<port1>'},
    {'host': '<host2>', 'port': '<port2>'},
    {'host': '<host3>', 'port': '<port3>'},
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