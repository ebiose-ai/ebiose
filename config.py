import os

import yaml


class Config:
    def __init__(self, config_file):
        config_path = os.path.join(os.path.dirname(__file__), config_file)
        with open(config_path) as file:
            self._config = yaml.safe_load(file)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self._config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default


config = Config("config.yml")
