def load(fp, *, loader=None):
    return fp.read()


def dump(text, fp, sort_keys=False):
    return fp.write(text)
