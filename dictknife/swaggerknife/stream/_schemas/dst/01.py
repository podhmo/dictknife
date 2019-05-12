# generated from examples/01ref.yaml
from logging import getLogger
from dictknife.swaggerknife.stream.interfaces import (
    Visitor
)
from dictknife.swaggerknife.stream import (
    runtime
)
from dictknife.langhelpers import reify
from dictknife.swaggerknife.stream.context import Context


logger = getLogger(__name__)  # noqa


class Name(Visitor):
    _schema_type = 'string'
    _roles = ['has_name', 'primitive_type']
    _uid = '/examples/01ref.yaml#/definitions/name'

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Name', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: simplify

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Name')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class Person(Visitor):
    _schema_type = 'object'
    _roles = ['has_name', 'has_properties']
    _uid = '/examples/01ref.yaml#/definitions/person'
    _properties = ['age', 'name']
    _links = ['name']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Person', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Person')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'name' in d:
            ctx.run('name', self.name.visit, d['name'])

    @reify
    def name(self):
        return runtime.resolve_visitor('name', cls=Name, logger=logger)



class toplevel(Visitor):
    _schema_type = 'object'
    _roles = ['has_properties', 'toplevel_properties']
    _uid = '/examples/01ref.yaml#/'
    _properties = ['father']
    _links = ['father']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.toplevel', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'toplevel')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'father' in d:
            ctx.run('father', self.father.visit, d['father'])

    @reify
    def father(self):
        return runtime.resolve_visitor('father', cls=Person, logger=logger)
