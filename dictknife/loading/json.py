from dictknife.langhelpers import make_dict
from .raw import setup_extra_parser  # noqa
from ._lazyimport import m


def load(fp, *, loader=None, errors=None, object_pairs_hook=make_dict):
    return m.json.load(fp, object_pairs_hook=object_pairs_hook)


def dump(d, fp, *, ensure_ascii=False, sort_keys=False, indent=2, default=str):
    return m.json.dump(
        d,
        fp,
        ensure_ascii=ensure_ascii,
        indent=indent,
        default=default,
        sort_keys=sort_keys,
    )
