from dictknife.jsonknife import get_resolver
from .context import Context
from .walker import OpenAPIWalker


def run(src: str):
    # todo: to generator
    # todo: cache
    # todo: separeted files
    events = []

    def emit(ev):
        print(ev)
        events.append(ev)

    resolver = get_resolver(src)
    walker = OpenAPIWalker()
    ctx = Context(resolver, emit)

    walker.walk(ctx, resolver.doc)
