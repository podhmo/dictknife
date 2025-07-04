import logging
from dictknife.langhelpers import make_dict
from prestring import NameStore

logger = logging.getLogger(".".join(__name__.split(".")[1:]))


def resolve_type(val):
    if isinstance(val, str):
        return "string", None
    elif isinstance(val, bool):
        return "boolean", None
    elif isinstance(val, int):
        return "integer", None
    elif isinstance(val, float):
        return "number", None
    elif hasattr(val, "keys"):
        return "object", None
    elif isinstance(val, (list, tuple)):
        return "array", None
    else:
        raise ValueError("unsupported for {!r}".format(val))


class NameResolver:
    def __init__(self) -> None:
        self.ns = NameStore()


def make_signature(info):
    if info.get("type2") == "array" or info["type"] == "object":
        return frozenset(
            (k, v["type"], v.get("type2")) for k, v in info["children"].items()
        )
    else:
        return frozenset((info["type"], info.get("type2")))


class Detector:
    resolve_type = staticmethod(resolve_type)

    def make_info(self):
        return {
            "freq": 0,
            "freq2": 0,
            "type": "any",
            "children": make_dict(),
            "values": [],
        }

    def detect(self, d, name: str, info=None):
        s = make_dict()
        s[name] = info or self.make_info()
        path = [name]
        self._detect(d, s[name], name, path=path)
        return s[name]

    def _detect(self, d, s, name: str, path) -> None:
        if hasattr(d, "keys"):
            s["type"] = "object"
            s["name"] = name
            s["freq"] += 1
            for k, v in d.items():
                if k not in s["children"]:
                    s["children"][k] = self.make_info()
                path.append(str(k))
                self._detect(v, s["children"][k], k, path=path)
                path.pop()
        elif isinstance(d, (list, tuple)):
            s["name"] = name
            s["type2"] = "array"
            s["freq2"] += 1
            for i, x in enumerate(d):
                path.append(str(i))
                self._detect(x, s, name, path=path)  # xxx
                path.pop()
        else:
            if d is None:
                s["type2"] = "null"
            else:
                typ, fmt = self.resolve_type(d)
                s["name"] = name
                s["freq"] += 1
                s["type"] = typ
                if fmt is not None:
                    s["format"] = fmt
                s["values"].append(d)
        ref = "#/{}".format("/".join(path))
        logger.debug("ref %s", ref)
        s["ref"] = ref


class Emitter:
    def __init__(self, annotations) -> None:
        self.doc: dict[str, dict] = make_dict(definitions=make_dict())
        self.definitions: dict = self.doc["definitions"]

        self.ns = NameStore()
        self.cw = CommentWriter()
        self.annotations = annotations or {}  # Dict[string, Dict]

    def resolve_name(self, info, fromarray: bool=False, suffix: str=""):
        ref = info["ref"] + suffix
        if ref in self.annotations and "name" in self.annotations[ref]:
            name = self.annotations[ref]["name"]
        else:
            name = info["name"]
            if fromarray:
                name = "{}Item".format(name)

        signature = (fromarray, info["signature"])
        self.ns[signature] = name
        return self.ns[signature]

    def make_schema(self, info, parent=None, fromarray: bool=False):
        info["signature"] = make_signature(info)  # xxx:
        if not fromarray and info.get("type2") == "array":
            return self.make_array_schema(info, parent=parent)
        elif info.get("type") == "object":
            return self.make_object_schema(info, parent=parent, fromarray=fromarray)
        else:
            return self.make_primitive_schema(info)

    def make_array_schema(self, info, parent):
        self.cw.write(info["name"] + "[]", info, parent=parent)
        d: dict[str, object] = make_dict(type="array")
        d["items"] = self.make_schema(info, parent=info, fromarray=True)
        schema_name = self.resolve_name(info, suffix="[]")
        self.definitions[schema_name] = d
        if info["ref"] + "[]" in self.annotations:
            d.update(self.annotations[info["ref"] + "[]"])
            d.pop("name", None)
        return {"$ref": "#/definitions/{name}".format(name=schema_name)}

    def make_object_schema(self, info, parent, fromarray: bool=False):
        if not fromarray:
            self.cw.write(info["name"], info, parent=parent)

        d: dict[str, object] = make_dict(type="object")
        d["properties"] = make_dict()
        from typing import Any
        props: dict[str, Any] = d["properties"]
        for name, value in info["children"].items():
            props[name] = self.make_schema(value, parent=info)
        required = [
            name
            for name, f in info["children"].items()
            if (f.get("freq2") or f["freq"]) == info["freq"]
        ]
        if required:
            d["required"] = required

        if info.get("type2") == "null":
            d["x-nullable"] = True
        schema_name = self.resolve_name(info, fromarray=fromarray)
        self.definitions[schema_name] = d
        if info["ref"] in self.annotations:
            d.update(self.annotations[info["ref"]])
            d.pop("name", None)
        return {"$ref": "#/definitions/{name}".format(name=schema_name)}

    def make_primitive_schema(self, info):
        d = make_dict(type=info["type"])
        if "format" in info:
            d["format"] = info["format"]
        if info["values"]:
            d["example"] = info["values"][0]
        if info.get("type2") == "null":
            d["x-nullable"] = True
        if info["ref"] in self.annotations:
            d.update(self.annotations[info["ref"]])
            d.pop("name", None)
        return d

    def emit(self, root, m):
        self.cw.cm_map[root["name"]] = m
        return self.make_schema(root)


class CommentWriter(object):
    def __init__(self) -> None:
        # Using Any for cm_map entries as they need scope(), stmt() and submodule() methods
        from typing import Any
        self.cm_map: dict[str, Any] = {}

    def write(self, name: str, info, parent=None) -> None:
        if parent is None:
            return
        cm = self.cm_map[parent["name"]]
        with cm.scope():
            cm.stmt("* {}".format(name))
            self.cm_map[info["name"]] = cm.submodule(newline=False)
