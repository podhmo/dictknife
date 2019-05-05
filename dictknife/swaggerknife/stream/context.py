import typing as t
import os.path  # xxx
from dictknife.jsonknife.accessor import AccessingMixin
from dictknife.langhelpers import pairrsplit
from dictknife.jsonknife.relpath import fixref
from .event import Event


class Resolver(AccessingMixin):
    def resolve(self, ref: str, format: str = None) -> t.Tuple["Resolver", str]:
        ...


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
        self._seen = set()

    @property
    def path(self) -> t.List[str]:
        return self.history[-1]

    @property
    def resolver(self) -> Resolver:
        return self.resolvers[-1]

    def get_uid(self, ref, *, to=None) -> str:
        uid = fixref(ref, where=self.filename, to=".")
        filepath, jsref = pairrsplit(uid, "#")
        uid = "{}#/{}".format(
            os.path.normpath(os.path.abspath(filepath)), jsref.lstrip("/")
        )
        return uid.replace(os.getcwd(), "")  # xxx

    def push_name(self, name: str) -> t.Callable[[None], None]:
        self.path.append(name)
        return self._push_name_teardown

    def _push_name_teardown(self):
        return self.path.pop()

    def run(self, name, fn, *args, **kwargs):
        teardown = None
        try:
            teardown = self.push_name(name)
            return fn(self, *args, **kwargs)
        finally:
            if teardown is not None:
                teardown()

    def resolve_ref(self, ref, *, cont) -> None:
        sd, query, teardown = self._resolve(ref)
        k = (self.resolver.name, query)
        try:
            if k in self._seen:
                return
            self._seen.add(k)
            cont(self, sd)
        finally:
            teardown()

    def _resolve(self, ref) -> t.Tuple[dict, t.Callable[[], None]]:
        subresolver, query = self.resolver.resolve(ref)
        self.resolvers.append(subresolver)
        d = subresolver.doc
        if query:
            d = subresolver.access_by_json_pointer(query)

        path = [subresolver.name]
        if query:
            path.extend(query.lstrip("#/").split("/"))

        self.history.append(path)
        return d, query, self._resolve_teardown

    def _resolve_teardown(self):
        self.history.pop()
        self.resolvers.pop()

    @property
    def filename(self) -> str:
        return self.resolver.name

    @property
    def root_filename(self) -> str:
        return self.resolvers[0].name

    def emit(
        self,
        data: dict,
        *,
        name: str,
        predicates: t.List[str] = None,
        annotation: dict = None
    ) -> None:
        self._emit(
            Event(
                name=name,
                path=self.path[1:],
                data=data,
                file=self.filename,
                root_file=self.root_filename,
                history=self.history,
                predicates=predicates or [],
                annotation=annotation or {},
            )
        )
