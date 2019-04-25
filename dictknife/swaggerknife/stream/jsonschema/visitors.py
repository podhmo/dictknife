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
        return self.node(ctx, d, self)

    @reify
    def node(self):
        return nodes.SchemaNode()
