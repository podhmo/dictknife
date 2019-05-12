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
    _roles = {'has_name', 'has_properties'}
    _uid = '/examples/06anonymous.yaml#/definitions/ComplexStructure'
    _properties = {'person', 'value'}
    _links = ['person']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.ComplexStructure', here=__name__, logger=logger)

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

        @reify
        def node(self):
            return runtime.resolve_node('.nodes._Person', here=__name__, logger=logger)

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

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.toplevel', here=__name__, logger=logger)

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
