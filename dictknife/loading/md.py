# markdown table format
from dictknife.langhelpers import make_dict
import itertools


def load(fp, *, loader=None, errors=None, make_dict=make_dict, null_value="null", **kwargs):
    keys = None
    while keys is None:
        line = next(fp)
        if "|" in line:
            keys = [tok.strip() for tok in line.strip("|\n").split("|")]
    maybe_nums = None
    while maybe_nums is None:
        line = next(fp)
        if "|" in line:
            maybe_nums = [
                tok.rstrip().endswith(":") and not tok.lstrip().startswith(":")
                for tok in line.strip("|\n").split("|")
            ]

    for line in fp:
        if "|" not in line:
            continue
        row = make_dict()
        for name, maybe_num, tok in zip(keys, maybe_nums, line.strip("|\n").split("|")):
            val = tok.strip()
            if not val:
                continue
            elif val == null_value:
                row[name] = None
            elif maybe_num:
                if "." in val:
                    row[name] = float(val)
                else:
                    row[name] = int(val)
            else:
                row[name] = val
        yield row


def dump(rows, fp, *, sort_keys=False, null_value="null", **kwargs):
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
            "| {} |".format(
                " | ".join(
                    [
                        ("" if k not in row else str(null_value if row[k] is None else row[k]))
                        for k in keys
                    ]
                )
            ),
            file=fp
        )
