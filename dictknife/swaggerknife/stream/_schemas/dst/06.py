# generated from examples/06anonymous.yaml
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


class ComplexStructure(Visitor):
    _schema_type = 'object'
    _roles = ['has_name', 'has_properties']
    _uid = '/examples/06anonymous.yaml#/definitions/ComplexStructure'
    _properties = ['person', 'value']
    _links = ['person']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.ComplexStructure', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'ComplexStructure')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'person' in d:
            ctx.run('person', self.person.visit, d['person'])

    # anonymous definition for 'person' (TODO: nodename)
    class _Person(Visitor):
        _schema_type = 'object'
        _roles = ['has_properties']
        _uid = '/examples/06anonymous.yaml#/definitions/ComplexStructure/person'
        _properties = ['age', 'name']

        @reify
        def node(self):
            return runtime.resolve_node('.nodes._Person', here=__name__, logger=logger)

        def visit(self, ctx: Context, d: dict):
            return self._visit(ctx, d)  # todo: remove this code

        def _visit(self, ctx: Context, d: dict):
            logger.debug("visit: %s", '_Person')
            if self.node is not None:
                self.node.attach(ctx, d, self)


    @reify
    def person(self):
        return runtime.resolve_visitor('person', cls=ComplexStructure._Person, logger=logger)



class Toplevel(Visitor):
    _schema_type = 'object'
    _roles = ['has_properties', 'toplevel_properties']
    _uid = '/examples/06anonymous.yaml#/'
    _properties = ['structure']
    _links = ['structure']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Toplevel', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Toplevel')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'structure' in d:
            ctx.run('structure', self.structure.visit, d['structure'])

    @reify
    def structure(self):
        return runtime.resolve_visitor('structure', cls=ComplexStructure, logger=logger)
