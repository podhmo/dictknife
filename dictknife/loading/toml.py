from ._lazyimport import m
from .raw import setup_extra_parser  # noqa


def load(fp, *, loader=None, errors=None, **kwargs):
    return m.toml.load(fp, **kwargs)


def dump(d, fp, *, sort_keys: bool=False, **kwargs):
    return m.toml.dump(d, fp, **kwargs)
