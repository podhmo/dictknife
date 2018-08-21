import difflib
from .deepequal import sort_flexibly


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
    unsort=False,
):
    """fancy diff"""
    if normalize:
        d0 = sort_flexibly(d0)
        d1 = sort_flexibly(d1)
        _normalize_dict(d0)
        _normalize_dict(d1)
    s0 = tostring(d0, sort_keys=not unsort).split(terminator)
    s1 = tostring(d1, sort_keys=not unsort).split(terminator)
    return difflib.unified_diff(s0, s1, fromfile=fromfile, tofile=tofile, lineterm="", n=n)


def diff_rows(d0, d1, *, fromfile="left", tofile="right", diff_key="diff", normalize=False):
    if normalize:
        d0 = sort_flexibly(d0)
        d1 = sort_flexibly(d1)
        _normalize_dict(d0)
        _normalize_dict(d1)

    rows = []
    if isinstance(d0, (list, tuple)):
        for i, sd0 in enumerate(d0):
            try:
                sd1 = d1[i]
            except IndexError:
                sd1 = sd0.__class__()  # xxx
            subrows = diff_rows(sd0, sd1, fromfile=fromfile, tofile=tofile, diff_key=diff_key)
            for srow in subrows:
                srow["name"] = "{}/{}".format(i, srow["name"])
            rows.extend(subrows)
        return rows

    for k, lv in d0.items():
        rv = d1.get(k)
        row = {"name": k, fromfile: lv, tofile: rv}
        if lv is None or rv is None:
            row[diff_key] = None
            rows.append(row)
        elif isinstance(lv, (int, float)) and isinstance(rv, (int, float)):
            row[diff_key] = rv - lv
            rows.append(row)
        elif hasattr(lv, "keys") or isinstance(lv, (list, tuple)):
            subrows = diff_rows(lv, rv, fromfile=fromfile, tofile=tofile, diff_key=diff_key)
            for srow in subrows:
                srow["name"] = "{}/{}".format(k, srow["name"])
            rows.extend(subrows)
        else:
            lvs = str(lv)
            rvs = str(rv)
            if lvs == rvs:
                row[diff_key] = ""
            else:
                row[diff_key] = "".join(difflib.ndiff(lvs, rvs))
            rows.append(row)
    return rows


if __name__ == "__main__":
    import datetime
    d0 = {"x": datetime.date(2000, 1, 1), "y": {"a": 1, "b": 10}}
    d1 = {"x": datetime.date(2000, 2, 1), "y": {"a": 1, "c": 10}}
    for line in diff(d0, d1):
        print(line)
