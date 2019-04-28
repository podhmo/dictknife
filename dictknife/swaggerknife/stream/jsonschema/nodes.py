import logging
from ..interfaces import Visitor, Node
from ..context import Context
from . import names

logger = logging.getLogger(__name__)


class SchemaNode(Node):
    def __call__(self, ctx: Context, d: dict, visitor: Visitor):
        ctx.emit(d, name=names.schema.object)
