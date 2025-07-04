from dictknife.langhelpers import reify


class WrappedExceptionFactory:
    def __init__(self, *, prefix: str = "Wrapped", mixin_class=None) -> None:
        self.prefix = prefix
        self.mixin_class = mixin_class or WrappedMixin
        self.classes: dict[type, type] = {}

    def __call__(self, e: Exception, *, where: str) -> Exception:
        if isinstance(e, self.mixin_class):
            if not hasattr(e, "stack"):
                e.stack = []  # type: ignore[attr-defined]
            e.stack.append(where)  # type: ignore[attr-defined]
            return e

        cls = self.classes.get(e.__class__)
        if cls is None:
            cls = type(
                f"{self.prefix}{e.__class__.__name__}", (WrappedMixin, e.__class__), {}
            )
            self.classes[e.__class__] = cls

        # sync
        exc = cls.__new__(cls).with_traceback(e.__traceback__)  # type: ignore[call-arg, call-overload]
        exc.__dict__.update(e.__dict__)
        if hasattr(e, "args"):
            exc.args = e.args
        return self(exc, where=where)


class WrappedMixin:
    @reify
    def stack(self):
        # This is just a list, but appended from inner to outer, on except-clause, usually.
        return []

    def __str__(self) -> str:
        return f"{super().__str__()} (where={tuple(reversed(self.stack))})"


wrap_exception = WrappedExceptionFactory(prefix="Ex")
