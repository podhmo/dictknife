import contextlib
from .langhelpers import make_dict


class Accessor:
    """Provides methods for accessing and modifying nested dictionary-like objects.

    Attributes:
        make_dict: A function to create new dictionary-like objects.
        zero_value: The value to use when an index is out of bounds in a list.
    """

    def __init__(self, make_dict=make_dict, zero_value=None) -> None:
        self.make_dict = make_dict
        self.zero_value = zero_value

    def assign(self, d, path, value) -> None:
        original = d
        for name in path[:-1]:
            try:
                d = d[name]
            except IndexError:
                for i in range(len(d), int(name) + 1):
                    d.append(self.make_dict())
                d = d[name]
            except KeyError:
                d[name] = self.make_dict()
                d = d[name]
        try:
            d[path[-1]] = value
        except TypeError:
            d = self.make_dict()
            self.assign(original, path[:-1], d)
            d[path[-1]] = value
        except IndexError:
            for i in range(len(d), path[-1] + 1):
                d.append(self.zero_value)
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

    def maybe_remove(self, d, path) -> None:
        container = self.maybe_access_container(d, path)
        if container is not None:
            container.pop(path[-1])

    def exists(self, d, path) -> bool:
        return self.maybe_access_container(d, path) is not None

    def maybe_access(self, d, path, *, default=None):
        if d is None:
            return default
        d = self.maybe_access_container(d, path, default=default)
        if d is default:
            return default
        return d[path[-1]]

    def maybe_access_container(self, d, path, *, default=None):
        for name in path[:-1]:
            try:
                d = d[name]
            except KeyError:
                return default
            except TypeError:
                if d is None:
                    return default
                if not isinstance(d, (list, tuple)):
                    raise
                d = d[int(name)]
        try:
            d[path[-1]]
            return d
        except (KeyError, IndexError):
            return default
        except TypeError:
            if d is None:
                return default
            if not isinstance(d, (list, tuple)):
                raise
            return default


missing = object()


class Scope:
    def __init__(self, init=None, *, accessor=None) -> None:
        self.states: list[object] = []
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

    def push(self, state) -> None:
        self.states.append(state)

    def pop(self) -> None:
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


def dictmap(fn, x, *, mutable: bool = False, with_key: bool = False):
    """Recursively applies a function to the values of a dictionary-like object.

    Args:
        fn: The function to apply to each value.
        x: The dictionary-like object to map.
        mutable: If True, modifies the original object in place.
                 Otherwise, returns a new object.
        with_key: If True, the function `fn` will be called with the key as the first argument
                  and the value as the second argument for dictionary elements.
                  For list elements, it's called with the value only.
                  If False (default), `fn` is always called with the value only.

    Returns:
        The mapped dictionary-like object.
    """
    modifier = get_modifier(mutable=mutable)
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


def get_modifier(*, mutable: bool = False):
    return MutableModifier() if mutable else ImmutableModifier()
