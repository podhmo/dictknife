# -*- coding:utf-8 -*-
import functools


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


def deepmerge(*ds):
    return functools.reduce(_deepmerge, ds)
