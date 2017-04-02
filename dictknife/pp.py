import json
import sys
import contextlib
from io import StringIO


def pp(d, out=None):
    out = out or sys.stdout
    try:
        json.dump(d, out, sort_keys=True, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        # xxx: such as `unorderable types: NoneType() < str()`
        json.dump(d, out, sort_keys=False, indent=2, ensure_ascii=False, default=str)


@contextlib.contextmanager
def indent(n):
    buf = StringIO()
    with contextlib.redirect_stdout(buf):
        yield buf
    buf.seek(0)

    prefix = " " * n
    write = sys.stdout.write
    for line in buf:
        write(prefix)
        write(line)
    sys.stdout.flush()
