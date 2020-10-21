from logging import INFO

from open_box.log import Logger, SECONDS
from open_box.log.formatter import DEFAULT_TEXT_FORMAT, DEFAULT_JSON_FORMAT


def base():
    logger = Logger('HNF', level=INFO)
    logger.info('hello world!')


def text_formatter():
    logger = Logger('HNF', level=INFO, formatter=DEFAULT_TEXT_FORMAT)
    logger.info('hello world!')


def json_formatter():
    logger = Logger('HNF', level=INFO, formatter=DEFAULT_JSON_FORMAT)
    logger.info('hello world!')


def json_formatter_with_fields():
    json_formatter = DEFAULT_JSON_FORMAT
    json_formatter.add_key('username').add_key('password')
    json_formatter.add_keys('age', 'gender')
    logger = Logger('HNF', level=INFO, formatter=json_formatter)
    logger.info('login succeed!', extra={
        'username': '123', 'password': '456',
        'age': 28, 'gender': 'male',
    })


def with_file_log():
    json_formatter = DEFAULT_JSON_FORMAT
    json_formatter.add_key('username').add_key('password')
    json_formatter.add_keys('age', 'gender')
    logger = Logger('HNF', level=INFO, formatter=json_formatter)
    logger.add_rotating_file_handler('./logs/hnf.log', formatter=DEFAULT_TEXT_FORMAT)
    logger.info('login succeed!', extra={
        'username': '123', 'password': '456',
        'age': 28, 'gender': 'male',
    })


def with_tiemd_file_log():
    json_formatter = DEFAULT_JSON_FORMAT
    json_formatter.add_key('username').add_key('password')
    json_formatter.add_keys('age', 'gender')
    logger = Logger('HNF', level=INFO, formatter=json_formatter)
    logger.add_timed_rotating_file_handler('./logs/hnf.log', when=SECONDS, formatter=DEFAULT_TEXT_FORMAT)
    logger.info('login succeed!', extra={
        'username': '123', 'password': '456',
        'age': 28, 'gender': 'male',
    })


def with_email_log():
    logger = Logger('HNF', level=INFO)

    sender = '<sender>'
    receives = [
        '369685930@qq.com'
    ]
    mail_host = '<mail-host>'
    subject = 'login failed'
    logger.add_email_handler(
        sender, receives, subject, mail_host=mail_host, level=INFO
    )

    logger.error('login failed!', extra={
        'username': '123', 'password': '456',
        'age': 28, 'gender': 'male',
    })


if __name__ == '__main__':
    base()
    # text_formatter()
    # json_formatter()
    # json_formatter_with_fields()
    # with_file_log()
    # with_tiemd_file_log()
    # with_email_log()