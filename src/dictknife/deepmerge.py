import copy
import warnings
import itertools
from functools import partial
from dictknife.langhelpers import make_dict


def _deepmerge_extend(left, right, *, dedup: bool = False):
    if isinstance(left, list):
        r = left[:]
        if isinstance(right, list):
            for e in right:
                if not (dedup and e in r):
                    r.append(e)
        else:
            if not (dedup and right in r):
                r.append(right)
        return r
    elif isinstance(left, tuple):
        r = list(left)
        if isinstance(right, tuple):
            for e in right:
                if not (dedup and e in r):
                    r.append(e)
        else:
            if not (dedup and right in r):
                r.append(right)
        return tuple(r)
    elif hasattr(left, "get"):
        if hasattr(right, "get"):
            r = left.copy()
            for k in right.keys():
                if k in left:
                    r[k] = _deepmerge_extend(r[k], right[k], dedup=dedup)
                else:
                    r[k] = right[k]
            return r
        elif right is None:
            return left
        else:
            raise ValueError(
                "cannot merge dict and non-dict: left=%s, right=%s", left, right
            )
    else:
        return right


def _deepmerge_replace(left, right):
    if hasattr(right, "keys"):
        for k, v in right.items():
            if k in left:
                left[k] = _deepmerge_replace(left[k], v)
            else:
                left[k] = copy.deepcopy(v)
        return left
    elif isinstance(right, (list, tuple)):
        return right[:]
    else:
        return right


def _deepmerge_merge(left, right):
    if isinstance(left, (list, tuple)):
        if not isinstance(right, (list, tuple)):
            right = [right]
        r = []
        for x, y in itertools.zip_longest(left, right):
            if x is None:
                r.append(y)
            elif y is None:
                r.append(x)
            else:
                r.append(_deepmerge_merge(x, y))
        return r
    elif hasattr(left, "get"):
        if hasattr(right, "get"):
            r = left.copy()
            for k in right.keys():
                if k in left:
                    r[k] = _deepmerge_extend(r[k], right[k])
                else:
                    r[k] = right[k]
            return r
        elif right is None:
            return left
        else:
            raise ValueError(
                "cannot merge dict and non-dict: left=%s, right=%s", left, right
            )
    else:
        return right


METHODS = ["merge", "append", "addtoset", "replace"]


def deepmerge(*ds, override: bool = False, method: str = "addtoset"):
    """Recursively merges multiple dictionary-like objects.

    Args:
        *ds: A variable number of dictionary-like objects to merge.
        override (bool, optional): Deprecated. If True, uses the 'replace' method.
            Defaults to False.
        method (str, optional): The merge strategy to use.
            Available methods are:
            - 'addtoset': (Default) Extends lists and sets, ensuring uniqueness in lists.
                          For dicts, merges keys, recursively merging values.
            - 'append': Extends lists and sets without ensuring uniqueness.
                        For dicts, merges keys, recursively merging values.
            - 'merge': For lists and tuples, merges elements pairwise.
                       For dicts, merges keys, recursively merging values using 'append' strategy for lists.
            - 'replace': Replaces the value in the left dictionary with the value from the right.
                         For lists and tuples, the entire list/tuple is replaced.
            Defaults to "addtoset".

    Returns:
        A new dictionary-like object containing the merged data.

    Raises:
        ValueError: If an invalid merge method is provided.
    """
    if len(ds) == 0:
        return make_dict()

    if override:
        warnings.warn(
            "override option is deprecated, will be removed, near future",
            category=DeprecationWarning,
        )
        merge = _deepmerge_replace
    elif method == "addtoset":
        merge = partial(_deepmerge_extend, dedup=True)
    elif method == "append":
        merge = partial(_deepmerge_extend, dedup=False)
    elif method == "merge":
        merge = _deepmerge_merge
    elif method == "replace":
        merge = _deepmerge_replace
    else:
        raise ValueError(
            "unavailable method not in {METHODS!r}".format(METHODS=METHODS)
        )

    left = ds[0].__class__()

    for right in ds:
        if not right:
            continue
        left = merge(left, right)
    return left
