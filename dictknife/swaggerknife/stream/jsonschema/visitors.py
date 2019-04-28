import logging
from dictknife.langhelpers import reify
from ..context import Context
from ..interfaces import Visitor
from . import nodes

logger = logging.getLogger(__name__)


# visitor = {schemas, paths, all}
# iterator ?


class ToplevelVisitor(Visitor):
    """openAPI v3 node"""

    @reify
    def schema(self):
        return SchemaVisitor()

    def __call__(self, ctx: Context, d: dict):
        teardown = ctx.push_name(ctx.resolver.name)
        self.schema.visit(ctx, d)
        teardown()


class SchemaVisitor(Visitor):
    def __call__(self, ctx: Context, d: dict):
        if hasattr(d, "get") and "$ref" in d:
            return ctx.resolve_ref(d["$ref"], cont=self)

        if not hasattr(d, "get"):
            return

        if "properties" in d:
            for name, prop in d["properties"].items():
                ctx.run(name, self, prop)
        for k in ["additionalProperties", "items"]:
            if k in d:
                ctx.run(k, self, d[k])
        if "patternProperties" in d:
            teardown = ctx.push_name("patternProperties")
            try:
                for k, v in d["patternProperties"].items():
                    ctx.run(k, self, v)
            finally:
                teardown()
        for k in ["oneOf", "allOf", "anyOf"]:
            if k in d:
                teardown = ctx.push_name(k)
                try:
                    for i, x in enumerate(d[k]):
                        ctx.run(i, self, x)
                finally:
                    teardown()
        return self.node(ctx, d, self)

    @reify
    def node(self):
        return nodes.SchemaNode()
