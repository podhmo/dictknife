import re


def apply(q, v, *args):
    """Applies a query or callable to a value.

    If `q` is callable, it's called with `v` and any additional `args`.
    Otherwise, it performs an equality check between `q` and `v`.

    Args:
        q: The query or callable.
        v: The value to apply the query to.
        *args: Additional arguments to pass to the callable if `q` is callable.

    Returns:
        The result of the application or comparison.
    """
    if callable(q):
        return q(v, *args)
    else:
        return q == v


def repr(self) -> str:
    return "<{self.__class__.__name__} args={args!r}>".format(self=self, args=self.args)


class Regexp(object):
    """A callable object that performs a regular expression search.

    Attributes:
        args: The compiled regular expression pattern.
    """
    __repr__ = repr

    def __init__(self, rx) -> None:
        if isinstance(rx, (str, bytes)):
            rx = re.compile(rx)
        self.args = rx

    def __call__(self, v, *args):
        return self.args.search(v)


class Any(object):
    """A callable object that always returns True.

    Useful as a wildcard or placeholder in queries.
    """
    def __repr__(self) -> str:
        return "<{self.__class__.__name__}>".format(self=self)

    def __call__(self, v, *args) -> bool:
        return True


ANY = Any()


class Not(object):
    """A callable object that negates the result of applying another query.

    Attributes:
        args: The query object whose result will be negated.
    """
    __repr__ = repr

    def __init__(self, value) -> None:
        self.args = value

    def __call__(self, v, *args) -> bool:
        return not apply(self.args, v, *args)


class Or(object):
    """A callable object that performs a logical OR operation on multiple queries.

    It returns True if any of the provided queries return True when applied to the value.

    Attributes:
        args: A list or tuple of query objects.
    """
    __repr__ = repr

    def __init__(self, args) -> None:
        self.args = args

    def __call__(self, v, *args) -> bool:
        for e in self.args:
            if apply(e, v, *args):
                return True
        return False


class And(object):
    """A callable object that performs a logical AND operation on multiple queries.

    It returns True if all of the provided queries return True when applied to the value.

    Attributes:
        args: A list or tuple of query objects.
    """
    __repr__ = repr

    def __init__(self, args) -> None:
        self.args = args

    def __call__(self, v, *args) -> bool:
        for e in self.args:
            if not apply(e, v, *args):
                return False
        return True
