from ._lazyimport import m
from .raw import setup_extra_parser


def load(fp, *, loader=None, errors=None, **kwargs):
    return m.yaml.load(fp, Loader=m.yaml.Loader, **kwargs)


def dump(d, fp, *, sort_keys=False):
    dumper_class = m.yaml.SortedDumper if sort_keys else m.yaml.Dumper
    return m.yaml.dump(d, fp, allow_unicode=True, default_flow_style=False, Dumper=dumper_class)
