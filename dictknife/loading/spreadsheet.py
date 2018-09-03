import contextlib
from ._lazyimport import m


def load(pattern, *, errors=None, **kwargs):
    return m.gsuite.Loader().load_sheet(pattern)


def dump(rows, fp, *, sort_keys=False):
    raise NotImplementedError("><")


@contextlib.contextmanager
def not_open(path, encoding=None, errors=None):
    yield path.strip()
