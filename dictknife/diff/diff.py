import difflib
from dictknife.deepequal import sort_flexibly
from ._utils import _normalize_dict


def diff(
    d0,
    d1,
    tostring=None,
    fromfile="left",
    tofile="right",
    n=3,
    terminator="\n",
    normalize=False,
    sort_keys=False,
):
    """fancy diff"""
    if normalize:
        d0 = sort_flexibly(d0)
        d1 = sort_flexibly(d1)
        _normalize_dict(d0)
        _normalize_dict(d1)

    # iterator?
    if hasattr(d0, "__next__"):
        d0 = list(d0)
    if hasattr(d1, "__next__"):
        d1 = list(d1)
    tostring = tostring or _default_tostring

    s0 = tostring(d0, sort_keys=sort_keys).split(terminator)
    s1 = tostring(d1, sort_keys=sort_keys).split(terminator)
    return difflib.unified_diff(s0, s1, fromfile=fromfile, tofile=tofile, lineterm="", n=n)


def _default_tostring(d, *, default=str, sort_keys=True):
    import json
    return json.dumps(d, indent=2, ensure_ascii=False, sort_keys=sort_keys, default=default)


if __name__ == "__main__":
    import datetime
    d0 = {"x": datetime.date(2000, 1, 1), "y": {"a": 1, "b": 10}}
    d1 = {"x": datetime.date(2000, 2, 1), "y": {"a": 1, "c": 10}}
    for line in diff(d0, d1):
        print(line)
