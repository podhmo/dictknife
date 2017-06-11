import difflib
from .deepequal import sort_flexibly


def _default_tostring(d, default=str):
    import json
    return json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True, default=default)


def _normalize_dict(d):  # side effect!
    if hasattr(d, "keys"):
        for k, v in list(d.items()):
            d[str(k)] = d.pop(k)
            _normalize_dict(v)
    elif isinstance(d, (list, tuple)):
        for x in d:
            _normalize_dict(x)


def diff(
    d0,
    d1,
    tostring=_default_tostring,
    fromfile="left",
    tofile="right",
    n=3,
    terminator="\n",
    normalize=False
):
    """fancy diff"""
    if normalize:
        d0 = sort_flexibly(d0)
        d1 = sort_flexibly(d1)
        _normalize_dict(d0)
        _normalize_dict(d1)
    s0 = tostring(d0).split(terminator)
    s1 = tostring(d1).split(terminator)
    return difflib.unified_diff(s0, s1, fromfile=fromfile, tofile=tofile, lineterm="", n=n)


if __name__ == "__main__":
    import datetime
    d0 = {"x": datetime.date(2000, 1, 1), "y": {"a": 1, "b": 10}}
    d1 = {"x": datetime.date(2000, 2, 1), "y": {"a": 1, "c": 10}}
    for line in diff(d0, d1):
        print(line)
