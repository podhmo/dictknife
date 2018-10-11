import difflib
import itertools
from dictknife.deepequal import sort_flexibly


def _default_tostring(d, *, default=str, sort_keys=True):
    import json
    return json.dumps(d, indent=2, ensure_ascii=False, sort_keys=sort_keys, default=default)


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

    s0 = tostring(d0, sort_keys=sort_keys).split(terminator)
    s1 = tostring(d1, sort_keys=sort_keys).split(terminator)
    return difflib.unified_diff(s0, s1, fromfile=fromfile, tofile=tofile, lineterm="", n=n)


def diff_rows(d0, d1, *, fromfile="left", tofile="right", diff_key="diff", normalize=False):
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

    if isinstance(d0, (list, tuple)) or isinstance(d1, (list, tuple)):
        rows = []
        for i, (sd0, sd1) in enumerate(itertools.zip_longest(d0 or [], d1 or [])):
            if sd0 is None:
                sd0 = sd1.__class__()
            elif sd1 is None:
                sd1 = sd0.__class__()
            subrows = diff_rows(sd0, sd1, fromfile=fromfile, tofile=tofile, diff_key=diff_key)
            for srow in subrows:
                srow["name"] = "{}/{}".format(i, srow["name"]) if srow["name"] else str(i)
            rows.extend(subrows)
        return rows
    elif hasattr(d0, "keys") or hasattr(d1, "keys"):
        seen = set()
        rows = []
        d0 = d0 or {}
        d1 = d1 or {}
        for k in itertools.chain(d0.keys(), d1.keys()):
            if k in seen:
                continue
            seen.add(k)
            lv = d0.get(k)
            rv = d1.get(k)
            subrows = diff_rows(lv, rv, fromfile=fromfile, tofile=tofile, diff_key=diff_key)
            for srow in subrows:
                srow["name"] = "{}/{}".format(k, srow["name"]) if srow["name"] else k
            rows.extend(subrows)
    elif d0 is None or d1 is None:
        return [{"name": "", fromfile: d0, tofile: d1, diff_key: None}]
    elif isinstance(d0, (int, float)) and isinstance(d1, (int, float)):
        return [{"name": "", fromfile: d0, tofile: d1, diff_key: d1 - d0}]
    else:  # str
        lvs = str(d0)
        rvs = str(d1)
        diff_value = "" if lvs == rvs else "".join(difflib.ndiff(lvs, rvs))
        return [{"name": "", fromfile: d0, tofile: d1, diff_key: diff_value}]
    return rows


if __name__ == "__main__":
    import datetime
    d0 = {"x": datetime.date(2000, 1, 1), "y": {"a": 1, "b": 10}}
    d1 = {"x": datetime.date(2000, 2, 1), "y": {"a": 1, "c": 10}}
    for line in diff(d0, d1):
        print(line)
