import sys
import contextlib


@contextlib.contextmanager
def traceback_shortly(debug):
    try:
        yield
    except Exception as e:
        if debug:
            raise
        else:
            print(
                "\x1b[33m\x1b[1m{e.__class__.__name__}: {e}\x1b[0m".format(e=e),
                file=sys.stderr,
            )
            sys.exit(1)
