from open_box.redis import get_redis_client
from open_box.redis.cache import WrapperCache

startup_nodes = [
    {'host': '<host1>', 'port': '<port1>'},
    {'host': '<host2>', 'port': '<port2>'},
    {'host': '<host3>', 'port': '<port3>'},
]
rc = get_redis_client(startup_nodes)
cache = WrapperCache(rc)


def cache_context_usage(**kwargs):
    with cache.CacheContext(key_prefix='good', timeout=5, **kwargs) as ctx:
        if ctx.val:
            print('[from cache]{}: {}'.format(ctx.key, ctx.val))
        else:
            ctx.val = 100
            print('[to cache]{}: {}'.format(ctx.key, ctx.val))


@cache.CacheDecorator(key_prefix='hnf', timeout=5)
def cache_decorator_usage(a, b=3, *args, **kwargs):
    return {'a': a, 'b': b, 'args': args, 'kwargs': kwargs}
    # return 1
    # return datetime.now()


if __name__ == '__main__':
    cache_context_usage(name='hnf', age=28)
    print(cache_decorator_usage('lx', 299, age=28))