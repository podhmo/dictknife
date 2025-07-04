import difflib
from dictknife.deepequal import sort_flexibly
from dictknife.transform import str_dict
from typing import Optional, Callable


def diff(
    d0,
    d1,
    tostring: Optional[Callable[..., str]] = None,
    fromfile: str = "left",
    tofile: str = "right",
    n: int = 3,
    terminator: str = "\n",
    normalize: bool = False,
    sort_keys: bool = False,
):
    """Compares two dictionary-like objects and returns a unified diff.

    Args:
        d0: The first dictionary-like object.
        d1: The second dictionary-like object.
        tostring (callable, optional): A function to convert the objects to strings
            for comparison. Defaults to a JSON string representation with indentation.
        fromfile (str, optional): Label for the first object in the diff output.
            Defaults to "left".
        tofile (str, optional): Label for the second object in the diff output.
            Defaults to "right".
        n (int, optional): Number of context lines to show in the diff. Defaults to 3.
        terminator (str, optional): The line terminator used when splitting the
            string representation of objects. Defaults to "\\n".
        normalize (bool, optional): If True, sorts lists and dictionary keys
            (flexibly, attempting to handle unorderable types) before comparison.
            Defaults to False.
        sort_keys (bool, optional): If True, sorts dictionary keys when converting
            objects to strings. This is passed to the `tostring` function.
            Defaults to False.

    Returns:
        An iterator yielding lines of the unified diff.
    """
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
    tostring = tostring or _default_tostring

    s0 = tostring(d0, sort_keys=sort_keys).split(terminator)
    s1 = tostring(d1, sort_keys=sort_keys).split(terminator)
    return difflib.unified_diff(
        s0, s1, fromfile=fromfile, tofile=tofile, lineterm="", n=n
    )


def _default_tostring(d, *, default=str, sort_keys: bool = True):
    import json

    return json.dumps(
        d, indent=2, ensure_ascii=False, sort_keys=sort_keys, default=default
    )


if __name__ == "__main__":
    import datetime

    d0 = {"x": datetime.date(2000, 1, 1), "y": {"a": 1, "b": 10}}
    d1 = {"x": datetime.date(2000, 2, 1), "y": {"a": 1, "c": 10}}
    for line in diff(d0, d1):
        print(line)
