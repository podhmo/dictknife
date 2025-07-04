from functools import partial
from dictknife.langhelpers import as_jsonpointer as _as_jsonpointer
from dictknife.langhelpers import as_path_node as _as_path_node
from dictknife import accessing
from dictknife import naming


def _make_key(k0, k1, *, sep: str="/"):
    if k1 is None:
        return _as_jsonpointer(str(k0))
    return "{}{}{}".format(_as_jsonpointer(str(k0)), sep, k1)


def unflatten(d, *, sep: str="/", accessor=accessing.Accessor()):
    r = accessor.make_dict()
    for k, v in d.items():
        accessor.assign(r, [_as_path_node(x) for x in k.split(sep)], v)
    return _fix_unflatten_list(r)


def _fix_unflatten_list(d):
    if hasattr(d, "keys"):
        for k in list(d.keys()):
            d[k] = _fix_unflatten_list(d[k])

        # list ?
        if "0" in d and str(len(d) - 1) in d:
            r = []
            for i in range(len(d)):
                k = str(i)
                if k not in d:
                    return d
                r.append(d[k])
            return r
    return d


def flatten(d, *, sep: str="/"):
    if isinstance(d, (list, tuple)):
        return {
            _make_key(i, k, sep=sep): v
            for i, row in enumerate(d)
            for k, v in flatten(row, sep=sep).items()
        }
    elif hasattr(d, "get"):
        return {
            _make_key(k, k2, sep=sep): v2
            for k, v in d.items()
            for k2, v2 in flatten(v, sep=sep).items()
        }
    elif hasattr(d, "__next__"):
        # todo: as generator
        return flatten(list(d), sep=sep)
    else:
        # todo: peformance improvement
        return {None: _as_jsonpointer(d) if hasattr(d, "replace") else d}


def rows(d, *, kname: str="name", vname: str="value"):
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


str_dict = partial(update_keys, key=str)
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


def shrink(
    d,
    *,
    max_length_of_string: int = 100,
    cont_suffix: str = "...",
    max_length_of_list: int = 3,
    with_tail: bool = False,
    mutable: bool = False,
):
    # todo: random select
    # todo: cont suffix for list
    from dictknife.accessing import get_modifier

    modifier = get_modifier(mutable=mutable)

    def _map(d):
        if isinstance(d, (list, tuple)):
            xs = d
            if len(xs) > max_length_of_list:
                xs = d[:max_length_of_list]
            if with_tail:
                xs.extend(d[-max_length_of_list:])
            return modifier.modify_list(_map, xs)
        elif hasattr(d, "keys"):
            return modifier.modify_dict(_map, d)
        elif isinstance(d, str):
            s = d
            if len(s) > max_length_of_string:
                s = s[:max_length_of_string] + cont_suffix
            return s
        else:
            return d

    return _map(d)
