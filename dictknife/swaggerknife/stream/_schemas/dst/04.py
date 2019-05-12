# generated from examples/04array.yaml
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
    _uid = '/examples/04array.yaml#/definitions/name'

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Name', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: simplify

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Name')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class People(Visitor):
    _schema_type = 'array'
    _roles = ['has_extra_properties', 'has_name']
    _uid = '/examples/04array.yaml#/definitions/people'
    _extra_properties = {'items': {'$ref': '#/definitions/person'}}

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.People', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return [self._visit(ctx, x) for x in d]

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'People')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class Person(Visitor):
    _schema_type = 'object'
    _roles = ['has_name', 'has_properties']
    _uid = '/examples/04array.yaml#/definitions/person'
    _properties = ['age', 'name', 'parents']
    _links = ['name', 'parents']

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
        if 'parents' in d:
            ctx.run('parents', self.parents.visit, d['parents'])

    @reify
    def name(self):
        return runtime.resolve_visitor('name', cls=Name, logger=logger)

    @reify
    def parents(self):
        return runtime.resolve_visitor('parents', cls=People, logger=logger)



class toplevel(Visitor):
    _schema_type = 'object'
    _roles = ['has_properties', 'toplevel_properties']
    _uid = '/examples/04array.yaml#/'
    _properties = ['father', 'mother']
    _links = ['father', 'mother']

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
        if 'mother' in d:
            ctx.run('mother', self.mother.visit, d['mother'])

    @reify
    def father(self):
        return runtime.resolve_visitor('father', cls=Person, logger=logger)

    @reify
    def mother(self):
        return runtime.resolve_visitor('mother', cls=Person, logger=logger)
