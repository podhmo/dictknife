from ._lazyimport import m
from .raw import setup_extra_parser  # noqa


def load(fp, *, errors=None, **kwargs):
    return m.yaml.load(fp, **kwargs)


def dump(d, fp, *, sort_keys: bool = False):
    return m.yaml.dump(
        d,
        fp,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=sort_keys,
    )
