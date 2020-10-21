import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, SMTPHandler

B = 1
KB = 1024 * B
MB = 1024 * KB
GB = 1024 * MB

SECONDS = 'S'
MINUTES = 'M'
HOURS = 'H'
DAYS = 'D'


class Logger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET, formatter=None):
        super().__init__(name, level)
        self.__formatter = formatter
        self.add_handler(logging.StreamHandler())

    @property
    def formatter(self):
        return self.__formatter

    def add_handler(self, hdr, level=logging.NOTSET, formatter=None):
        hdr.setLevel(level or self.level)
        hdr.setFormatter(formatter or self.__formatter)
        self.addHandler(hdr)
        return self

    def with_default_formatter(self):
        for hdr in self.handlers:
            hdr.setFormatter(self.__formatter)

    def add_rotating_file_handler(self, log_path, level=None, max_bytes=10 * MB, backup_count=5, formatter=None):
        dirname = os.path.dirname(log_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        hdr = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count)
        return self.add_handler(hdr, level, formatter)

    def add_timed_rotating_file_handler(self, log_path, level=None, when=DAYS, interval=1, backup_count=5,
                                        formatter=None):
        dirname = os.path.dirname(log_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        hdr = TimedRotatingFileHandler(log_path, when=when, interval=interval, backupCount=backup_count)
        return self.add_handler(hdr, level, formatter)

    def add_email_handler(self, sender, receives, subject, mail_host, username=None, password=None, level=None,
                          formatter=None):
        hdr = SMTPHandler(
            mailhost=mail_host, fromaddr=sender, toaddrs=receives, subject=subject,
            credentials=(username, password),
        )
        return self.add_handler(hdr, level, formatter)
