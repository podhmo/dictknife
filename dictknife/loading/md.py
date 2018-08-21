# markdown table format
from collections import OrderedDict
import itertools


def load(fp, *, loader=None, errors=None, make_dict=OrderedDict, **kwargs):
    keys = None
    while keys is None:
        line = next(fp)
        if "|" in line:
            keys = [tok.strip() for tok in line.strip("|").split("|")]
    maybe_nums = None
    while maybe_nums is None:
        line = next(fp)
        if "|" in line:
            maybe_nums = [
                tok.rstrip().endswith(":") and tok.lstrip().startswith(":")
                for tok in line.strip("|").split("|")
            ]
    for line in fp:
        if "|" not in line:
            continue
        row = make_dict()
        for name, maybe_num, tok in zip(keys, maybe_nums, line.strip("|").split("|")):
            val = tok.strip()
            if maybe_num:
                if not val:
                    row[name] = None
                elif "." in val:
                    row[name] = float(val)
                else:
                    row[name] = int(val)
            else:
                row[name] = val
        yield row


def dump(rows, fp, *, sort_keys=False, **kwargs):
    if not rows:
        return
    if hasattr(rows, "keys"):
        rows = [rows]  # dict
    elif hasattr(rows, "join"):
        rows = [{"": rows}]  # string

    itr = iter(rows)
    flines, slines = itertools.tee(itr)
    keys = []
    maybe_nums = {}
    for row in flines:
        for k, val in row.items():
            if k not in maybe_nums:
                maybe_nums[k] = False
                keys.append(k)
            if not maybe_nums[k]:
                if isinstance(val, (int, float)):
                    maybe_nums[k] = True

    if sort_keys:
        keys = sorted(keys)

    print("| {} |".format(" | ".join([str(k) for k in keys])), file=fp)
    print(
        "| {} |".format(" | ".join([("---:" if maybe_nums[k] else ":---") for k in keys])), file=fp
    )
    for row in slines:
        print(
            "| {} |".format(" | ".join([("" if k not in row else str(row[k])) for k in keys])),
            file=fp
        )
