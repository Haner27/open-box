import pyaml

from . import ConfigObject


class YamlConfigLoader:
    def __init__(self, conf_file):
        with open(conf_file) as f:
            yaml = pyaml.yaml.safe_load(f) or {}
        self.__dict__.update(ConfigObject(**yaml))
