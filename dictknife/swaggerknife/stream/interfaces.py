from .context import Context


# todo: use type_extensions.Protocol
class Visitor:
    def __call__(self, ctx: Context, d: dict):
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )

    def visit(self, ctx: Context, d: dict):
        return self(ctx, d)

    @property
    def registry(self) -> "Registry":
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )


class Node:
    def __call__(self, ctx: Context, d: dict, visitor: Visitor):
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )

    def accept(self, ctx: Context, d: dict, visitor: Visitor):
        return self(ctx, d, visitor)


class Registry:
    def resolve_visitor_from_ref(self, s: str) -> Visitor:
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )

    def resolve_node_from_string(self, s: str) -> Node:
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )
