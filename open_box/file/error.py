ERR_FILE_INPUT_TYPE = 100
ERR_GET_FILE_FROM_URL = 101
ERR_UNKNOWN = -1

ERRORS = {
    ERR_FILE_INPUT_TYPE: 'data type error of file input',
    ERR_GET_FILE_FROM_URL: 'load file data from url failed',
    ERR_UNKNOWN: 'unknown error',
}


class ImageError(Exception):
    def __init__(self, msg, code=None, extras=None):
        """
        :param msg: error msg
        :param code: error code
        :param extras:
        """
        self.msg = msg
        if code not in ERRORS:
            code = ERR_UNKNOWN

        self.code = code
        self.code_error = ERRORS.get(self.code)
        self.extras = extras
        error_msg = '[{0}][{1}]{2}'.format(self.code, self.code_error, self.msg)
        super().__init__(error_msg)


class FileInputTypeError(ImageError):
    def __init__(self, msg):
        code = ERR_FILE_INPUT_TYPE
        super().__init__(msg, code)


class GetFileFromUrlError(ImageError):
    def __init__(self, msg):
        code = ERR_GET_FILE_FROM_URL
        super().__init__(msg, code)
