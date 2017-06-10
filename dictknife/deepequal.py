# -*- coding:utf-8 -*-
def deepequal(d0, d1, normalize=False):
    if normalize:
        d0 = sort_flexibly(d0)
        d1 = sort_flexibly(d1)
    return halfequal(d0, d1) and halfequal(d1, d0)


def sort_flexibly(d):
    if hasattr(d, "keys"):
        return {k: sort_flexibly(v) for k, v in d.items()}
    elif isinstance(d, (list, tuple)):
        getkey = sort_flexibly_key(d)
        return sorted([sort_flexibly(x) for x in d], key=getkey)
    else:
        return d


def sort_flexibly_key(xs):
    s = set()
    types = set()

    # dict, collection, atom
    for x in xs:
        if hasattr(x, "keys"):
            types.add("dict")
            s.update(x.keys())
        elif isinstance(x, (list, tuple)):
            types.add("list")
        else:
            types.add("atom")
    types = tuple(types)
    if types == ("dict", ):
        ks = sorted(s)
        return lambda d: tuple([d.get(k) for k in ks])
    else:
        return None


def halfequal(left, right):
    if hasattr(left, "keys"):
        for k in left.keys():
            if k not in right:
                return False
            if not halfequal(left[k], right[k]):
                return False
        return True
    elif isinstance(left, (list, tuple)):
        if len(left) != len(right):
            return False
        for x, y in zip(left, right):
            if not halfequal(x, y):
                return False
        return True
    else:
        return left == right
