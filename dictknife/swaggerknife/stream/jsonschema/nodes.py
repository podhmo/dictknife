import logging
import copy
from dictknife import DictWalker, And, Accessor, deepmerge
from dictknife.langhelpers import reify
from ..interfaces import Visitor, Node
from ..context import Context, MiniReprDict
from . import names

logger = logging.getLogger(__name__)


_primitive_types = set(["string", "integer", "float", "boolean", "number"])
_combine_types = set(["oneOf", "anyOf", "allof", "not"])
_object_attributes = set(["properties", "additionalProperties", "patternProperties"])
_object_extra_attributes = set(["additionalProperties", "patternProperties"])
_array_attributes = set(["items"])


def _is_string(k, d) -> bool:
    return hasattr(d, "startswith")


def _has_ref(d) -> bool:
    if not hasattr(d, "get"):
        return False
    return "$ref" in d and _is_string("$ref", d["$ref"])


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


class _Expander:
    def __init__(self):
        self._kid = 0
        self.pool = {}  # kid -> object
        self.seen = {}  # resolver, path -> kid

    def genid(self):
        self._kid += 1
        return self._kid

    @reify
    def ref_walker(self):
        return DictWalker([And(["$ref", _is_string])])

    @reify
    def description_walker(self):
        return DictWalker(["description"])

    @reify
    def accessor(self):
        return Accessor()

    def expand(self, ctx: Context, data: dict, *, minimize=True) -> dict:
        pool = self.pool
        seen = self.seen
        genid = self.genid
        accessor = self.accessor
        ref_walker = self.ref_walker

        r = copy.deepcopy(data)
        # todo: merge code with ..context:Context.get_uid()
        # todo: drop description?
        q = []
        q.append((ctx.resolver, r))
        assigned = set()

        while q:
            resolver, d = q.pop()

            for path, sd in ref_walker.walk(d):
                history = []
                kid = genid()

                k = (resolver, "/".join(map(str, path)).lstrip("#/"))
                if k in seen:
                    assigned_kid = seen[k]
                    assigned.add(assigned_kid)
                    sd["$ref"] = f"#/definitions/{assigned_kid}"
                    continue

                seen[k] = kid
                history.append(k)
                stack = [(resolver, sd["$ref"])]

                found = False
                while True:
                    resolver, ref = stack[-1]
                    k = (resolver, ref.lstrip("#/"))
                    if k in seen:
                        assigned_kid = seen[k]
                        assigned.add(assigned_kid)
                        sd["$ref"] = f"#/definitions/{assigned_kid}"
                        for k in history:
                            seen[k] = assigned_kid
                        break

                    seen[k] = kid
                    history.append(k)
                    sresolver, sref = resolver.resolve(ref)

                    sd = sresolver.access_by_json_pointer(sref)
                    if not hasattr(sd, "get") or "$ref" not in sd:
                        found = True
                        stack.append((sresolver, sd))
                        break
                    stack.append((sresolver, sd["$ref"]))

                if not found:
                    continue
                sresolver, sd = stack[-1]
                new_sd = copy.deepcopy(sd)
                if minimize:
                    for _, prop in list(self.description_walker.walk(new_sd)):
                        prop.pop("description")
                pool[kid] = new_sd
                assigned.add(kid)
                accessor.assign(r, path, f"#/definitions/{kid}")
                q.append((sresolver, new_sd))

        if not assigned:
            return r
        return deepmerge(
            r, {"definitions": {str(kid): pool[kid] for kid in sorted(assigned)}}
        )


class SchemaNode(Node):
    @reify
    def expander(self):
        return _Expander()

    def __call__(self, ctx: Context, d: dict, visitor: Visitor, *, retry=False):
        typename = _guess_event_name(d)
        roles = []
        annotations = {}

        extra_properties = {}
        expanded = None

        # has name
        # <file>#/definitions/<name>
        if len(ctx.path) > 2 and ctx.path[-2] == "definitions":
            roles.append(names.roles.has_name)
            annotations[names.annotations.name] = ctx.path[-1]
        elif "definitions" not in ctx.path:
            roles.append(names.roles.toplevel_properties)  # ???
        elif len(ctx.path) > 2:
            if ctx.path[-2] in _object_attributes or ctx.path[-1] in _object_attributes:
                roles.append(names.roles.field_of_something)

        if typename == names.types.array:
            seen = False
            for x in _array_attributes:
                if x not in d:
                    continue
                if not seen:
                    seen = True
                    roles.append(names.roles.has_extra_properties)
                extra_properties[x] = d[x]
        elif typename == names.types.object:
            seen = False
            for x in _object_extra_attributes:
                if x not in d:
                    continue
                if not seen:
                    seen = True
                    roles.append(names.roles.has_extra_properties)
                extra_properties[x] = d[x]
        elif typename in _combine_types:
            roles.append(names.roles.combine_type)
            expanded = self.expander.expand(ctx, d)
            links = []
            for k in ["oneOf", "allOf", "anyOf"]:
                if k in d:
                    for i, prop in enumerate(d[k]):
                        if _has_ref(prop):
                            links.append((i, ctx.get_uid(prop["$ref"])))
                        else:
                            links.append((i, None))
            if links:
                annotations[names.annotations.xxx_of_links] = links

        elif typename in _primitive_types:
            keys = {k: True for k in d.keys()}
            keys.pop("type", None)
            keys.pop("title", None)  # xxx
            keys.pop("default", None)
            if len(keys) == 0:
                roles.append(names.roles.primitive_type)
            else:
                roles.append(names.roles.new_type)

        if "enum" in d:
            roles.append(names.roles.has_enum)
        if "format" in d:
            roles.append(names.roles.has_format)

        # refs (neighbour refs)
        if "properties" in d:
            roles.append(names.roles.has_properties)
            annotations[names.annotations.properties] = set(d["properties"].keys())

            links = []
            # todo: full name (unique)
            for name, prop in d["properties"].items():
                if _has_ref(prop):
                    links.append((name, ctx.get_uid(prop["$ref"])))
            if links:
                annotations[names.annotations.links] = links

        if extra_properties:
            annotations[names.annotations.extra_properties] = MiniReprDict(
                extra_properties
            )
            if "patternProperties" in d:
                links = []
                for name, prop in d["patternProperties"].items():
                    if _has_ref(prop):
                        links.append((name, ctx.get_uid(prop["$ref"])))
                    else:
                        links.append((name, None))  # fixme
                annotations[names.annotations.pattern_properties_links] = links

        if expanded:
            roles.append(names.roles.has_expanded)
            annotations[names.annotations.expanded] = MiniReprDict(expanded)
        ctx.emit(d, name=typename, roles=roles, annotations=annotations)
