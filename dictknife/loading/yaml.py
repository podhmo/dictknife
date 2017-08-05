from ._lazyimport import m


def load(fp, *, loader=None, **kwargs):
    return m.yaml.load(fp, Loader=m.yaml.Loader, **kwargs)


def dump(d, fp):
    return m.yaml.dump(d, fp, allow_unicode=True, default_flow_style=False, Dumper=m.yaml.Dumper)
