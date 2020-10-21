ERR_FILE_INPUT_TYPE = 100
ERR_GET_FILE_FROM_URL = 101
ERR_UNKNOWN = -1

ERRORS = {
    ERR_FILE_INPUT_TYPE: '文件初始化输入数据类型错误',
    ERR_GET_FILE_FROM_URL: '从url获取文件失败',
    ERR_UNKNOWN: '未知错误',
}


class ImageError(Exception):
    def __init__(self, msg, code=None, extras=None):
        """
        :param msg: 具体错误信息
        :param code: 错误码
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
