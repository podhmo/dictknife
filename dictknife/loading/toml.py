import toml


def load(fp, *, loader=None, **kwargs):
    return toml.load(fp, **kwargs)


dump = toml.dump
