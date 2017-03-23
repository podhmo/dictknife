import json
import sys


def pp(d, out=sys.stdout):
    try:
        json.dump(d, out, sort_keys=True, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        # xxx: such as `unorderable types: NoneType() < str()`
        json.dump(d, out, sort_keys=False, indent=2, ensure_ascii=False, default=str)
