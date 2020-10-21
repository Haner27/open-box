from datetime import datetime, date, timedelta

DEFAULT_DATETIME_FORMAT_PRECISION = '%Y-%m-%d %H:%M:%S.%f'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'


def now():
    return datetime.now()


def timestamp():
    return datetime.now().timestamp()


def today():
    return date.today()


def yesterday():
    return today() - timedelta(days=1)


def from_timestamp(ts):
    return datetime.fromtimestamp(ts)


def to_timestamp(dt):
    return dt.timestamp()


def format_datetime(dt, format_=DEFAULT_DATETIME_FORMAT_PRECISION):
    return dt.strftime(format_)


def to_datetime(dt_str, format_=DEFAULT_DATETIME_FORMAT):
    return datetime.strptime(dt_str, format_)


def cal_days(seconds):
    return int(seconds // 86400), seconds % 86400


def cal_hours(seconds):
    return int(seconds // 3600), seconds % 3600


def cal_minutes(seconds):
    return int(seconds // 60), seconds % 60


def covert_duration_text(seconds, with_unit=True):
    """转换时长文本"""
    hours, seconds = cal_hours(seconds)
    minutes, seconds = cal_minutes(seconds)
    if with_unit:
        text_list = []
        if hours:
            text_list.extend([str(hours), '小时'])
        if minutes:
            text_list.extend([str(minutes), '分钟'])
        if seconds:
            text_list.extend(['%d' % round(seconds), '秒'])
        return ''.join(text_list)

    return '%02d:%02d:%02d' % (hours, minutes, round(seconds))


def covert_message_duration_text(dt):
    """转换消息发送后距当前时间间隔文本"""
    ts = to_timestamp(dt)
    nts = timestamp()
    delta = nts - ts
    if delta < 60:
        return '刚刚'
    elif 60 <= delta < 3600:
        return '{0}分钟前'.format(int(delta // 60))
    elif 3600 <= delta < 86400:
        return '{0}小时前'.format(int(delta // 3600))
    elif 86400 <= delta < 86400 * 2:
        return '昨天 {}'.format(format_datetime(dt, TIME_FORMAT))
    else:
        return format_datetime(dt, DEFAULT_DATETIME_FORMAT)