import logging
from ..interfaces import Visitor, Node
from ..context import Context
from . import names

logger = logging.getLogger(__name__)


_primitive_types = set(["string", "integer", "float", "boolean", "number"])
_combine_types = set(["oneOf", "anyOf", "allof", "not"])
_object_attributes = set(["properties", "additionalProperties", "patternProperties"])
_object_extra_attributes = set(["additionalProperties", "patternProperties"])
_array_attributes = set(["items"])


def _is_ref(d):
    if not hasattr(d, "get"):
        return False
    return "$ref" in d


def _guess_event_name(d, *, retry=False, default=names.types.unknown, strict=False):
    typ = d.get("type", "").lower()
    name = default

    if len(d) == 0:
        return names.types.any

    if typ == "array":
        name = names.types.array
    elif typ == "object":
        name = names.types.object
    elif typ in _primitive_types:
        name = getattr(names.types, typ, default)
    elif "oneOf" in d:
        name = names.types.oneOf
    elif "anyOf" in d:
        name = names.types.anyOf
    elif "allOf" in d:
        name = names.types.allOf
    elif "not" in d:
        name = names.types.not_
    elif not retry:
        if any(x in d for x in _object_attributes):
            d["type"] = "object"
        elif any(x in d for x in _array_attributes):
            d["type"] = "array"
        return _guess_event_name(d, retry=True)

    if strict:
        assert name != default, "unexpected value"
    return name


class SchemaNode(Node):
    def __call__(self, ctx: Context, d: dict, visitor: Visitor, *, retry=False):
        typename = _guess_event_name(d)
        predicates = []
        annotation = {}
        extra_properties = {}

        # has name
        # <file>#/definitions/<name>
        if len(ctx.path) > 2 and ctx.path[-2] == "definitions":
            predicates.append(names.predicates.has_name)
            annotation[names.annotations.name] = ctx.path[-1]
        elif "definitions" not in ctx.path:
            predicates.append(names.predicates.toplevel_properties)  # ???
        elif len(ctx.path) > 2:
            if ctx.path[-2] in _object_attributes or ctx.path[-1] in _object_attributes:
                predicates.append(names.predicates.field_of_something)

        if typename == names.types.array:
            seen = False
            for x in _array_attributes:
                if x not in d:
                    continue
                if not seen:
                    seen = True
                    predicates.append(names.predicates.has_extra_properties)
                extra_properties[x] = d[x]
        elif typename == names.types.object:
            seen = False
            for x in _object_extra_attributes:
                if x not in d:
                    continue
                if not seen:
                    seen = True
                    predicates.append(names.predicates.has_extra_properties)
                extra_properties[x] = d[x]
        elif typename in _combine_types:
            predicates.append(names.predicates.combine_type)
        elif typename in _primitive_types:
            keys = {k: True for k in d.keys()}
            keys.pop("type", None)
            keys.pop("title", None)  # xxx
            keys.pop("default", None)
            if len(keys) == 0:
                predicates.append(names.predicates.primitive_type)
            else:
                predicates.append(names.predicates.new_type)

        if "enum" in d:
            predicates.append(names.predicates.has_enum)
        if "format" in d:
            predicates.append(names.predicates.has_format)

        # refs (neighbour refs)
        if "properties" in d:
            predicates.append(names.predicates.has_properties)
            annotation[names.annotations.properties] = set(d["properties"].keys())

            links = []
            # todo: full name (unique)
            for name, prop in d["properties"].items():
                if _is_ref(prop):
                    links.append((name, ctx.get_uid(prop["$ref"])))
            if links:
                predicates.append(names.predicates.has_links)
                annotation[names.annotations.links] = links

        if extra_properties:
            annotation[names.annotations.extra_properties] = extra_properties
        ctx.emit(d, name=typename, predicates=predicates, annotation=annotation)
