import operator
from collections import defaultdict


def _to_accesssor(k):
    if callable(k):
        return k
    elif isinstance(k, (str, bytes)):
        return operator.itemgetter(k)
    elif isinstance(k, (list, tuple)):
        # todo: compile?
        return lambda v: tuple([v.get(sk) for sk in k])
    else:
        raise ValueError(k)


class Options:
    def __init__(self, *, missing_value=None, accessor_factory=_to_accesssor) -> None:
        self.missing_value = missing_value
        self.accessor_factory = accessor_factory


_default_options = Options()


def how_inner_join(left, right, left_k, right_k, *, options=_default_options):
    right_cache = defaultdict(list)
    for x in right:
        right_cache[right_k(x)].append(x)

    for lv in left:
        lk = left_k(lv)
        if lk not in right_cache:
            continue
        for rv in right_cache[lk]:
            yield (lv, rv)


def how_left_outer_join(left, right, left_k, right_k, *, options=_default_options):
    missing_value = options.missing_value

    right_cache = defaultdict(list)
    for x in right:
        right_cache[right_k(x)].append(x)

    for lv in left:
        k = left_k(lv)
        if k in right_cache:
            for rv in right_cache[k]:
                yield (lv, rv)
        else:
            yield (lv, missing_value)


def how_right_outer_join(left, right, left_k, right_k, *, options=_default_options):
    for r, l in how_left_outer_join(right, left, right_k, left_k, options=options):
        yield l, r


def how_full_outer_join(left, right, left_k, right_k, *, options=_default_options):
    missing_value = options.missing_value

    right_cache = defaultdict(list)
    for x in right:
        right_cache[right_k(x)].append(x)

    right_used = set()

    for lv in left:
        lk = left_k(lv)
        if lk in right_cache:
            right_used.add(lk)
            for rv in right_cache[lk]:
                yield (lv, rv)
        else:
            yield (lv, missing_value)

    for rv in right:
        rk = right_k(rv)
        if rk in right_used:
            continue
        yield (missing_value, rv)


def join(
    left,
    right,
    *,
    left_on=None,
    right_on=None,
    on=None,
    how=how_inner_join,
    options=_default_options,
):
    assert on or (left_on and right_on)

    if on is not None:
        left_on = right_on = on

    left_on_accessor = options.accessor_factory(left_on)
    right_on_accessor = options.accessor_factory(right_on)
    yield from how(left, right, left_on_accessor, right_on_accessor, options=options)
