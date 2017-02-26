import json
import sys


def pp(d, out=sys.stdout):
    json.dump(d, out, sort_keys=True, indent=2, ensure_ascii=False, default=str)
