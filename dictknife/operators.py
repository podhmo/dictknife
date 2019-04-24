import re


def apply(q, v, *args):
    if callable(q):
        return q(v, *args)
    else:
        return q == v


def repr(self):
    return "<{self.__class__.__name__} args={args!r}>".format(self=self, args=self.args)


class Regexp(object):
    __repr__ = repr

    def __init__(self, rx):
        if isinstance(rx, (str, bytes)):
            rx = re.compile(rx)
        self.args = rx

    def __call__(self, v, *args):
        return self.args.search(v)


class Any(object):
    def __repr__(self):
        return "<{self.__class__.__name__}>".format(self=self)

    def __call__(self, v, *args):
        return True


ANY = Any()


class Not(object):
    __repr__ = repr

    def __init__(self, value):
        self.args = value

    def __call__(self, v, *args):
        return not apply(self.args, v, *args)


class Or(object):
    __repr__ = repr

    def __init__(self, args):
        self.args = args

    def __call__(self, v, *args):
        for e in self.args:
            if apply(e, v, *args):
                return True
        return False


class And(object):
    __repr__ = repr

    def __init__(self, args):
        self.args = args

    def __call__(self, v, *args):
        for e in self.args:
            if not apply(e, v, *args):
                return False
        return True
