from .walkers import LooseDictWalker
from .operators import ANY


class ChainedContext(object):
    def __init__(self, query_list, path=None, value=None, parent=None):
        self.query_list = query_list
        self.path = path or []
        self.value = value
        self.parent = parent

    def push(self, v):
        self.path.append(v)

    def pop(self):
        self.path.pop()

    def new_child(self, query_list=None, path=None, value=None):
        query_list = query_list or self.query_list
        path = path or self.path[:-1]
        return self.__class__(query_list, path=path, value=value, parent=self)

    @property
    def on_container(self):
        if not self.query_list:
            return None
        return self.query_list[0].on_container

    @property
    def on_data(self):
        if not self.query_list:
            return None
        return self.query_list[0].on_data

    def __getitem__(self, i):
        if i <= 0:
            return self
        else:
            ctx = self
            for _ in range(i):
                ctx = ctx.parent
            return

    def __call__(self, walker, fn, value):
        return fn(self, walker, value)


class ChainQuery(object):
    def __init__(self, source, qs, cont=None, on_container=None, on_data=None):
        self.on_container = on_container
        self.on_data = on_data
        self.source = source
        self.qs = qs
        self.cont = cont

    def __repr__(self):
        return "<ChainQury qs={!r}>".format(self.qs)

    def chain(self, qs, on_data=None, on_container=None):
        # constructing query but this is reversed.
        return self.__class__(self.source, qs, cont=self, on_container=on_container, on_data=on_data)

    def flatten(self, r):
        if self.cont is None:
            r.append(self)
            return r
        self.cont.flatten(r)
        r.append(self)
        return r

    def walk(self, d, on_container=None, on_data=None, **kwargs):
        def on_match(ctx, walker, value):
            if ctx.path:
                hook = ctx.parent.on_container or on_container
                if hook is not None:
                    if hook(ctx, walker, value) is False:
                        return
                hook = ctx.parent.on_data or on_data
                if hook is not None:
                    if hook(ctx, walker, value[ctx.path[-1]]) is False:
                        return

            if not ctx.query_list:
                return

            current_query, *rest = ctx.query_list
            new_ctx = ctx.new_child(rest, value=value)
            if callable(current_query.qs):
                current_query.qs(new_ctx, walker, value)
            else:
                qs = [ANY, *current_query.qs]
                walker.walk(qs, value, ctx=new_ctx)

        query_list = self.flatten([])
        ctx = self.source.context_factory(query_list, **kwargs)
        walker = self.source.walker_factory(on_container=on_match)
        return on_match(ctx, walker, d)


class ChainSource(object):
    def __init__(self, query_factory=ChainQuery, walker_factory=LooseDictWalker, context_factory=ChainedContext):
        self.query_factory = query_factory
        self.walker_factory = walker_factory
        self.context_factory = context_factory

    def chain(self, qs, on_container=None, on_data=None):
        return self.query_factory(self, qs, on_container=on_container, on_data=on_data)


chain = ChainSource
