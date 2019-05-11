# generated from examples/01ref.yaml
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
    _uid = '/examples/01ref.yaml#/definitions/name'

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



class Person(Visitor):
    _schema_type = 'object'
    _roles = {'has_properties', 'has_name'}
    _uid = '/examples/01ref.yaml#/definitions/person'
    _properties = {'name', 'age'}
    _links = ['name']

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

    @reify  # visitor
    def name(self):
        logger.debug("resolve %r node: %s", 'name', 'Name')
        return Name()



class toplevel(Visitor):
    _schema_type = 'object'
    _roles = {'has_properties', 'toplevel_properties'}
    _uid = '/examples/01ref.yaml#/'
    _properties = {'father'}
    _links = ['father']

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

    @reify  # visitor
    def father(self):
        logger.debug("resolve %r node: %s", 'father', 'Person')
        return Person()
