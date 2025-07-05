from dictknife.langhelpers import make_dict
from .raw import setup_extra_parser  # noqa
from ._lazyimport import m


def load(fp, *, loader=None, errors=None, object_pairs_hook=make_dict):
    """Loads JSON data from a file-like object.

    Args:
        fp: A file-like object supporting .read().
        loader: (Unused) The loader instance.
        errors: (Unused) Error handling scheme.
        object_pairs_hook: A function that will be called with the result of any
                           JSON object decoded with an ordered list of pairs.
                           The return value of object_pairs_hook will be used instead
                           of the dict. This feature can be used to implement custom
                           decoders. Defaults to `make_dict` from `dictknife.langhelpers`.

    Returns:
        The Python object loaded from JSON.
    """
    return m.json.load(fp, object_pairs_hook=object_pairs_hook)


def dump(
    d,
    fp,
    *,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
    indent: int = 2,
    default=str,
):
    """Dumps a Python object to a file-like object in JSON format.

    Args:
        d: The Python object to dump.
        fp: A file-like object supporting .write().
        ensure_ascii: If True, the output is guaranteed to have all incoming
                      non-ASCII characters escaped. If False (the default),
                      these characters will be output as-is.
        sort_keys: If True (not the default), then dictionary keys will be
                   sorted; otherwise, they will be in insertion order.
        indent: If a non-negative integer (it is 2 by default), then JSON array
                elements and object members will be pretty-printed with that indent
                level. An indent level of 0 will only insert newlines.
                None (the default) selects the most compact representation.
        default: A function that gets called for objects that can't otherwise be
                 serialized. It should return a JSON encodable version of the
                 object or raise a TypeError. Defaults to `str`.
    """
    return m.json.dump(
        d,
        fp,
        ensure_ascii=ensure_ascii,
        indent=indent,
        default=default,
        sort_keys=sort_keys,
    )
