import difflib
import itertools
from dictknife.deepequal import sort_flexibly
from dictknife.transform import str_dict


def diff_rows(
    d0, d1, *, fromfile="left", tofile="right", diff_key="diff", normalize=False
):
    if normalize:
        d0 = sort_flexibly(d0)
        d1 = sort_flexibly(d1)
        str_dict(d0)
        str_dict(d1)

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
            subrows = diff_rows(
                sd0, sd1, fromfile=fromfile, tofile=tofile, diff_key=diff_key
            )
            for srow in subrows:
                srow["name"] = (
                    "{}/{}".format(i, srow["name"]) if srow["name"] else str(i)
                )
            rows.extend(subrows)
        return rows
    elif hasattr(d0, "keys") or hasattr(d1, "keys"):
        seen = set()
        rows = []
        d0 = d0 or {}
        d1 = d1 or {}
        for k in _all_keys(list(d0.keys()), list(d1.keys())):
            if k in seen:
                continue
            seen.add(k)
            lv = d0.get(k)
            rv = d1.get(k)
            subrows = diff_rows(
                lv, rv, fromfile=fromfile, tofile=tofile, diff_key=diff_key
            )
            for srow in subrows:
                srow["name"] = "{}/{}".format(k, srow["name"]) if srow["name"] else k
            rows.extend(subrows)
        return rows
    elif d0 is None or d1 is None:
        return [{"name": "", fromfile: d0, tofile: d1, diff_key: None}]
    elif isinstance(d0, (int, float)) and isinstance(d1, (int, float)):
        return [{"name": "", fromfile: d0, tofile: d1, diff_key: d1 - d0}]
    else:  # str
        lvs = str(d0)
        rvs = str(d1)
        diff_value = "" if lvs == rvs else "".join(difflib.ndiff(lvs, rvs))
        return [{"name": "", fromfile: d0, tofile: d1, diff_key: diff_value}]


def _all_keys(xs, ys):
    if not xs:
        return ys
    if not ys:
        return xs

    seen = set(xs)
    pre = []
    r = [[x] for x in xs]
    i = 0
    first = True
    for y in ys:
        if y in seen:
            first = False
            while r[i][0] != y:
                i += 1
        else:
            if first:
                pre.append(y)
            else:
                r[i].append(y)
    return itertools.chain(pre, *r)
