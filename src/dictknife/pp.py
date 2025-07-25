import sys
import contextlib
from io import StringIO
from typing import Optional


def pp(d, out=None) -> None:
    """Pretty prints a dictionary-like object to the specified output stream.

    It uses JSON formatting with indentation and sorted keys (if possible).

    Args:
        d: The dictionary-like object to print.
        out (file-like object, optional): The output stream.
            Defaults to sys.stdout.
    """
    import json

    out = out or sys.stdout
    try:
        json.dump(d, out, sort_keys=True, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        # xxx: such as `unorderable types: NoneType() < str()`
        json.dump(d, out, sort_keys=False, indent=2, ensure_ascii=False, default=str)


@contextlib.contextmanager
def indent(n, prefix: Optional[str] = None, newline: bool = True):
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        yield buf
    buf.seek(0)

    padding = " " * n
    write = sys.stdout.write

    if prefix is not None:
        write(prefix)
        if newline:
            write("\n")

    for line in buf:
        write(padding)
        write(line)
    sys.stdout.flush()
