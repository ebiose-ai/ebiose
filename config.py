from pathlib import Path

import yaml


class Config:
    def __init__(self, config_file: str) -> None:
        config_path = Path(__file__).parent / config_file
        with config_path.open() as file:
            self._config = yaml.safe_load(file)

    def get(self, key: str) -> any:
        keys = key.split(".")
        value = self._config
        for k in keys:
            value = value.get(k, {})
        return value # if value != {} else default


config = Config("config.yml")
