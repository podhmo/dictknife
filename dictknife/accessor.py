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
            d = d[name]
        return d

    def maybe_remove(self, d, path):
        container = self.maybe_access_container(d, path)
        if container is not None:
            container.pop(path[-1])

    def exists(self, d, path):
        return self.maybe_access_container(d, path) is not None

    def maybe_access_container(self, d, path):
        for name in path[:-1]:
            if name not in d:
                return None
            d = d[name]
        if path[-1] not in d:
            return None
        return d
