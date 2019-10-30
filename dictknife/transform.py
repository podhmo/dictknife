from functools import partial
from dictknife.langhelpers import as_jsonpointer as _as_jsonpointer
from dictknife import naming


def _make_key(k0, k1, *, sep="/"):
    if k1 is None:
        return _as_jsonpointer(str(k0))
    return "{}{}{}".format(_as_jsonpointer(str(k0)), sep, k1)


def flatten(d, *, sep="/"):
    if isinstance(d, (list, tuple)):
        return {
            _make_key(i, k, sep=sep): v
            for i, row in enumerate(d)
            for k, v in flatten(row).items()
        }
    elif hasattr(d, "get"):
        return {
            _make_key(k, k2, sep=sep): v2
            for k, v in d.items()
            for k2, v2 in flatten(v, sep=sep).items()
        }
    elif hasattr(d, "__next__"):
        return flatten(list(d), sep=sep)
    else:
        return {None: _as_jsonpointer(str(d))}


def rows(d, *, kname="name", vname="value"):
    return [{kname: k, vname: v} for k, v in d.items()]


def update_keys(d, *, key, coerce=str):  # side effect!
    if hasattr(d, "keys"):
        for k, v in list(d.items()):
            d[key(coerce(k))] = d.pop(k)
            update_keys(v, key=key, coerce=coerce)
    elif isinstance(d, (list, tuple)):
        for x in d:
            update_keys(x, key=key, coerce=coerce)
    return d


normalize_dict = partial(update_keys, key=naming.normalize)
snakecase_dict = partial(update_keys, key=naming.snakecase)
camelcase_dict = partial(update_keys, key=naming.camelcase)
kebabcase_dict = partial(update_keys, key=naming.kebabcase)
pascalcase_dict = partial(update_keys, key=naming.pascalcase)


def only_num(d):
    return {
        k: v
        for k, v in d.items()
        if (isinstance(v, (int, float)) and not isinstance(v, bool))
        or (hasattr(v, "isdigit") and v.isdigit())
    }


def only_str(d):
    return {k: v for k, v in d.items() if isinstance(v, str)}
