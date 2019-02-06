import re

# if sys.version_info[:2] >= (3, 6):
#     make_dict = dict
# else:
from collections import OrderedDict as make_dict  # noqa


def normalize(name, ignore_rx=re.compile("[^0-9a-zA-Z_]+")):
    return ignore_rx.sub("", name.replace("-", "_"))


def titleize(name):
    if not name:
        return name
    name = str(name)
    return normalize("{}{}".format(name[0].upper(), name[1:]))


def untitleize(name):
    if not name:
        return name
    return "{}{}".format(name[0].lower(), name[1:])


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
        except:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def as_jsonpointer(k):
    if "/" not in k:
        return k
    return k.replace("~", "~0").replace("/", "~1")
