import inspect
import json
from functools import wraps, partial
from logging import INFO

from rediscluster import RedisCluster

from open_box.log import Logger
from open_box.log.formatter import DEFAULT_TEXT_FORMAT

cache_logger = Logger('cache', level=INFO, formatter=DEFAULT_TEXT_FORMAT)


def check_params(params):
    if not isinstance(params, (int, float, list, dict, str, tuple, bool, type(None))):
        cache_logger.warning('build key failed: {}'.format('{}({}), is not JSON serializable'.format(params, type(params))))
        return False

    if isinstance(params, dict):
        for k, v in params.items():
            code = check_params(v)
            if not code:
                return False

    if isinstance(params, list):
        for param in params:
            code = check_params(param)
            if not code:
                return False
    return True


def json_result(result):
    if not result:
        return result
    try:
        return json.dumps(result, ensure_ascii=False)
    except Exception as ex:
        cache_logger.warning('cache result failed: {}'.format(ex))
        return None


def build_key(key_prefix, params, func_name=None):
    kv_pairs = []
    for k, v in sorted(params.items(), key=lambda a: a[0]):
        val = v
        if isinstance(v, (list, tuple)):
            val = ','.join([str(i) for i in v])
        kv_pairs.append('{}={}'.format(k, val))
    if func_name:
        key = '{}::{}::{}'.format(key_prefix, func_name, '&'.join(kv_pairs))
    else:
        key = '{}::{}'.format(key_prefix, '&'.join(kv_pairs))
    return key


class CacheContext:
    def __init__(self, rc: RedisCluster, key_prefix: str, timeout: int = 600, **params):
        self.__rc = rc
        self.__params = params
        self.__key_prefix = key_prefix
        self.__key = None
        self.val = None
        self.__timeout = timeout
        self.__exist_val = False

    @property
    def key(self):
        return self.__key

    @property
    def key_prefix(self):
        return self.__key_prefix

    def __enter__(self):
        code = check_params(self.__params)
        if code:
            self.__key = build_key(self.__key_prefix, self.__params)
            result_str = self.__rc.get(self.__key)
            if result_str is not None:
                self.val = json.loads(result_str)
                self.__exist_val = True
                cache_logger.info("GET: 【{}】【{}】".format(self.__key, result_str))
            else:
                self.val = None
                self.__exist_val = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            cache_logger.error('cache value failed: {}'.format(exc_val))
            return True
        if self.__key and self.val is not None and not self.__exist_val:
            result_str = json_result(self.val)
            if result_str:
                self.__rc.set(self.__key, result_str, self.__timeout)
                cache_logger.info("SET: 【{}】【{}】".format(self.__key, result_str))
        return True


def load_params(func, *args, **kwargs):
    var_positional_key = None
    positional_or_keyword_keys = []
    keyword_vals = {}
    func_sign = inspect.signature(func)
    for k, v in func_sign.parameters.items():
        if v.kind == inspect._ParameterKind.VAR_POSITIONAL:
            var_positional_key = k

        if v.kind == inspect._ParameterKind.KEYWORD_ONLY:
            keyword_vals[k] = v

        if v.kind == inspect._ParameterKind.POSITIONAL_OR_KEYWORD:
            if v.default == inspect._empty:
                positional_or_keyword_keys.append(k)
            else:
                keyword_vals[k] = v.default

    params = {}
    # positional_or_keyword_params
    positional_or_keyword_params = dict(zip(positional_or_keyword_keys, args))
    params.update(positional_or_keyword_params)

    # var_keyword_params
    var_keyword_params = keyword_vals
    params.update(var_keyword_params)

    # var_positional_params
    var_positional_val = list(args[len(positional_or_keyword_params):])
    if var_positional_key and var_positional_val:
        var_positional_params = {var_positional_key: var_positional_val}
        params.update(var_positional_params)

    # kwargs
    params.update(kwargs)
    return params


def cache_decorator(rc: RedisCluster, key_prefix: str, timeout: int = 600):
    def wrapper(func):
        @wraps(func)
        def __wrapper(*args, **kwargs):
            params = load_params(func, *args, **kwargs)
            code = check_params(params)
            if code:
                key = build_key(key_prefix, params, func.__name__)
                result_str = rc.get(key)
                if result_str is not None:
                    result = json.loads(result_str)
                    cache_logger.info("GET: 【{}】【{}】".format(key, result_str))
                    return result

            result = func(*args, **kwargs)
            if code:
                result_str = json_result(result)
                if result_str:
                    rc.set(key, result_str, timeout)
                    cache_logger.info("SET: 【{}】【{}】".format(key, result_str))
            return result
        return __wrapper
    return wrapper


class WrapperCache:
    def __init__(self, rc: RedisCluster):
        self.CacheContext = partial(CacheContext, rc)
        self.CacheDecorator = partial(cache_decorator, rc)
