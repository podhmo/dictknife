import typing as t
from dictknife.jsonknife.accessor import AccessingMixin


class Resolver(AccessingMixin):
    def resolve(self, ref: str, format: str = None) -> t.Tuple["Resolver", str]:
        ...
