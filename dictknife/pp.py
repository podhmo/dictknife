import sys
import contextlib
from io import StringIO


def pp(d, out=None):
    import json
    out = out or sys.stdout
    try:
        json.dump(d, out, sort_keys=True, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        # xxx: such as `unorderable types: NoneType() < str()`
        json.dump(d, out, sort_keys=False, indent=2, ensure_ascii=False, default=str)


@contextlib.contextmanager
def indent(n, prefix=None, newline=True):
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
