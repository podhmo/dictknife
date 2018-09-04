import contextlib
from ._lazyimport import m

_loader = None


def load(pattern, *, errors=None, loader=None, **kwargs):
    global _loader
    loader = loader or _loader
    if _loader is None:
        _loader = m.gsuite.Loader()
    return _loader.load_sheet(pattern)


def dump(rows, fp, *, sort_keys=False):
    raise NotImplementedError("><")


@contextlib.contextmanager
def not_open(path, encoding=None, errors=None):
    yield path.strip()
