import typing as t
from dictknife.jsonknife import get_resolver
from .event import Event
from .context import Context
from .walker import OpenAPIWalker


def run(src: str):
    for ev in make_stream(src):
        print(ev)


def make_stream(src: str) -> t.Iterable[Event]:
    import threading
    import queue

    q = queue.Queue()

    def provide():
        resolver = get_resolver(src)
        walker = OpenAPIWalker()
        ctx = Context(resolver, emit=q.put)

        try:
            walker.walk(ctx, resolver.doc)
        finally:
            q.put(None)

    th = threading.Thread(target=provide, daemon=True)
    th.start()
    while True:
        v = q.get()
        if v is None:
            break
        yield v
        q.task_done()
    th.join()
