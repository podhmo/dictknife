import logging
from dictknife.langhelpers import reify
from ..context import Context
from ..interfaces import Visitor
from . import nodes

logger = logging.getLogger(__name__)


# visitor = {schemas, paths, all}
# iterator ?


class OpenAPIVisitor(Visitor):
    """openAPI v3 node"""

    @reify
    def components(self):
        return ComponentsVisitor()

    def __call__(self, ctx: Context, d: dict):
        teardown = ctx.push_name(ctx.resolver.name)
        if "components" in d:
            ctx.run("components", self.components, d["components"])
        teardown()


class ComponentsVisitor(Visitor):
    def __call__(self, ctx: Context, d: dict):
        if "schemas" in d:
            ctx.run("schemas", self.on_schemas, d["schemas"])

    def on_schemas(self, ctx: Context, d: dict):
        for name, value in d.items():
            ctx.run(name, self.schema, value)

    @reify
    def schema(self):
        return SchemaVisitor()


class SchemaVisitor(Visitor):
    """
    https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schemaObject
    """

    def __call__(self, ctx: Context, d: dict):
        if "$ref" in d:
            return ctx.resolve_ref(d["$ref"], cont=self)
        self.node(ctx, d, self)

    @reify
    def node(self):
        return nodes.SchemaNode()
