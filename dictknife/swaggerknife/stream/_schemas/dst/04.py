# generated from examples/04array.yaml
from logging import getLogger
from dictknife.swaggerknife.stream import (
    Visitor,
    runtime
)
from dictknife.langhelpers import reify
from dictknife.swaggerknife.stream.context import Context


logger = getLogger(__name__)  # noqa


class Name(Visitor):
    _schema_type = 'string'
    _roles = {'has_name', 'primitive_type'}
    _uid = '/examples/04array.yaml#/definitions/name'

    @reify  # todo: use Importer
    def node(self):
        try:
            logger.debug("resolve node: %s", 'Name')
            from .nodes import Name
            return Name()
        except ImportError:
            logger.info("resolve node: %s is not found", 'Name')
            return None

    def __call__(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: simplify

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Name')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class People(Visitor):
    _schema_type = 'array'
    _roles = {'has_name', 'has_extra_properties'}
    _uid = '/examples/04array.yaml#/definitions/people'
    _extra_properties = {'items': {'$ref': '#/definitions/person'}}

    @reify  # todo: use Importer
    def node(self):
        try:
            logger.debug("resolve node: %s", 'People')
            from .nodes import People
            return People()
        except ImportError:
            logger.info("resolve node: %s is not found", 'People')
            return None

    def __call__(self, ctx: Context, d: dict):
        return [self._visit(ctx, x) for x in d]

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'People')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class Person(Visitor):
    _schema_type = 'object'
    _roles = {'has_name', 'has_properties'}
    _uid = '/examples/04array.yaml#/definitions/person'
    _properties = {'age', 'parents', 'name'}
    _links = ['name', 'parents']

    @reify  # todo: use Importer
    def node(self):
        try:
            logger.debug("resolve node: %s", 'Person')
            from .nodes import Person
            return Person()
        except ImportError:
            logger.info("resolve node: %s is not found", 'Person')
            return None

    def __call__(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Person')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'name' in d:
            ctx.run('name', self.name.visit, d['name'])
        if 'parents' in d:
            ctx.run('parents', self.parents.visit, d['parents'])

    @reify  # visitor
    def name(self):
        logger.debug("resolve %r node: %s", 'name', 'Name')
        return Name()

    @reify  # visitor
    def parents(self):
        logger.debug("resolve %r node: %s", 'parents', 'People')
        return People()



class toplevel(Visitor):
    _schema_type = 'object'
    _roles = {'toplevel_properties', 'has_properties'}
    _uid = '/examples/04array.yaml#/'
    _properties = {'mother', 'father'}
    _links = ['father', 'mother']

    @reify  # todo: use Importer
    def node(self):
        try:
            logger.debug("resolve node: %s", 'toplevel')
            from .nodes import toplevel
            return toplevel()
        except ImportError:
            logger.info("resolve node: %s is not found", 'toplevel')
            return None

    def __call__(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'toplevel')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'father' in d:
            ctx.run('father', self.father.visit, d['father'])
        if 'mother' in d:
            ctx.run('mother', self.mother.visit, d['mother'])

    @reify  # visitor
    def father(self):
        logger.debug("resolve %r node: %s", 'father', 'Person')
        return Person()

    @reify  # visitor
    def mother(self):
        logger.debug("resolve %r node: %s", 'mother', 'Person')
        return Person()
