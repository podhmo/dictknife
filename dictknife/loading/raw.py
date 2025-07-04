def load(fp, *, loader=None, errors=None):
    return fp.read()


def dump(text: str, fp, sort_keys: bool=False):
    return fp.write(text)


def setup_extra_parser(parser):
    """for dictknife.cliutils.extraarguments"""
    return parser
