from .langhelpers import reify


def deepequal(d0, d1, normalize=False):
    if normalize:
        d0 = sort_flexibly(d0)
        d1 = sort_flexibly(d1)
    return halfequal(d0, d1) and halfequal(d1, d0)


def sort_flexibly(ob):
    wv = _wrap(ob)
    return _unwrap(wv)


def _wrap(ob):
    if isinstance(ob, (list, tuple)):
        wvals = [_wrap(x) for x in ob]
        keys = set()
        for wv in wvals:
            if wv.keys:
                keys.update(wv.keys)
        keys = tuple(sorted(keys))
        for wv in wvals:
            wv.arrange(keys)
        return _Collection(sorted(wvals, key=lambda x: x.uid), keys)
    elif hasattr(ob, "keys"):
        for k, v in list(ob.items()):
            ob[k] = _wrap(v)
        return _Dict(ob)
    else:
        return _Atom(ob)


def _unwrap(wob):
    if hasattr(wob, "unwrap"):
        return wob.unwrap()
    else:
        return wob


def halfequal(left, right):
    if hasattr(left, "keys"):
        for k in left.keys():
            if k not in right:
                return False
            if not halfequal(left[k], right[k]):
                return False
        return True
    elif isinstance(left, (list, tuple)):
        if len(left) != len(right):
            return False
        for x, y in zip(left, right):
            if not halfequal(x, y):
                return False
        return True
    else:
        return left == right


class _Atom:
    def __init__(self, value) -> None:
        self.value = value

    @reify
    def uid(self):
        return repr(self.value)

    @property
    def keys(self):
        return None

    def unwrap(self):
        return self.value

    def arrange(self, new_keys) -> None:
        pass


class _Collection:
    def __init__(self, value, keys) -> None:
        self.value = value
        self.keys = keys

    @reify
    def uid(self):
        return repr(tuple([v.uid for v in self.value]))

    def unwrap(self):
        return [v.unwrap() for v in self.value]

    def arrange(self, new_keys) -> None:
        self.keys = new_keys


class _Dict:
    def __init__(self, value) -> None:
        self.value = value

    @reify
    def keys(self):
        return frozenset(self.value.keys())

    @reify
    def uid(self):
        return repr(tuple(self.value.get(k, _NONE).uid for k in self.keys))

    def unwrap(self):
        d = self.value
        for k in list(d.keys()):
            d[k] = d[k].unwrap()
        return d

    def arrange(self, new_keys) -> None:
        self.keys = new_keys


_NONE = _Atom(None)
