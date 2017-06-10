class Accessor(object):
    def __init__(self, make_dict=dict):
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

    def maybe_access(self, d, path):
        d = self.maybe_access_container(d, path)
        if d is None:
            return None
        return d.get(path[-1])

    def maybe_access_container(self, d, path):
        for name in path[:-1]:
            if name not in d:
                return None
            d = d[name]
        if not d:
            return None
        if path[-1] not in d:
            return None
        return d
