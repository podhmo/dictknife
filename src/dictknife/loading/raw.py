def load(fp, *, loader=None, errors=None) -> str:
    """Loads raw text content from a file-like object.

    Args:
        fp: A file-like object supporting .read().
        loader: (Unused) The loader instance.
        errors: (Unused) Error handling scheme.

    Returns:
        The raw string content read from the file.
    """
    return fp.read()


def dump(text: str, fp, sort_keys: bool = False) -> int:
    """Dumps raw text content to a file-like object.

    Args:
        text: The string content to write.
        fp: A file-like object supporting .write().
        sort_keys: (Unused) Whether to sort keys.

    Returns:
        The number of characters written.
    """
    return fp.write(text)


def setup_extra_parser(parser):
    """Sets up extra parser arguments for raw format.

    This function is intended for use with `dictknife.cliutils.extraarguments`.
    Currently, it's a no-op for the raw format.

    Args:
        parser: The argparse parser instance.

    Returns:
        The parser instance.
    """
    return parser
