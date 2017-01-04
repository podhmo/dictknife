# with walkers


class SimpleContext(object):
    def push(self, ctx):
        pass

    def pop(self):
        pass

    def new_child(self):
        return self.__class__()

    def __call__(self, walker, fn, value):
        return fn(value)


class PathContext(object):
    def __init__(self):
        self.path = []

    def push(self, v):
        self.path.append(v)

    def pop(self):
        self.path.pop()

    def __call__(self, walker, fn, value):
        return fn(self.path, value)


class RecPathContext(PathContext):
    def __call__(self, walker, fn, value):
        return fn(walker, self.path, value)
