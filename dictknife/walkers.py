from collections import deque
from .operators import apply
from .contexts import PathContext

# - LooseDictWalker is like a internal iterator
# - LooseDictWalkingIterator is like a external iterator
# xxx: in the future, which one is deleted.


class LooseDictWalker(object):
    context_factory = PathContext

    def __init__(self, on_container=None, on_data=None, context_factory=None):
        self.on_container = on_container
        self.on_data = on_data
        self.context_factory = context_factory or self.__class__.context_factory

    def on_found(self, ctx, d, k):
        if self.on_container is not None:
            ctx(self, self.on_container, d)
        if self.on_data is not None:
            ctx(self, self.on_data, d[k])

    def create_context(self, ctx=None):
        return ctx or self.context_factory()

    def walk(self, qs, d, depth=-1, ctx=None):
        ctx = self.create_context(ctx)
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
            return
        elif isinstance(d, (list, tuple)):
            ctx.push("[]")
            for e in d:
                self._walk(ctx, qs, e, depth)
            ctx.pop()
            return
        else:
            return


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


class LooseDictWalkingIterator(object):
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

    def iterate(self, d, qs=None, depth=-1, ctx=None):
        qs = qs or self.qs
        ctx = self.create_context(ctx)
        return self._iterate(ctx, deque(self.qs), d, depth=depth)

    def _iterate(self, ctx, qs, d, depth):
        if depth == 0:
            return

        if not qs:
            return

        if hasattr(d, "keys"):
            for k in list(d.keys()):
                ctx.push(k)
                if apply(qs[0], k):
                    q = qs.popleft()
                    yield from self._iterate(ctx, qs, d[k], depth - 1)
                    if len(qs) == 0:
                        yield from self.on_found(ctx, d, k)
                    qs.appendleft(q)
                else:
                    yield from self._iterate(ctx, qs, d[k], depth)
                ctx.pop()
            return
        elif isinstance(d, (list, tuple)):
            ctx.push("[]")
            for e in d:
                yield from self._iterate(ctx, qs, e, depth)
            ctx.pop()
            return
        else:
            return
