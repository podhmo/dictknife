from dictknife.langhelpers import reify


class LoadingModule:
    @reify
    def json(self):
        import json
        return json

    @reify
    def toml(self):
        import toml
        return toml

    @reify
    def yaml(self):
        from . import _yaml as yaml
        yaml.setup(yaml.Loader, yaml.Dumper)
        return yaml


m = LoadingModule()
