import json
import time
from datetime import datetime
from logging import Formatter


def json_defaulter(d):
    if isinstance(d, datetime):
        return d.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(d)


class JsonStyle:
    default_format = '{"message": "{message}"}'
    asctime_search = 'asctime'

    def __init__(self, fmt):
        self.keys = fmt.split('|') or []
        self._fmt = self.__build_fmt() or self.default_format

    def usesTime(self):
        return self._fmt.find(self.asctime_search) >= 0

    def format(self, record):
        return self._fmt.format(**record.__dict__)

    def add_key(self, key):
        if key not in self.keys:
            self.keys.append(key)
            self._fmt = self.__build_fmt() or self.default_format

    def __build_fmt(self):
        _fmt = {}
        for key in self.keys:
            key = key.strip()
            _fmt[key] = '{{{}}}'.format(key)
        return '{' + json.dumps(_fmt, ensure_ascii=False, default=json_defaulter) + '}'


class JsonFormatter(Formatter):
    converter = time.localtime

    def __init__(self, fmt, datefmt):
        super().__init__(fmt, datefmt)
        self._style = JsonStyle(fmt)
        self._fmt = self._style._fmt
        self.datefmt = datefmt

    def add_key(self, key):
        self._style.add_key(key)
        return self

    def add_keys(self, *keys):
        for key in keys:
            self.add_key(key)
        return self


DEFAULT_TEXT_LOG_FORMAT = '%(name)s | %(asctime)s | %(levelname)-8s | %(message)s'
DEFAULT_TEXT_DATE_FORMAT = '%d/%m/%y %H:%M:%S'
DEFAULT_TEXT_FORMAT = Formatter(DEFAULT_TEXT_LOG_FORMAT, DEFAULT_TEXT_DATE_FORMAT)
DEFAULT_JSON_LOG_FORMAT = 'name|asctime|levelname|message'
DEFAULT_JSON_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_JSON_FORMAT = JsonFormatter(DEFAULT_JSON_LOG_FORMAT, DEFAULT_JSON_DATE_FORMAT)