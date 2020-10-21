import hashlib
import mimetypes
import os
import re
from io import BytesIO
from urllib.parse import unquote
from urllib.request import urlopen

import magic

from .error import GetFileFromUrlError, FileInputTypeError

SIZE_B = 'B'
SIZE_KB = 'KB'
SIZE_MB = 'MB'
SIZE_GB = 'GB'
SIZE_TB = 'TB'
SIZE_PB = 'PB'
UNIT_MAP = {
    0: SIZE_B,
    1: SIZE_KB,
    2: SIZE_MB,
    3: SIZE_GB,
    4: SIZE_TB,
    5: SIZE_PB,
}

B = 1
KB = 1024 * B
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB
PB = 1024 * TB


class File:
    FILENAME_PATTERN = re.compile(r'filename\*=UTF-8\'\'')

    def __init__(self, input, filename=""):
        self.bio, self.filename  = self.__load_file(input, filename)
        self.size = self.__load_size()
        self.content_type = self.__load_content_type(filename)
        self.ext = self.__load_ext()
        self.__refine_filename()

    @property
    def size_text(self):
        num = self.size
        n = 0
        while num > 1024:
            num = num / 1024.0
            n += 1
            if n >= 5:
                break
        return '%.2f%s' % (num, UNIT_MAP.get(n))

    @property
    def md5(self):
        md5 = hashlib.md5(self.bio.getvalue()).hexdigest()
        self.bio.seek(0)
        return md5

    def __refine_filename(self):
        if not self.filename:
            if self.md5 and self.ext:
                self.filename = '{}{}'.format(self.md5, self.ext)

    def __load_ext(self):
        _, ext = os.path.splitext(self.filename)
        if not ext:
            ext = mimetypes.guess_extension(self.content_type) or ''
        return ext

    def __load_file(self, input, filename):
        if isinstance(input, BytesIO):
            return input, filename

        if isinstance(input, bytes):
            bio = BytesIO(input)
            bio.seek(0)
            return bio, filename

        if hasattr(input, 'read') and hasattr(input, 'seek'):
            bio = BytesIO(input.read())
            bio.seek(0)
            input.seek(0)
            return bio, filename

        if isinstance(input, str):
            if os.path.exists(input):
                if not filename:
                    filename = os.path.basename(input)

                bio = BytesIO()
                with open(input, 'rb') as f:
                    bio.write(f.read())
                bio.seek(0)
                return bio, filename

            if input.startswith(("http", "https")):
                r = urlopen(input)
                if r.status == 200:
                    if not filename:
                        filename = self.__get_filename_from_url(r)

                    bio = BytesIO()
                    bio.write(r.read())
                    bio.seek(0)
                    return bio, filename
                else:
                    raise GetFileFromUrlError(input)

        raise FileInputTypeError("")

    def __load_size(self):
        self.bio.seek(0, 2)
        size = self.bio.tell()
        self.bio.seek(0)
        return size

    def __load_content_type(self, filename):
        buf = magic.from_buffer(self.bio.read(), mime=True)
        self.bio.seek(0)
        if buf == 'application/octet-stream':
            if filename:
                _, ext = os.path.splitext(filename)
                mimetype = mimetypes.types_map.get(ext, '')
                if mimetype != buf:
                    return mimetype
        return buf

    def __get_filename_from_url(self, result):
        attachment_name = result.info().get_filename() or ''
        content_disposition = result.headers.get('content-disposition', '')
        if content_disposition:
            for item in content_disposition.split(';'):
                item = item.strip()
                if 'filename*=UTF-8' in item:
                    attachment_name = re.sub(self.FILENAME_PATTERN, '', item)
                    attachment_name = unquote(attachment_name)

        attachment_name = unquote(attachment_name)
        if not attachment_name:
            attachment_name = os.path.basename(result.url)
        return attachment_name

    def save(self, dirname=''):
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        path = self.filename
        if dirname:
            if not dirname.endswith('/'):
                dirname += '/'
            path = dirname + path

        with open(path, 'wb') as f:
            f.write(self.bio.getvalue())

        self.bio.seek(0)

    @property
    def profile(self):
        return {
            'filename': self.filename,
            'content_type': self.content_type,
            'size': self.size,
            'size_text': self.size_text,
            'md5': self.md5,
            'ext': self.ext,
        }
