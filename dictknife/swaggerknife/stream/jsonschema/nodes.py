import logging
from ..interfaces import Visitor, Node
from ..context import Context
from . import names

logger = logging.getLogger(__name__)

# todo
# - additionalPropeties
# - patternPropeties
# - oneOf
# - allOf
# - anyOf


class ReferenceNode(Node):
    def __call__(self, ctx: Context, d: dict, visitor: Visitor):
        if "$ref" in d:
            return ctx.resolve_ref(d["$ref"], cont=self)
        raise RuntimeError("invalid")


class SchemaNode(Node):
    def __call__(self, ctx: Context, d: dict, visitor: Visitor):
        # xxx
        if not hasattr(d, "get"):
            return

        typ = d.get("type")
        if typ == "array":
            return self.on_array(ctx, d, visitor)
        elif typ == "object" or "properties" in d:
            return self.on_object(ctx, d, visitor)
        else:
            return self.on_primitive(ctx, d, visitor)

    def on_primitive(self, ctx: Context, d: dict, visitor: Visitor):
        ctx.emit(d, name=names.schema.primitive)

    def on_array(self, ctx: Context, d: dict, visitor: Visitor):
        if "items" in d:
            ctx.run("items", visitor, d["items"])
        ctx.emit(d, name=names.schema.array)

    def on_object(self, ctx: Context, d: dict, visitor: Visitor):
        if "properties" in d:
            for name, prop in d["properties"].items():
                ctx.run(name, visitor, prop)
        ctx.emit(d, name=names.schema.object)
