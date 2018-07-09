from ._lazyimport import m


def load(fp, *, loader=None, errors=None, **kwargs):
    return m.toml.load(fp, **kwargs)


def dump(d, fp, *, sort_keys=False, **kwargs):
    return m.toml.dump(d, fp, **kwargs)
