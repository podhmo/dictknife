import logging
from dictknife.langhelpers import reify
from .context import Context

logger = logging.getLogger(__name__)


class EventName:
    class schema:
        primitive = "primitiveSchema"
        object = "objectSchema"
        array = "arraySchema"


# walker = {schemas, paths, all}
# iterator ?


class Walker:
    def __call__(self, ctx: Context, d: dict):
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )

    def walk(self, ctx: Context, d: dict):
        return self(ctx, d)


class OpenAPIWalker(Walker):
    """openAPI v3 node"""

    @reify
    def components(self):
        return ComponentsWalker()

    def __call__(self, ctx: Context, d: dict):
        teardown = ctx.push(ctx.resolver.name)
        if "components" in d:
            ctx.run("components", self.components, d["components"])
        teardown()


class ComponentsWalker(Walker):
    def __call__(self, ctx: Context, d: dict):
        if "schemas" in d:
            ctx.run("schemas", self.on_schemas, d["schemas"])

    def on_schemas(self, ctx: Context, d: dict):
        for name, value in d.items():
            ctx.run(name, self.schema, value)

    @reify
    def schema(self):
        return SchemaWalker()


class SchemaWalker(Walker):
    """
    https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#schemaObject
    """

    def __call__(self, ctx: Context, d: dict):
        if "$ref" in d:
            return ctx.resolve_ref(d["$ref"], cont=self)

        typ = d.get("type", "object")
        if typ == "array":
            return self.on_array(ctx, d)
        elif typ == "object":
            return self.on_object(ctx, d)
        else:
            return self.on_primitive(ctx, d)

    def on_primitive(self, ctx: Context, d: dict):
        ctx.emit(d, name=EventName.schema.primitive)

    def on_array(self, ctx: Context, d: dict):
        if "items" in d:
            ctx.run("items", self, d["items"])
        ctx.emit(d, name=EventName.schema.array)

    def on_object(self, ctx: Context, d: dict):
        if "properties" in d:
            for name, prop in d["properties"].items():
                ctx.run(name, self, prop)
        ctx.emit(d, name=EventName.schema.object)
