# generated from examples/06anonymous.yaml
from logging import getLogger
from dictknife.swaggerknife.stream import (
    Visitor,
    runtime
)
from dictknife.langhelpers import reify
from dictknife.swaggerknife.stream.context import Context


logger = getLogger(__name__)  # noqa


class ComplexStructure(Visitor):
    _schema_type = 'object'
    _roles = {'has_properties', 'has_name'}
    _uid = '/examples/06anonymous.yaml#/definitions/ComplexStructure'
    _properties = {'person', 'value'}
    _links = ['person']

    @reify  # todo: use Importer
    def node(self):
        try:
            logger.debug("resolve node: %s", 'ComplexStructure')
            from .nodes import ComplexStructure
            return ComplexStructure()
        except ImportError:
            logger.info("resolve node: %s is not found", 'ComplexStructure')
            return None

    def __call__(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'ComplexStructure')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'person' in d:
            ctx.run('person', self.person.visit, d['person'])

    @reify  # visitor
    def person(self):
        logger.debug("resolve %r node: %s", 'person', '_Person')
        return _Person()

    # anonymous definition for 'person' (TODO: nodename)
    class _Person(Visitor):
        _schema_type = 'object'
        _roles = {'has_properties'}
        _uid = '/examples/06anonymous.yaml#/definitions/ComplexStructure/person'
        _properties = {'name', 'age'}

        @reify  # todo: use Importer
        def node(self):
            try:
                logger.debug("resolve node: %s", '_Person')
                from .nodes import _Person
                return _Person()
            except ImportError:
                logger.info("resolve node: %s is not found", '_Person')
                return None

        def __call__(self, ctx: Context, d: dict):
            return self._visit(ctx, d)  # todo: remove this code

        def _visit(self, ctx: Context, d: dict):
            logger.debug("visit: %s", '_Person')
            if self.node is not None:
                self.node.attach(ctx, d, self)


    @reify  # visitor
    def person(self):
        logger.debug("resolve %r node: %s", 'person', '_Person')
        return ComplexStructure._Person()



class toplevel(Visitor):
    _schema_type = 'object'
    _roles = {'has_properties', 'toplevel_properties'}
    _uid = '/examples/06anonymous.yaml#/'
    _properties = {'structure'}
    _links = ['structure']

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
        if 'structure' in d:
            ctx.run('structure', self.structure.visit, d['structure'])

    @reify  # visitor
    def structure(self):
        logger.debug("resolve %r node: %s", 'structure', 'ComplexStructure')
        return ComplexStructure()
