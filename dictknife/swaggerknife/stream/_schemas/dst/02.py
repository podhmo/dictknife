# generated from examples/02one-of.yaml
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


class One(Visitor):
    _schema_type = 'object'
    _roles = ['has_name', 'has_properties']
    _uid = '/examples/02one-of.yaml#/definitions/one'
    _properties = ['one']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.One', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'One')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class Twotwo(Visitor):
    _schema_type = 'object'
    _roles = ['has_name', 'has_properties']
    _uid = '/examples/02one-of.yaml#/definitions/twotwo'
    _properties = ['two']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Twotwo', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Twotwo')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class Value(Visitor):
    _schema_type = 'oneOf'
    _roles = ['combine_type', 'has_expanded', 'has_name']
    _uid = '/examples/02one-of.yaml#/definitions/value'

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Value', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        # for oneOf (xxx: _case is module global)
        if _case.when(d, '#/definitions/1'):
            return ctx.run(None, self.oneOf0.visit, d)
        if _case.when(d, '#/definitions/2'):
            return ctx.run(None, self.oneOf1.visit, d)
        raise ValueError('unexpected value')  # todo gentle message

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Value')
        if self.node is not None:
            self.node.attach(ctx, d, self)

    @reify  # visitor
    def oneOf0(self):
        logger.debug("resolve %r node: %s", 'oneOf0', 'One')
        return One()

    @reify  # visitor
    def oneOf1(self):
        logger.debug("resolve %r node: %s", 'oneOf1', 'Twotwo')
        return Twotwo()



class toplevel(Visitor):
    _schema_type = 'object'
    _roles = ['has_properties', 'toplevel_properties']
    _uid = '/examples/02one-of.yaml#/'
    _properties = ['value']
    _links = ['value']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.toplevel', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'toplevel')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'value' in d:
            ctx.run('value', self.value.visit, d['value'])

    @reify  # visitor
    def value(self):
        logger.debug("resolve %r node: %s", 'value', 'Value')
        return Value()



# fmt: off
_case = runtime.Case({'definitions': {'1': {'type': 'object', 'properties': {'one': {'type': 'string'}}}, '2': {'type': 'object', 'properties': {'two': {'type': 'string'}}}}})
# fmt: on
