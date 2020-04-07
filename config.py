import os.path, json

class ConfigItem:
    def __init__(self, obj):
        self._raw = obj
        for k, v in obj.items():
            self.__dict__[k] = self.new(v)

    @classmethod
    def new(cls, x):
        if isinstance(x, dict):
            return ConfigItem(x)
        return x

BASE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(BASE, "config.json"), "r") as configfile:
    for k, v in json.load(configfile).items():
        globals()[k] = ConfigItem.new(v)
