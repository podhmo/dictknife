# generated from examples/03one-of.yaml
from logging import getLogger
from dictknife.swaggerknife.stream import (
    Visitor,
    runtime
)
from dictknife.langhelpers import reify
from dictknife.swaggerknife.stream.context import Context


logger = getLogger(__name__)  # noqa


class Reference(Visitor):
    _schema_type = 'object'
    _roles = {'has_properties', 'has_name'}
    _uid = '/examples/03one-of.yaml#/definitions/Reference'
    _properties = {'$ref'}

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Reference', here=__name__, logger=logger)

    def __call__(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Reference')
        if self.node is not None:
            self.node.attach(ctx, d, self)



class Schema(Visitor):
    _schema_type = 'object'
    _roles = {'has_properties', 'has_name'}
    _uid = '/examples/03one-of.yaml#/definitions/Schema'
    _properties = {'patternProperties', 'properties', 'type', 'additionalProperties'}
    _links = ['patternProperties', 'properties', 'additionalProperties']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.Schema', here=__name__, logger=logger)

    def __call__(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'Schema')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'patternProperties' in d:
            ctx.run('patternProperties', self.patternProperties.visit, d['patternProperties'])
        if 'properties' in d:
            ctx.run('properties', self.properties.visit, d['properties'])
        if 'additionalProperties' in d:
            ctx.run('additionalProperties', self.additionalProperties.visit, d['additionalProperties'])

    @reify  # visitor
    def patternProperties(self):
        logger.debug("resolve %r node: %s", 'patternProperties', '_PatternProperties')
        return _PatternProperties()

    @reify  # visitor
    def properties(self):
        logger.debug("resolve %r node: %s", 'properties', '_Properties')
        return _Properties()

    @reify  # visitor
    def additionalProperties(self):
        logger.debug("resolve %r node: %s", 'additionalProperties', '_AdditionalProperties')
        return _AdditionalProperties()

    # anonymous definition for 'properties' (TODO: nodename)
    class _Properties(Visitor):
        _schema_type = 'object'
        _roles = {'field_of_something', 'has_extra_properties'}
        _uid = '/examples/03one-of.yaml#/definitions/Schema/properties'
        _extra_properties = {'patternProperties': {'^[a-zA-Z0-9\\.\\-_]+$': {'oneOf': [{'$ref': '#/definitions/Schema'}, {'$ref': '#/definitions/Reference'}]}}}

        @reify  # visitor
        def _pattern_properties_regexes(self):
            import re
            r = []
            r.append((re.compile('^[a-zA-Z0-9\\.\\-_]+$'), None))
            return r

        @reify
        def node(self):
            return runtime.resolve_node('.nodes._Properties', here=__name__, logger=logger)

        def __call__(self, ctx: Context, d: dict):
            return self._visit(ctx, d)  # todo: remove this code

        def _visit(self, ctx: Context, d: dict):
            logger.debug("visit: %s", '_Properties')
            if self.node is not None:
                self.node.attach(ctx, d, self)

            # patternProperties
            for rx, visitor in self._pattern_properties_regexes:
                for k, v in d.items():
                    m = rx.search(rx)
                    if m is not None and visitor is not None:
                        ctx.run(k, visitor.visit, v)

        # anonymous definition for 'patternProperties/^[a-zA-Z0-9\\.\\-_]+$' (TODO: nodename)
        class _PatternProperties/^[aZAZ09\.\]+$(Visitor):
            _schema_type = 'oneOf'
            _roles = {'has_expanded', 'field_of_something', 'combine_type'}
            _uid = '/examples/03one-of.yaml#/definitions/Schema/properties/patternProperties/^[a-zA-Z0-9\\.\\-_]+$'

            @reify
            def node(self):
                return runtime.resolve_node('.nodes._PatternProperties/^[aZAZ09\\.\\]+$', here=__name__, logger=logger)

            def __call__(self, ctx: Context, d: dict):
                # for oneOf (xxx: _case is module global)
                if _case.when(d, '#/definitions/1'):
                    return ctx.run(None, self.oneOf0.visit, d)
                if _case.when(d, '#/definitions/3'):
                    return ctx.run(None, self.oneOf1.visit, d)
                raise ValueError('unexpected value')  # todo gentle message

            def _visit(self, ctx: Context, d: dict):
                logger.debug("visit: %s", '_PatternProperties/^[aZAZ09\\.\\]+$')
                if self.node is not None:
                    self.node.attach(ctx, d, self)

            @reify  # visitor
            def oneOf0(self):
                logger.debug("resolve %r node: %s", 'oneOf0', 'Schema')
                return Schema()

            @reify  # visitor
            def oneOf1(self):
                logger.debug("resolve %r node: %s", 'oneOf1', 'Reference')
                return Reference()


        @reify  # visitor
        def patternProperties/^[a-zA-Z0-9\.\-_]+$(self):
            logger.debug("resolve %r node: %s", 'patternProperties/^[a-zA-Z0-9\\.\\-_]+$', '_PatternProperties/^[aZAZ09\\.\\]+$')
            return _Properties._PatternProperties/^[aZAZ09\.\]+$()


    @reify  # visitor
    def properties(self):
        logger.debug("resolve %r node: %s", 'properties', '_Properties')
        return Schema._Properties()

    # anonymous definition for 'patternProperties' (TODO: nodename)
    class _PatternProperties(Visitor):
        _schema_type = 'object'
        _roles = {'field_of_something', 'has_extra_properties'}
        _uid = '/examples/03one-of.yaml#/definitions/Schema/patternProperties'
        _extra_properties = {'additionalProperties': {'oneOf': [{'$ref': '#/definitions/Schema'}, {'$ref': '#/definitions/Reference'}]}}

        @reify
        def node(self):
            return runtime.resolve_node('.nodes._PatternProperties', here=__name__, logger=logger)

        def __call__(self, ctx: Context, d: dict):
            return self._visit(ctx, d)  # todo: remove this code

        def _visit(self, ctx: Context, d: dict):
            logger.debug("visit: %s", '_PatternProperties')
            if self.node is not None:
                self.node.attach(ctx, d, self)

            # additionalProperties
            for k, v in d.items():
                if if k in self._properties:
                    continue
                ctx.run(k, self.additional_properties.visit, v)

        # anonymous definition for 'additionalProperties' (TODO: nodename)
        class _AdditionalProperties(Visitor):
            _schema_type = 'oneOf'
            _roles = {'has_expanded', 'field_of_something', 'combine_type'}
            _uid = '/examples/03one-of.yaml#/definitions/Schema/patternProperties/additionalProperties'

            @reify
            def node(self):
                return runtime.resolve_node('.nodes._AdditionalProperties', here=__name__, logger=logger)

            def __call__(self, ctx: Context, d: dict):
                # for oneOf (xxx: _case is module global)
                if _case.when(d, '#/definitions/1'):
                    return ctx.run(None, self.oneOf0.visit, d)
                if _case.when(d, '#/definitions/3'):
                    return ctx.run(None, self.oneOf1.visit, d)
                raise ValueError('unexpected value')  # todo gentle message

            def _visit(self, ctx: Context, d: dict):
                logger.debug("visit: %s", '_AdditionalProperties')
                if self.node is not None:
                    self.node.attach(ctx, d, self)

            @reify  # visitor
            def oneOf0(self):
                logger.debug("resolve %r node: %s", 'oneOf0', 'Schema')
                return Schema()

            @reify  # visitor
            def oneOf1(self):
                logger.debug("resolve %r node: %s", 'oneOf1', 'Reference')
                return Reference()


        @reify  # visitor
        def additionalProperties(self):
            logger.debug("resolve %r node: %s", 'additionalProperties', '_AdditionalProperties')
            return _PatternProperties._AdditionalProperties()


    @reify  # visitor
    def patternProperties(self):
        logger.debug("resolve %r node: %s", 'patternProperties', '_PatternProperties')
        return Schema._PatternProperties()

    # anonymous definition for 'additionalProperties' (TODO: nodename)
    class _AdditionalProperties(Visitor):
        _schema_type = 'oneOf'
        _roles = {'has_expanded', 'field_of_something', 'combine_type'}
        _uid = '/examples/03one-of.yaml#/definitions/Schema/additionalProperties'

        @reify
        def node(self):
            return runtime.resolve_node('.nodes._AdditionalProperties', here=__name__, logger=logger)

        def __call__(self, ctx: Context, d: dict):
            # for oneOf (xxx: _case is module global)
            if _case.when(d, '#/definitions/15'):
                return ctx.run(None, self.oneOf0.visit, d)
            if _case.when(d, '#/definitions/3'):
                return ctx.run(None, self.oneOf1.visit, d)
            if _case.when(d, '#/definitions/3'):
                return ctx.run(None, self.oneOf2.visit, d)
            raise ValueError('unexpected value')  # todo gentle message

        def _visit(self, ctx: Context, d: dict):
            logger.debug("visit: %s", '_AdditionalProperties')
            if self.node is not None:
                self.node.attach(ctx, d, self)

        @reify  # visitor
        def oneOf0(self):
            logger.debug("resolve %r node: %s", 'oneOf0', '<missing>')
            return <missing>()

        @reify  # visitor
        def oneOf1(self):
            logger.debug("resolve %r node: %s", 'oneOf1', 'Schema')
            return Schema()

        @reify  # visitor
        def oneOf2(self):
            logger.debug("resolve %r node: %s", 'oneOf2', 'Reference')
            return Reference()


    @reify  # visitor
    def additionalProperties(self):
        logger.debug("resolve %r node: %s", 'additionalProperties', '_AdditionalProperties')
        return Schema._AdditionalProperties()



class toplevel(Visitor):
    _schema_type = 'object'
    _roles = {'has_properties', 'toplevel_properties'}
    _uid = '/examples/03one-of.yaml#/'
    _properties = {'definitions', 'properties', 'type'}
    _links = ['definitions', 'properties']

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.toplevel', here=__name__, logger=logger)

    def __call__(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'toplevel')
        if self.node is not None:
            self.node.attach(ctx, d, self)
        if 'definitions' in d:
            ctx.run('definitions', self.definitions.visit, d['definitions'])
        if 'properties' in d:
            ctx.run('properties', self.properties.visit, d['properties'])

    @reify  # visitor
    def definitions(self):
        logger.debug("resolve %r node: %s", 'definitions', '<missing>')
        return <missing>()

    @reify  # visitor
    def properties(self):
        logger.debug("resolve %r node: %s", 'properties', '<missing>')
        return <missing>()

    # anonymous definition for 'definitions' (TODO: nodename)
    class _Definitions(Visitor):
        _schema_type = 'object'
        _roles = {'has_extra_properties'}
        _uid = '/examples/03one-of.yaml#/definitions'
        _extra_properties = {'patternProperties': {'^[a-zA-Z0-9\\.\\-_]+$': {'$ref': '#/definitions/Schema'}}}

        @reify  # visitor
        def _pattern_properties_regexes(self):
            import re
            r = []
            r.append((re.compile('^[a-zA-Z0-9\\.\\-_]+$'), Schema()))
            return r

        @reify
        def node(self):
            return runtime.resolve_node('.nodes._Definitions', here=__name__, logger=logger)

        def __call__(self, ctx: Context, d: dict):
            return self._visit(ctx, d)  # todo: remove this code

        def _visit(self, ctx: Context, d: dict):
            logger.debug("visit: %s", '_Definitions')
            if self.node is not None:
                self.node.attach(ctx, d, self)

            # patternProperties
            for rx, visitor in self._pattern_properties_regexes:
                for k, v in d.items():
                    m = rx.search(rx)
                    if m is not None and visitor is not None:
                        ctx.run(k, visitor.visit, v)


    @reify  # visitor
    def definitions(self):
        logger.debug("resolve %r node: %s", 'definitions', '_Definitions')
        return toplevel._Definitions()



# fmt: off
_case = runtime.Case({'definitions': {'1': {'type': 'object', 'properties': {'type': {'type': 'string'}, 'patternProperties': {'type': 'object', 'additionalProperties': {'oneOf': [{'$ref': '#/definitions/1'}, {'$ref': '#/definitions/3'}]}}, 'properties': {'type': 'object', 'patternProperties': {'^[a-zA-Z0-9\\.\\-_]+$': {'oneOf': [{'$ref': '#/definitions/1'}, {'$ref': '#/definitions/3'}]}}}, 'additionalProperties': {'oneOf': [{'$ref': '#/definitions/2'}, {'$ref': '#/definitions/1'}, {'$ref': '#/definitions/3'}]}}, 'required': ['type']}, '2': {'type': 'boolean'}, '3': {'type': 'object', 'properties': {'$ref': {'type': 'string', 'format': 'uniref'}}, 'required': ['$ref']}, '15': {'type': 'boolean'}}})
# fmt: on
