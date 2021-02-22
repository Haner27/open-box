import os

import pyaml

from open_box.conf import ConfigObject
from addict import Dict


class YamlConfigLoader:
    def __init__(self, conf_file: str):
        with open(conf_file) as f:
            yaml = pyaml.yaml.safe_load(f) or {}
        self.yaml_dict = Dict(yaml)

    def __getattr__(self, item: str):
        return self.yaml_dict[item]
