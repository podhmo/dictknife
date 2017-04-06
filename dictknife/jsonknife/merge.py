# -*- coding:utf-8 -*-
# https://tools.ietf.org/html/rfc7396


def merge(d, q, make_dict=dict):
    if not hasattr(q, "items"):
        return q

    if d is None:
        d = make_dict()

    for k, v in q.items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = merge(d.get(k), v, make_dict=make_dict)
    return d
