import typing as t
from collections import defaultdict
from dictknife.jsonknife import get_resolver
from .event import Event
from .context import Context
from .openapi3 import OpenAPIVisitor


def run(src: str, *, create_visitor=OpenAPIVisitor) -> t.Iterable[Event]:
    return make_stream(src, create_visitor=create_visitor)


def dedup_stream(stream: t.Iterable[Event]) -> t.Iterable[Event]:
    # todo: optimization by walker
    seen = defaultdict(int)
    for ev in stream:
        k = (ev.file, tuple(ev.path))
        if seen[k] == 0:
            yield ev
        seen[k] += 1


def make_stream(src: str, *, create_visitor=None) -> t.Iterable[Event]:
    import threading
    import queue

    create_visitor = create_visitor or OpenAPIVisitor
    q = queue.Queue()

    def provide():
        resolver = get_resolver(src)
        visitor = create_visitor()
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


def main(create_visitor=None) -> t.Iterable[Event]:
    import argparse
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("--log", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log))
    return run(args.src, create_visitor=create_visitor)
