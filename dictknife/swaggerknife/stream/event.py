import typing as t
import json
import pathlib
from dictknife.langhelpers import as_jsonpointer

VERBOSE = False


def _serialize_default(ev: "Event", *, verbose=VERBOSE) -> str:
    try:
        d = {"event": ev.name}
        d["ref"] = ev.fullref
        d["flavors"] = sorted(ev.flavors)
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
    __slots__ = ("name", "path", "data", "file", "history", "flavors", "annotated")
    serializer: t.Callable[["Event"], str] = staticmethod(_serialize_default)

    def __init__(
        self,
        *,
        name: str,
        path: t.List[str],
        data: dict,
        file: str,
        flavors: t.List[str],
        history: t.List[t.List[str]] = None,
        annotation: dict = None,  # flavor -> any
    ) -> None:
        self.name = name
        self.path = path
        self.data = data
        self.flavors = set(flavors or [])

        self.file = file
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
    def fullref(self) -> str:
        file = str(pathlib.Path(self.file).relative_to(pathlib.Path().absolute()))
        ref = self.ref
        if not ref:
            return file
        return "{file}#/{ref}".format(file=file, ref=ref)
