from functools import wraps
from time import sleep

from ..log import Logger

retry_logger = Logger('retry')


class OverRetryError(Exception):
    def __init__(self, msg=''):
        self.message = 'OverRetryException: {}'.format(msg)

    def __str__(self):
        return self.message


class RetryError(Exception):
    def __init__(self, msg=''):
        self.message = 'RetryError: {}'.format(msg)

    def __str__(self):
        return self.message


def retry(attempts: int = 3, interval: int = 0):
    """
    重试装饰器

    :param attempts: 重试次数
    :param interval: 重试间隔
    :return:
    """

    def wrapper(func):
        @wraps(func)
        def deco(*args, **kwargs):
            last_ex = None
            for i in range(attempts if attempts > 1 else 1):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    last_ex = ex
                    retry_logger.info('{} attempt failed. error: {}'.format(i + 1, ex))
                    if interval:
                        sleep(interval)
            raise OverRetryError(
                'Over {} attempts to retry {}. Error: {}'.format(
                    attempts,
                    func.__name__,
                    last_ex,
                )
            )

        return deco

    return wrapper
