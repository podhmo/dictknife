# generated from examples/00simple.yaml
from logging import getLogger
from dictknife.swaggerknife.stream import (
    Visitor,
    runtime
)
from dictknife.langhelpers import reify
from dictknife.swaggerknife.stream.context import Context


logger = getLogger(__name__)  # noqa


class toplevel(Visitor):
    _schema_type = 'object'
    _roles = {'toplevel_properties', 'has_properties'}
    _uid = '/examples/00simple.yaml#/'
    _properties = {'name'}

    @reify
    def node(self):
        return runtime.resolve_node('.nodes.toplevel', here=__name__, logger=logger)

    def __call__(self, ctx: Context, d: dict):
        return self._visit(ctx, d)  # todo: remove this code

    def _visit(self, ctx: Context, d: dict):
        logger.debug("visit: %s", 'toplevel')
        if self.node is not None:
            self.node.attach(ctx, d, self)
