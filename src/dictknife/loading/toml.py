from ._lazyimport import m
from .raw import setup_extra_parser  # noqa


def load(fp, *, loader=None, errors=None, **kwargs):
    """Loads TOML data from a file-like object.

    For specific dependency requirements and installation, refer to the `Loader`
    class documentation or the project's main documentation.

    Args:
        fp: A file-like object supporting .read().
        loader: (Unused) The loader instance.
        errors: (Unused) Error handling scheme.
        **kwargs: Additional keyword arguments passed to `tomlkit.load()`.

    Returns:
        The Python object loaded from TOML.
    """
    return m.toml.load(fp, **kwargs)


def dump(d, fp, *, sort_keys: bool = False, **kwargs):
    """Dumps a Python object to a file-like object in TOML format.

    For specific dependency requirements and installation, refer to the `Dumper`
    class documentation or the project's main documentation.

    Note: `tomlkit.dump` does not directly support a `sort_keys` argument.
    If `sort_keys` is True, the input dictionary `d` should be sorted before calling this function,
    for example, by using `collections.OrderedDict(sorted(d.items()))` if you need to control
    the top-level key order. `tomlkit` itself preserves insertion order for dictionaries by default.

    Args:
        d: The Python object to dump.
        fp: A file-like object supporting .write().
        sort_keys: If True, it's recommended to pre-sort the dictionary `d` as `tomlkit`
                   itself doesn't use this argument but respects input order.
        **kwargs: Additional keyword arguments passed to `tomlkit.dump()`.
    """
    # `tomlkit.dump` does not have a sort_keys parameter.
    # The `sort_keys` argument in `dictknife`'s interface is a general one.
    # For `tomlkit`, if sorting is desired, the input `d` should be an ordered dict
    # or sorting should be handled before this call. We'll pass `sort_keys` along
    # in case a future version of tomlkit or a different underlying library handles it,
    # but it's not currently used by tomlkit.
    if "sort_keys" in kwargs and sort_keys: # pragma: no cover
        # this path is not typically hit because dispatcher usually filters sort_keys
        pass
    elif sort_keys and "sort_keys" not in kwargs: # pragma: no cover
        # This is a hint; actual sorting must be done on `d` before this call.
        # Consider if a warning or specific handling is needed if `sort_keys` is True.
        pass

    # Actual tomlkit dump call, kwargs are passed through.
    return m.toml.dump(d, fp, **kwargs)
