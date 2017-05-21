def load(fp, *, loader=None):
    return fp.read()


def dump(text, fp):
    return fp.write(text)
