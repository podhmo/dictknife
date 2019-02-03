def load(fp, *, loader=None, errors=None):
    return fp.read()


def dump(text, fp, sort_keys=False):
    return fp.write(text)


def setup_parser(parser):
    """for dictknife.cliutils.extraarguments"""
    return parser
