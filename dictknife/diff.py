import difflib
import json


def _default_tostring(d, default=str):
    return json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True, default=default)


def diff(d0, d1, tostring=_default_tostring, fromfile="left", tofile="right", n=3, terminator="\n"):
    """fancy diff"""
    s0 = tostring(d0).split(terminator)
    s1 = tostring(d1).split(terminator)
    return difflib.unified_diff(s0, s1, fromfile=fromfile, tofile=tofile, lineterm="", n=n)


if __name__ == "__main__":
    import datetime
    d0 = {"x": datetime.date(2000, 1, 1), "y": {"a": 1, "b": 10}}
    d1 = {"x": datetime.date(2000, 2, 1), "y": {"a": 1, "c": 10}}
    for line in diff(d0, d1):
        print(line)
