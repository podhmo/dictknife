# -*- coding:utf-8 -*-
import copy
from collections import OrderedDict


def _deepmerge(left, right):
    if isinstance(left, list):
        r = left[:]
        if isinstance(right, (list, tuple)):
            for e in right:
                if e not in r:
                    r.append(e)
        else:
            if right not in r:
                r.append(right)
        return r
    elif hasattr(left, "get"):
        if hasattr(right, "get"):
            r = left.copy()
            for k in right.keys():
                if k in left:
                    r[k] = _deepmerge(r[k], right[k])
                else:
                    r[k] = right[k]
            return r
        elif right is None:
            return left
        else:
            raise ValueError("cannot merge dict and non-dict: left=%s, right=%s", left, right)
    else:
        return right


def _deepmerge_override(left, right):
    if hasattr(right, "keys"):
        for k, v in right.items():
            if k in left:
                left[k] = _deepmerge_override(left[k], v)
            else:
                left[k] = copy.deepcopy(v)
        return left
    elif isinstance(right, (list, tuple)):
        return right[:]
    else:
        return right


def deepmerge(*ds, override=False, make_dict=OrderedDict):
    if override:
        merge = _deepmerge_override
    else:
        merge = _deepmerge
    left = make_dict()
    for right in ds:
        left = merge(left, right)
    return left
