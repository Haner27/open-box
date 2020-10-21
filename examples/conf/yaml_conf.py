from tempfile import NamedTemporaryFile

from open_box.conf.yaml_loader import YamlConfigLoader


def test1():
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

        conf = YamlConfigLoader(f.name)

        # 加载完成后直接根据yaml文件的定义来使用配置项
        print(conf.mongodb.database_url)
        print(conf.mongodb.database_name)
        print(conf.elasticsearch.hosts)
        print(conf.mysql.host)

        print(dir(conf))


if __name__ == '__main__':
    test1()
