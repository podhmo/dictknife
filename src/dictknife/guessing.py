import re
from .langhelpers import reify
from .accessing import get_modifier


class Guesser:
    def __init__(self, modifier, default=None) -> None:
        self.modifier = modifier
        self.default = default or self.guess_default

    @reify
    def is_bool(self):
        return re.compile(r"[Tt]rue|[Ff]alse").match

    @reify
    def is_float(self):
        return re.compile(r"-?(?:\d*\.\d+(?:e-\d+)?|nan|inf)$").match

    @reify
    def is_int(self):
        return re.compile(r"-?(?:0|[1-9]\d*)$").match

    def is_list(self, v):
        return isinstance(v, (list, tuple))

    def is_dict(self, v):
        return hasattr(v, "keys")

    def guess(self, v):
        if self.is_list(v):
            return self.modifier.modify_list(self.guess, v)
        elif self.is_dict(v):
            return self.modifier.modify_dict(self.guess, v)
        elif not hasattr(v, "strip"):
            return v
        elif self.is_bool(v):
            return v.lower() == "true"
        elif self.is_int(v):
            return int(v)
        elif self.is_float(v):
            return float(v)
        else:
            return self.default(v)

    def guess_default(self, v):
        return v


def guess(d, *, guesser_factory=Guesser, default=None, mutable: bool = False):
    modifier = get_modifier(mutable=mutable)
    g = guesser_factory(modifier, default=default)
    return g.guess(d)
