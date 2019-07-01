# todo: rename, shrink? minidict?, or other implementation?
import os
from .langhelpers import make_dict

MAX_DEPTH = int(os.environ.get("DICTKNIFE_MAX_DEPTH") or "-1")


class Describer:
    def __init__(self, *, on_last, max_depth=MAX_DEPTH):
        self.on_last = on_last
        self.max_depth = max_depth

    def _describe(self, d, *, life: int):
        if life == 0:
            return self.on_last(d)
        else:
            if isinstance(d, (list, tuple)):
                return [self._describe(x, life=life - 1) for x in d]
            elif hasattr(d, "keys"):
                r = make_dict()
                for k in d.keys():
                    r[k] = self._describe(d[k], life=life - 1)
                return r
            else:
                return d  # xxx

    def describe(self, d, *, max_depth=None):
        life = max_depth
        if life is None:
            life = self.max_depth
        return self._describe(d, life=life)


def on_last_default(d):
    if isinstance(d, (list, tuple)):
        return {"@type": "list", "@length": len(d), "@max_depth": _depth(d)}
    elif hasattr(d, "keys"):
        return {"@type": "dict", "@keys": sorted(d.keys()), "@max_depth": _depth(d)}
    else:
        return d  # xxx


def _depth(d) -> int:
    if isinstance(d, (list, tuple)):
        return max(_depth(x) for x in d) + 1 if d else 0
    elif hasattr(d, "keys"):
        return max(_depth(v) for v in d.values()) + 1 if d else 0
    else:
        return 0


def describe(d, *, max_depth=None, describer=Describer(on_last=on_last_default)):
    return describer.describe(d)
