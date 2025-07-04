from ._lazyimport import m
from .raw import setup_extra_parser  # noqa


def load(fp, *, errors=None, **kwargs):
    """Loads YAML data from a file-like object.

    Args:
        fp: A file-like object supporting .read().
        errors: (Unused by ruamel.yaml's load in this context, but kept for API consistency)
                Error handling scheme.
        **kwargs: Additional keyword arguments passed to `ruamel.yaml.YAML().load()`.

    Returns:
        The Python object loaded from YAML.
    """
    return m.yaml.load(fp, **kwargs)


def dump(d, fp, *, sort_keys: bool = False):
    """Dumps a Python object to a file-like object in YAML format.

    Args:
        d: The Python object to dump.
        fp: A file-like object supporting .write().
        sort_keys: If True, dictionary keys will be sorted in the output.
                   Defaults to False.
    """
    return m.yaml.dump(
        d,
        fp,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=sort_keys,
    )
