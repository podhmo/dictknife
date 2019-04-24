import typing as t
from collections import defaultdict
from dictknife.jsonknife import get_resolver
from .event import Event
from .context import Context
from .visitors import OpenAPIVisitor


def run(src: str):
    for ev in dedup_stream(make_stream(src)):
        print(ev)


def dedup_stream(stream: t.Iterable[Event]) -> t.Iterable[Event]:
    # todo: optimization by walker
    seen = defaultdict(int)
    for ev in stream:
        k = (ev.file, tuple(ev.path))
        if seen[k] == 0:
            yield ev
        seen[k] += 1


def make_stream(src: str) -> t.Iterable[Event]:
    import threading
    import queue

    q = queue.Queue()

    def provide():
        resolver = get_resolver(src)
        visitor = OpenAPIVisitor()
        ctx = Context(resolver, emit=q.put)

        try:
            visitor.visit(ctx, resolver.doc)
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
