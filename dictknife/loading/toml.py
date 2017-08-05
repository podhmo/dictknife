from ._lazyimport import m


def load(fp, *, loader=None, **kwargs):
    return m.toml.load(fp, **kwargs)


def dump(*args, **kwargs):
    return m.toml.dump(*args, **kwargs)
