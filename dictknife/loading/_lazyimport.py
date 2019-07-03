from logging import getLogger as get_logger
from dictknife.langhelpers import reify
logger = get_logger(__name__)


class LoadingModule:
    @reify
    def json(self):
        import json
        return json

    @reify
    def toml(self):
        import qtoml
        return qtoml

    @reify
    def csv(self):
        import csv
        return csv

    @reify
    def gsuite(self):
        try:
            import sys
            from . import _gsuite as gsuite
            return gsuite
        except ImportError as e:
            msg = "google-api-python-client package is not found (original exception is {!r})".format(e)
            print(msg, file=sys.stderr)
            sys.exit(1)

    @reify
    def yaml(self):
        try:
            from . import _yaml as yaml
            yaml.setup(yaml.Loader, yaml.Dumper)
            return yaml
        except ImportError:
            logger.info("yaml package is not found, failback to json")
            import json

            class _fake_yaml:
                SortedDumper = None
                Dumper = None
                Loader = None

                @classmethod
                def load(cls, *args, Loader=None, **kwargs):
                    return json.load(*args, **kwargs)

                @classmethod
                def dump(
                    cls, *args, allow_unicode=None, default_flow_style=None, Dumper=None, **kwargs
                ):
                    if "indent" not in kwargs:
                        kwargs["indent"] = 2
                    if "ensure_ascii" not in kwargs:
                        kwargs["ensure_ascii"] = False
                    return json.dump(*args, **kwargs)

            return _fake_yaml


m = LoadingModule()
