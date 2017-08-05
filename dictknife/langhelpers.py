# -*- coding:utf-8 -*-
import re
import sys
import contextlib


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


@contextlib.contextmanager
def traceback_shortly(debug):
    try:
        yield
    except Exception as e:
        if debug:
            raise
        else:
            print("\x1b[33m\x1b[1m{e.__class__.__name__}: {e}\x1b[0m".format(e=e, file=sys.stderr))
            sys.exit(1)


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
