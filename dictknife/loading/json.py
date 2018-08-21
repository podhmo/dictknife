from dictknife.langhelpers import make_dict
from ._lazyimport import m


def load(fp, *, loader=None, errors=None):
    return m.json.load(fp, object_pairs_hook=make_dict)


def dump(d, fp, *, sort_keys=False):
    return m.json.dump(d, fp, ensure_ascii=False, indent=2, default=str, sort_keys=sort_keys)
