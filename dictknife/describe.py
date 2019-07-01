# todo: rename, shrink? minidict?, or other implementation?
import os
from .langhelpers import make_dict

MAX_DEPTH = int(os.environ.get("DICTKNIFE_MAX_DEPTH") or "-1")


def _depth(d) -> int:
    if isinstance(d, (list, tuple)):
        return max(_depth(x) for x in d) + 1 if d else 0
    elif hasattr(d, "keys"):
        return max(_depth(v) for v in d.values()) + 1 if d else 0
    else:
        return 0


def _mini_dict(d) -> dict:
    return {"@type": "dict", "@keys": sorted(d.keys()), "@max_depth": _depth(d)}


def _mini_list(d) -> dict:
    return {"@type": "list", "@length": len(d), "@max_depth": _depth(d)}


def describe(d, *, max_depth=None):
    def _describe(d, *, life):
        if life == 0:
            if isinstance(d, (list, tuple)):
                return _mini_list(d)
            elif hasattr(d, "keys"):
                return _mini_dict(d)
            else:
                return d  # xxx
        else:
            if isinstance(d, (list, tuple)):
                return [_describe(x, life=life - 1) for x in d]
            elif hasattr(d, "keys"):
                r = make_dict()
                for k in d.keys():
                    r[k] = _describe(d[k], life=life - 1)
                return r
            else:
                return d  # xxx

    life = max_depth
    if life is None:
        life = MAX_DEPTH
    return _describe(d, life=life)
