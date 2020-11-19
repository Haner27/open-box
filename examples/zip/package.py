from io import BytesIO
import hashlib
from tempfile import NamedTemporaryFile

from open_box.zip import Zip


def package_file():
    z = Zip()
    # with NamedTemporaryFile(prefix='test-', suffix='zip.txt') as f:
    #     with open(f.name, 'w') as fi:
    #         fi.write('i am haner')
    #     z.add_file('local.txt', f.name)

    bio = BytesIO()
    bio.write('haner27'.encode())
    z.add_file('fp.txt', bio)

    # z.add_file('xxx.jpg', 'https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png')

    output_io = z.output()

    with open('test.zip', 'wb') as f:
        content = output_io.getvalue()
        _md5 = hashlib.md5(content).hexdigest()
        print(_md5)
        f.write(content)


if __name__ == '__main__':
    package_file()
