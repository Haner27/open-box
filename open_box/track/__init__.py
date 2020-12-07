import inspect
import json
from contextlib import contextmanager

from open_box.datetime import now, datetime, format_datetime


def json_defaulter(d):
    if isinstance(d, (dict, list, bool, tuple, str, int, float, type(None))):
        return d

    if isinstance(d, datetime):
        x = format_datetime(d)
        return x

    return str(d)


class Stage:
    def __init__(self, name, caller_info=None):
        self.__name = name
        self.__start = now()
        self.__end = None
        self.__caller_info = caller_info

    @property
    def name(self):
        return self.__name

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def duration(self):
        try:
            return self.__end.timestamp() - self.__start.timestamp()
        except Exception as _:
            return 0

    @property
    def caller_info(self):
        return self.__caller_info

    def finish(self, dt=None):
        self.__end = dt or now()

    def report(self):
        return {
            'name': self.__name,
            'start': self.__start,
            'end': self.__end,
            'duration': self.duration,
            'caller_info': self.__caller_info
        }

    @staticmethod
    def format_dt(dt):
        try:
            return format_datetime(dt)
        except Exception as _:
            return 'None'

    def __repr__(self):
        return '<Stage: {} start: {} end: {} durations: {}>'.format(
            self.__name,
            self.format_dt(self.__start),
            self.format_dt(self.__end),
            self.duration
        )


class Tracker:
    def __init__(self, name):
        self.__name = name
        self.__stages = []
        self.__current_stage = None
        self.__start = None
        self.__end = None
        self.__is_finished = False
        self.__init_stages()

    def __init_stages(self):
        self.mark('TRACKER BEGIN', frame_depth=3)
        self.__start = self.__current_stage.start

    @property
    def name(self):
        return self.__name

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    @property
    def duration(self):
        try:
            return self.__end.timestamp() - self.__start.timestamp()
        except Exception as _:
            return 0

    @property
    def stages(self):
        return self.__stages

    def mark(self, stage_name, frame_depth=1):
        depth = 0
        frame = inspect.currentframe()
        while depth < frame_depth:
            frame = frame.f_back
            depth += 1
        caller_info = self.caller_info(frame)
        stage = Stage(stage_name, caller_info)
        if self.__current_stage:
            self.__current_stage.finish(stage.start)
        self.__stages.append(stage)
        self.__current_stage = stage

    @contextmanager
    def span(self, stage_name):
        try:
            self.mark(stage_name, frame_depth=3)
            yield
        finally:
            self.__current_stage.finish()

    def report(self):
        if not self.__is_finished:
            raise Exception('tracker is not finished, do finish()!!!')

        return {
            'name': self.__name,
            'start': self.__start,
            'end': self.__end,
            'duration': self.duration,
            'stages': [stage.report() for stage in self.__stages]
        }

    def output(self):
        data = self.report()
        return json.dumps(data, indent=4, ensure_ascii=False, default=json_defaulter)

    def finish(self, dt=None):
        self.__end = dt or now()
        if self.__current_stage:
            self.__current_stage.finish(self.__end)
        self.__is_finished = True

    @staticmethod
    def format_dt(dt):
        try:
            return format_datetime(dt)
        except Exception as _:
            return 'None'

    @staticmethod
    def caller_info(f):
        module = f.f_globals.get('__name__', '')
        func_name = f.f_code.co_name
        var_names = list(f.f_code.co_varnames)
        var_names = var_names[:f.f_code.co_argcount]
        params = {}
        for var_name in var_names:
            params[var_name] = f.f_locals.get(var_name)
        return {
            'module': module,
            'func_name': func_name,
            'params': params
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.finish()

    def __repr__(self):
        return '<Tracker: {} start: {} end: {} duration: {}>'.format(
            self.__name,
            self.format_dt(self.__start),
            self.format_dt(self.__end),
            self.duration
        )
