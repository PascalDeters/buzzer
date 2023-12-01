import os

import ujson

from config import Config
from logger import Logger


class ConfigManager:
    def __init__(self, file_path="config.json"):
        self.file_path = file_path
        self.logger = Logger()
        self.caller = "ConfigManager"

    def write_config(self, config):
        try:
            with open(self.file_path, "w") as f:
                ujson.dump(config.to_dict(), f)
                self.logger.debug(self.caller, "Config written successfully.")
        except Exception as e:
            self.logger.error(self.caller, "Error writing config: {}".format(e))

    def read_config(self):
        try:
            with open(self.file_path, "r") as f:
                data = ujson.load(f)
                config = Config()
                config.from_dict(data)
                self.logger.debug(self.caller, "Config read successfully.")
                return config
        except Exception as e:
            self.logger.error(self.caller, "Error reading config: {}".format(e))
            return None

    def remove_config(self):
        if self.read_config() is not None:
            try:
                os.remove(self.file_path)
                self.logger.debug(self.caller, "Config removed successfully.")
            except Exception as e:
                self.logger.error(self.caller, "Error removing config: {}".format(e))
        else:
            self.logger.debug(self.caller, "Config file doesn´t exists.")