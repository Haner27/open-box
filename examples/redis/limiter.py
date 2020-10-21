from time import sleep

from open_box.redis.limiter import LeakyBucketLimiter, TokenBucketLimiter
from open_box.redis.limiter.rate import LimitRate, SECOND


def test_leaky_bucket_limiter():
    limit_rate = LimitRate(times=5, intervals=SECOND)
    print(limit_rate)
    leaky_bucket_limiter = LeakyBucketLimiter(5, limit_rate)
    key = 'han.api'

    for i in range(100):
        sleep(0.1)
        print(i, leaky_bucket_limiter.acquire(key, 1), leaky_bucket_limiter.current_tokens)


def test_token_bucket_limiter():
    limit_rate = LimitRate(times=10, intervals=SECOND * 86400)
    print(limit_rate)
    token_bucket_limiter = TokenBucketLimiter(5, limit_rate)
    key = 'han.api'

    for i in range(100):
        sleep(0.1)
        print(i, token_bucket_limiter.acquire(key, 1), token_bucket_limiter.current_tokens)


if __name__ == '__main__':
    # test_leaky_bucket_limiter()
    test_token_bucket_limiter()