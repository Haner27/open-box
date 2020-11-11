import zipfile
from io import BytesIO
from logging import INFO
from urllib.request import urlopen

from open_box.log import Logger
from open_box.log.formatter import DEFAULT_TEXT_FORMAT

zip_logger = Logger('zip', level=INFO, formatter=DEFAULT_TEXT_FORMAT)


class Zip(object):
    def __init__(self, md5_not_modified=False):
        self.__io = BytesIO()
        self.__zf = zipfile.ZipFile(self.__io, 'a', zipfile.ZIP_DEFLATED, False)
        self.__md5_not_modified = md5_not_modified

    def add_file(self, alias, filename_or_fp):
        """
        add file to zip
        :param alias: alias name
        :param filename_or_fp: local file, url, fp
        :return:
        """
        if alias not in self.__zf.namelist():
            if isinstance(filename_or_fp, BytesIO):
                self.__add_fp(alias, filename_or_fp)
            elif isinstance(filename_or_fp, str):
                if filename_or_fp.startswith(('http', 'https')):
                    self.__add_url(alias, filename_or_fp)
                else:
                    self.__add_local_file(alias, filename_or_fp)
            else:
                raise Exception('filename_or_fp must be BytesIO or filename')
            zip_logger.info('add [{}] to zip'.format(alias))
        return self

    def __add_fp(self, alias, fp):
        if self.__md5_not_modified:
            self.__zf.writestr(zipfile.ZipInfo(alias), fp.getvalue(), zipfile.ZIP_DEFLATED)
        else:
            self.__zf.writestr(alias, fp.getvalue(), zipfile.ZIP_DEFLATED)
        fp.seek(0)
        fp.close()

    def __add_local_file(self, alias, filename):
        self.__zf.write(filename, alias, zipfile.ZIP_DEFLATED)

    def __add_url(self, alias, url):
        r = urlopen(url)
        if r.status == 200:
            bio = BytesIO()
            bio.write(r.read())
            bio.seek(0)
            self.__add_fp(alias, bio)
        else:
            raise Exception('{} is not a valid url')

    def __close(self):
        self.__zf.close()
        self.__io.seek(0)

    def output(self):
        self.__close()
        return self.__io

    @property
    def size(self):
        self.__io.seek(0, 2)
        size = self.__io.tell()
        self.__io.seek(0)
        return size
