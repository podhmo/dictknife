from dictknife.langhelpers import make_dict
from ._lazyimport import m


def load(fp, *, loader=None, errors=None):
    return m.json.load(fp, object_pairs_hook=make_dict)


def dump(d, fp, *, ensure_ascii=False, sort_keys=False, indent=2, default=str):
    return m.json.dump(
        d, fp, ensure_ascii=ensure_ascii, indent=indent, default=default, sort_keys=sort_keys
    )
