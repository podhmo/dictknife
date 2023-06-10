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
        import tomlkit

        class _TomlAdaptor:
            @classmethod
            def load(cls, fp, *args, **kwargs):
                return tomlkit.load(fp)

            @classmethod
            def dump(cls, data, fp=None, *args, sort_keys=False, **kwargs):
                return tomlkit.dump(data, fp, sort_keys=sort_keys)

        return _TomlAdaptor

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
            msg = "google-api-python-client package is not found (original exception is {!r})".format(
                e
            )
            print(msg, file=sys.stderr)
            sys.exit(1)

    @reify
    def yaml(self):
        try:
            from . import _yaml as yaml
            return yaml
        except ImportError:
            logger.info("yaml package is not found, failback to json")
            import json

            class _fake_yaml:
                SortedDumper = None
                Loader = None

                @classmethod
                def load(cls, *args, typ="rt", loader=None, **kwargs):
                    return json.load(*args, **kwargs)

                @classmethod
                def dump(
                    cls,
                    *args,
                    # allow_unicode=None,
                    # default_flow_style=None,
                    **kwargs
                ):
                    if "indent" not in kwargs:
                        kwargs["indent"] = 2
                    if "ensure_ascii" not in kwargs:
                        kwargs["ensure_ascii"] = False
                    return json.dump(*args, **kwargs)

            return _fake_yaml


m = LoadingModule()
