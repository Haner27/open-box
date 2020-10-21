from tempfile import NamedTemporaryFile

from open_box.file import File


def file_usage():
    # load file from url
    f = File("https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1603282675348&di=517865944433fc76b375dc7f2415650c&imgtype=0&src=http%3A%2F%2Fa2.att.hudong.com%2F36%2F48%2F19300001357258133412489354717.jpg")
    print(f.filename, f.content_type, f.size, f.size_text, f.md5, f.ext)
    # load file from local path
    f = File(__file__)
    print(f.filename, f.content_type, f.size, f.size_text, f.md5, f.ext)
    # load file from bytes or file-like
    with NamedTemporaryFile(suffix='.yaml') as f:
        s = b"""mongodb:
      database_url: mongodb://xxxxxxxxxxxxx
      database_name: yyyyyyyyyyy
    elasticsearch:
      hosts: ["127.0.0.1:9200", "127.0.0.1:9201"]
    mysql:
      host: mysql+pymysql://zzzzzzzzzzzz
    """
        f.write(s)
        f.seek(0)
        fp = File(f)
        print(fp.filename, fp.content_type, fp.size, fp.size_text, fp.md5, fp.ext)
        fp = File(f.read())
        print(fp.filename, fp.content_type, fp.size, fp.size_text, fp.md5, fp.ext)
        print(fp.profile)


if __name__ == '__main__':
    file_usage()