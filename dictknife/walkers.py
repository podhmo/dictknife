from collections import deque
from .operators import apply


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


class ContainerHandler(object):
    def identity(self, *args):
        return args

    def __call__(self, walker, ctx, d, k):
        return ctx(walker, self.identity, d)


class DataHandler(object):
    def identity(self, *args):
        return args

    def __call__(self, walker, ctx, d, k):
        return ctx(walker, self.identity, d[k])


class DictWalker(object):
    context_factory = PathContext
    handler_factory = ContainerHandler

    def __init__(self, qs, handler=None, context_factory=None):
        self.qs = qs
        self.context_factory = context_factory or self.__class__.context_factory
        self.handler = handler or self.__class__.handler_factory()

    def on_found(self, ctx, d, k):
        yield self.handler(self, ctx, d, k)

    def create_context(self, ctx=None):
        return ctx or self.context_factory()

    def walk(self, d, qs=None, depth=-1, ctx=None):
        qs = qs or self.qs
        ctx = self.create_context(ctx)
        return self._walk(ctx, deque(self.qs), d, depth=depth)

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
                    yield from self._walk(ctx, qs, d[k], depth - 1)
                    if len(qs) == 0:
                        yield from self.on_found(ctx, d, k)
                    qs.appendleft(q)
                else:
                    yield from self._walk(ctx, qs, d[k], depth)
                ctx.pop()
            return
        elif isinstance(d, (list, tuple)):
            for i, e in enumerate(d):
                ctx.push(i)
                yield from self._walk(ctx, qs, e, depth)
                ctx.pop()
            return
        else:
            return

    iterate = walk  # for backward compatibility


LooseDictWalkingIterator = DictWalker  # NOQA for backward comaptibility
