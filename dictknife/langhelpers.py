# if sys.version_info[:2] >= (3, 6):
#     make_dict = dict
# else:
from collections import OrderedDict as make_dict  # noqa

# for backword comaptibility (TODO: remove)
from .cliutils import traceback_shortly  # noqa F401
from .naming import normalize, titleize, untitleize  # noqa F401


def pairsplit(s, sep):
    r = s.split(sep, 1)
    if len(r) == 1:
        return r[0], ""
    else:
        return r


def pairrsplit(s, sep):
    r = s.rsplit(sep, 1)
    if len(r) == 1:
        return r[0], ""
    else:
        return r


# stolen from pyramid
class reify(object):
    """cached property"""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # noqa
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def as_jsonpointer(k):
    k = str(k)
    if "/" not in k:
        return k
    return k.replace("~", "~0").replace("/", "~1")


def as_path_node(ref):
    if "~" not in ref:
        return ref
    return ref.replace("~1", "/").replace("~0", "~")
