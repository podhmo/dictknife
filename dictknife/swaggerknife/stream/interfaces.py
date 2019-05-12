from .context import Context


# todo: use type_extensions.Protocol
class Visitor:
    def visit(self, ctx: Context, d: dict):
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )


class Node:
    def accept(self, ctx: Context, d: dict, visitor: Visitor):
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )
