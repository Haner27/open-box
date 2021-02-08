from time import sleep

from open_box.redis import get_redis_client
from open_box.redis.limiter import LimitRate, LeakyBucketLimiter, TokenBucketLimiter, FixedWindowLimiter, \
    SlideWindowLimiter, SECOND

startup_nodes = [
    {'host': '<host1>', 'port': '<port1>'},
    {'host': '<host2>', 'port': '<port2>'},
    {'host': '<host3>', 'port': '<port3>'},
]
rc = get_redis_client(startup_nodes)


def test_fixed_window_limiter():
    limit_rate = LimitRate(times=2, intervals=SECOND)
    print(limit_rate)
    fixed_window_limiter = FixedWindowLimiter(rc=rc, rates=[limit_rate])
    key = '/han/api2'

    for i in range(100):
        sleep(0.3)
        print(fixed_window_limiter.limit(key))
        for limiter_key, times in fixed_window_limiter.remaining_times(key).items():
            print('times:', limiter_key, times)
        print()


def test_slide_window_limiter():
    limit_rate = LimitRate(times=5, intervals=SECOND)
    print(limit_rate)
    slide_window_limiter = SlideWindowLimiter(rc=rc, rates=[limit_rate])
    key = '/han/api2'

    for i in range(100):
        sleep(0.1)
        print(slide_window_limiter.limit(key))
        for limiter_key, times in slide_window_limiter.remaining_times(key).items():
            print('times:', limiter_key, times)
        print()


def test_leaky_bucket_limiter():
    limit_rate = LimitRate(times=5, intervals=SECOND * 10)
    print(limit_rate)
    leaky_bucket_limiter = LeakyBucketLimiter(rc=rc, rates=[limit_rate])
    key = '/han/api'

    for i in range(100):
        sleep(1)
        print(leaky_bucket_limiter.limit(key))
        for limiter_key, times in leaky_bucket_limiter.remaining_times(key).items():
            print('times:', limiter_key, times)
        print()


def test_token_bucket_limiter():
    limit_rate = LimitRate(times=5, intervals=SECOND * 10)
    print(limit_rate)
    token_bucket_limiter = TokenBucketLimiter(rc, [limit_rate])
    key = '/han/api'

    for i in range(100):
        sleep(1)
        print(token_bucket_limiter.limit(key))
        for limiter_key, times in token_bucket_limiter.remaining_times(key).items():
            print('times:', limiter_key, times)
        print()


if __name__ == '__main__':
    test_fixed_window_limiter()
    test_slide_window_limiter()
    test_leaky_bucket_limiter()
    test_token_bucket_limiter()