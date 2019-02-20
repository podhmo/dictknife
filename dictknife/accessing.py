import contextlib
from .langhelpers import make_dict


class Accessor:
    def __init__(self, make_dict=make_dict):
        self.make_dict = make_dict

    def assign(self, d, path, value):
        for name in path[:-1]:
            if name not in d:
                d[name] = self.make_dict()
            d = d[name]
        d[path[-1]] = value

    def access(self, d, path):
        for name in path:
            try:
                d = d[name]
            except TypeError:
                if not isinstance(d, (list, tuple)):
                    raise
                d = d[int(name)]
        return d

    def maybe_remove(self, d, path):
        container = self.maybe_access_container(d, path)
        if container is not None:
            container.pop(path[-1])

    def exists(self, d, path):
        return self.maybe_access_container(d, path) is not None

    def maybe_access(self, d, path, *, default=None):
        d = self.maybe_access_container(d, path, default=default)
        if d is default:
            return default
        return d.get(path[-1])

    def maybe_access_container(self, d, path, *, default=None):
        for name in path[:-1]:
            if name not in d:
                return default
            d = d[name]
        if not d:
            return default
        if path[-1] not in d:
            return default
        return d


missing = object()


class Scope:
    def __init__(self, init=None, *, accessor=None):
        self.states = []
        self.accessor = accessor or Accessor()
        if init is not None:
            self.push(init)

    def get(self, path, default=None):
        if not isinstance(path, (list, tuple)):
            raise TypeError("please tuple or list")
        for s in reversed(self.states):
            v = self.accessor.maybe_access(s, path, default=missing)
            if v is not missing:
                return v
        return default

    def __getitem__(self, path):
        v = self.get(path, default=missing)
        if v is not missing:
            return v
        raise KeyError(path)

    def push(self, state):
        self.states.append(state)

    def pop(self):
        self.states.pop()

    @contextlib.contextmanager
    def scope(self, d=None):
        if d is None:
            yield self
        else:
            try:
                self.push(d)
                yield self
            finally:
                self.pop()


class ImmutableModifier:
    def modify_list(self, fn, xs):
        return [fn(x) for x in xs]

    def modify_dict(self, fn, d):
        r = type(d)()
        for k, v in d.items():
            r[k] = fn(v)
        return r

    def modify_dict_with_keys(self, fn, d):
        r = type(d)()
        for k, v in d.items():
            r[fn(k)] = fn(v)
        return r


class MutableModifier:
    def modify_list(self, fn, xs):
        for i, v in enumerate(xs):
            xs[i] = fn(xs[i])
        return xs

    def modify_dict(self, fn, d):
        for k in list(d.keys()):
            d[k] = fn(d[k])
        return d

    def modify_dict_with_keys(self, fn, d):
        for k in list(d.keys()):
            d[fn(k)] = fn(d.pop(k))
        return d


def dictmap(fn, x, *, mutable=False, with_key=False):
    modifier = MutableModifier() if mutable else ImmutableModifier()
    if with_key:
        modify_dict = modifier.modify_dict_with_keys
    else:
        modify_dict = modifier.modify_dict

    def _map(d):
        if isinstance(d, (list, tuple)):
            return modifier.modify_list(_map, d)
        elif hasattr(d, "keys"):
            return modify_dict(_map, d)
        else:
            return fn(d)

    return _map(x)
