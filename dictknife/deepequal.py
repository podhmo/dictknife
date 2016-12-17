# -*- coding:utf-8 -*-


def deepequal(d0, d1):
    return halfequal(d0, d1) and halfequal(d1, d0)


def halfequal(left, right):
    if hasattr(left, "keys"):
        for k in left.keys():
            if k not in right:
                return False
            return halfequal(left[k], right[k])
    elif isinstance(left, (list, tuple)):
        if len(left) != len(right):
            return False
        for x, y in zip(left, right):
            if not halfequal(x, y):
                return False
    else:
        return left == right
