class Accessor(object):
    def make_dict(self):
        return {}

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

    def maybe_access_container(self, d, path):
        for name in path[:-1]:
            if name not in d:
                return None
            d = d[name]
        if path[-1] not in d:
            return None
        return d
