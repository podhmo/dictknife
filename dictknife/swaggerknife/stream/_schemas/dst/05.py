# generated from examples/05patternProperties.yaml
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


class Schema(Visitor):
    _schema_type = 'object'
    _roles = ['has_extra_properties', 'has_name', 'has_properties']
    _uid = '/examples/05patternProperties.yaml#/definitions/Schema'
    _properties = ['description', 'type']
    _extra_properties = {'additionalProperties': False, 'patternProperties': {'^x-': {}}}

    @reify  # visitor
    def _pattern_properties_regexes(self):
        import re
        r = []
        r.append((re.compile('^x-'), None))
        return r

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Schema', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Schema')
        if self.node is not None:
            self.node.attach(ctx, d, self)

        # patternProperties
        for rx, visitor in self._pattern_properties_regexes:
            for k, v in d.items():
                m = rx.search(rx)
                if m is not None and visitor is not None:
                    ctx.run(k, visitor.visit, v)

        # additionalProperties
        for k, v in d.items():
            if if k in self._properties:
                continue
            for rx, visitor in self._pattern_properties_regexes:
                m = rx.search(rx)
                if m is not None:
                    continue
            logger.warning('unexpected property is found: %r, where=%s', k, self.__class__.__name__)



class Point(Visitor):
    _schema_type = 'integer'
    _roles = ['has_name', 'primitive_type']
    _uid = '/examples/05patternProperties.yaml#/definitions/Point'

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Point', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: simplify

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Point')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class Points(Visitor):
    _schema_type = 'object'
    _roles = ['has_extra_properties', 'has_name']
    _uid = '/examples/05patternProperties.yaml#/definitions/Points'
    _extra_properties = {'patternProperties': {'^point[0-9]+': {'$ref': '#/definitions/Point'}}}

    @reify  # visitor
    def _pattern_properties_regexes(self):
        r = []
        r.append((re.compile('^point[0-9]+'), Point()))
        return r

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Points', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Points')
        if self.node is not None:
            self.node.attach(ctx, d, self)

        # patternProperties
        for rx, visitor in self._pattern_properties_regexes:
            for k, v in d.items():
                m = rx.search(rx)
                if m is not None and visitor is not None:
                    ctx.run(k, visitor.visit, v)



class toplevel(Visitor):
    _schema_type = 'object'
    _roles = ['has_properties', 'toplevel_properties']
    _uid = '/examples/05patternProperties.yaml#/'
    _properties = ['points', 'schema']
    _links = ['schema', 'points']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.toplevel', here=__name__, logger=logger)

    def visit(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'toplevel')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'schema' in d:
            ctx.run('schema', self.schema.visit, d['schema'])
        if 'points' in d:
            ctx.run('points', self.points.visit, d['points'])

    @reify  # visitor
    def schema(self):
        logger.debug("resolve %r node: %s", 'schema', 'Schema')
        return Schema()

    @reify  # visitor
    def points(self):
        logger.debug("resolve %r node: %s", 'points', 'Points')
        return Points()
