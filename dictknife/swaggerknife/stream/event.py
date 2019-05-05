import typing as t
import json
import os.path  # xxx:
from dictknife.langhelpers import as_jsonpointer

VERBOSE = False


def _serialize_default(ev: "Event", *, verbose=VERBOSE) -> str:
    try:
        d = {"event": ev.name}
        d["uid"] = ev.uid
        d["predicates"] = sorted(ev.predicates)
        if verbose:
            d["history"] = ev.history
        return json.dumps(d)
    except Exception as e:
        d["error"] = repr(e)
        try:
            return json.dumps(d)
        except Exception as e:
            return json.dumps({"error": repr(e), "name": "unexpected"})


class Event:
    __slots__ = (
        "name",
        "path",
        "data",
        "root_file",
        "file",
        "history",
        "predicates",
        "annotated",
    )
    serializer: t.Callable[["Event"], str] = staticmethod(_serialize_default)

    def __init__(
        self,
        *,
        name: str,
        path: t.List[str],
        data: dict,
        file: str,
        root_file: str,
        predicates: t.List[str],
        history: t.List[t.List[str]] = None,
        annotation: dict = None,  # predicate -> any
    ) -> None:
        self.name = name
        self.path = path
        self.data = data
        self.predicates = set(predicates or [])

        self.file = file
        self.root_file = root_file
        self.history = history or []
        self.annotated = annotation

    def __str__(self):
        return self.serializer(self)

    def get_annotated(self, name, *, default=None):
        return self.annotated.get(name, default)

    @property
    def ref(self) -> str:
        return "/".join(as_jsonpointer(x) for x in self.path)

    @property
    def uid(self) -> str:
        uid = "{}#/{}".format(os.path.abspath(self.file), self.ref.lstrip("#/"))
        return uid.replace(os.getcwd(), "")  # xxx
