from .context import Context


class Visitor:
    def __call__(self, ctx: Context, d: dict):
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )

    def visit(self, ctx: Context, d: dict):
        return self(ctx, d)


class Node:
    def __call__(self, ctx: Context, d: dict, visitor: Visitor):
        raise NotImplementedError(
            "please implementation on {self.__class__!r}".foramt(self=self)
        )

    def accept(self, ctx: Context, d: dict, visitor: Visitor):
        return self(ctx, d, visitor)
