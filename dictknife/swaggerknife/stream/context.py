import typing as t
from .resolver import Resolver
from .event import Event


class Context:
    def __init__(
        self,
        resolver: Resolver,
        emit: t.Callable[[Event], None],
        *,
        history: t.List[t.List[str]] = None
    ):
        self.resolvers = [resolver]
        self._emit = emit
        self.history = history or [[]]

    @property
    def path(self) -> t.List[str]:
        return self.history[-1]

    @property
    def resolver(self) -> Resolver:
        return self.resolvers[-1]

    def push(self, name: str) -> t.Callable[[None], None]:
        self.path.append(name)
        return self._push_teardown

    def _push_teardown(self):
        return self.path.pop()

    pop = _push_teardown

    def run(self, name, fn, *args, **kwargs):
        v = None
        teardown = None
        try:
            teardown = self.push(name)
            v = fn(self, *args, **kwargs)
        finally:
            if teardown is not None:
                teardown()
        return v

    def resolve(self, ref) -> t.Tuple[dict, t.Callable[[], None]]:
        subresolver, query = self.resolver.resolve(ref)
        self.resolvers.append(subresolver)
        d = subresolver.doc
        if query:
            d = subresolver.access_by_json_pointer(query)

        path = [subresolver.name]
        if query:
            path.extend(query.lstrip("#/").split("/"))

        self.history.append(path)
        return d, self._resolve_teardown

    def _resolve_teardown(self):
        self.history.pop()
        self.resolvers.pop()

    @property
    def filename(self) -> str:
        return self.resolver.name

    def emit(self, data: dict, *, name: str) -> None:
        self._emit(
            Event(
                name=name,
                path=self.path[1:],
                data=data,
                file=self.filename,
                history=self.history,
            )
        )
