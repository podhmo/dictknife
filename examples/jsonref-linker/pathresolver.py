import os.path


class PathResolver(object):
    def __init__(self, path, history=None, registry=None):
        self.registry = registry or {}
        self.history = history or []
        self.path = path

    def __repr__(self):
        return "<Resolver path={!r} at {}>".format(self.path, hex(id(self)))

    def resolve_path(self, path):
        dirname = os.path.dirname(os.path.abspath(self.path))
        return os.path.normpath(os.path.join(dirname, path))

    def open(self):
        return open(self.path)

    def resolve(self, path):
        if path in self.registry:
            return self.registry[path]
        history = self.history[:]
        history.append(path)
        return self.__class__(self.resolve_path(path), history=history, registry=self.registry)
