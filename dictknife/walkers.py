from collections import deque
from .operators import apply


class SimpleContext(object):
    def push(self, ctx):
        pass

    def pop(self, ctx):
        pass

    def __call__(self, fn, walker, value):
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


class LooseDictWalker(object):
    context_factory = PathContext

    def __init__(self, on_container=None, on_data=None):
        self.on_container = on_container
        self.on_data = on_data

    def on_found(self, ctx, d, k):
        if self.on_container is not None:
            ctx(self, self.on_container, d)
        if self.on_data is not None:
            ctx(self, self.on_data, d[k])

    def walk(self, qs, d, depth=-1, ctx=None):
        ctx = ctx or self.context_factory()
        return self._walk(ctx, deque(qs), d, depth=depth)

    def _walk(self, ctx, qs, d, depth):
        if depth == 0:
            return

        if not qs:
            return

        if hasattr(d, "keys"):
            for k in list(d.keys()):
                ctx.push(k)
                if apply(qs[0], k):
                    q = qs.popleft()
                    self._walk(ctx, qs, d[k], depth - 1)
                    if len(qs) == 0:
                        self.on_found(ctx, d, k)
                    qs.appendleft(q)
                else:
                    self._walk(ctx, qs, d[k], depth)
                ctx.pop()
            return d
        elif isinstance(d, (list, tuple)):
            ctx.push("[]")
            for e in d:
                self._walk(ctx, qs, e, depth)
            ctx.pop()
            return d
        else:
            return d
