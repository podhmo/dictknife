from ._lazyimport import m
from .raw import setup_extra_parser  # noqa


def load(fp, *, loader=None, errors=None, **kwargs):
    return m.yaml.load(fp, Loader=m.yaml.Loader, **kwargs)


def dump(d, fp, *, sort_keys=False):
    return m.yaml.dump(
        d,
        fp,
        allow_unicode=True,
        default_flow_style=False,
        Dumper=m.yaml.Dumper,
        sort_keys=sort_keys,
    )
