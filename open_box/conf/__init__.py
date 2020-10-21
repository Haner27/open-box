import json


class ConfigObject(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_attributes(kwargs)

    def load_attributes(self, d):
        for k, v in d.items():
            if isinstance(v, dict):
                self[k] = self.__class__(**v)

            elif isinstance(v, list):
                vs = []
                for i in v:
                    if isinstance(i, dict):
                        vs.append(self.__class__(**i))
                    else:
                        vs.append(i)

                self[k] = vs

    def __getattr__(self, name):
        try:
            value = self[name]
            return value
        except Exception as _:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def __str__(self):
        return json.dumps(self, indent=4, ensure_ascii=False)

