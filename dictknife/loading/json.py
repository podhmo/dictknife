import json
from collections import OrderedDict


def load(fp):
    return json.load(fp, object_pairs_hook=OrderedDict)


def dump(d, fp):
    return json.dump(d, fp, ensure_ascii=False, indent=2, default=str)
