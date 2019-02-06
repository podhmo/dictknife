import os.path
from dictknife.langhelpers import pairrsplit

# todo: move module


def fixpath(relpath, *, where, to):
    """
    >>> fixpath('../a.html', where='foo/bar/b.html', to='foo/bar/c.html')
    '../a.html'
    >>> fixpath('../a.html', where='foo/bar/b.html', to='foo/c.html')
    'a.html'
    >>> fixpath('../a.html', where='foo/bar/b.html', to='c.html')
    'foo/a.html'
    """
    return os.path.relpath(
        os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(where), relpath))),
        start=os.path.dirname(to)
    )


def fixref(ref, *, where, to):
    fpath, jsref = pairrsplit(ref, "#")
    if not fpath:
        filepath = os.path.relpath(os.path.abspath(where), start=os.path.dirname(to))
        return "{}#{}".format(filepath, jsref)
    elif fpath == to:
        return "#{}".format(jsref)
    else:
        filepath = fixpath(fpath, where=where, to=to)
        return ref.replace(fpath, filepath)


def relref(ref, *, where):
    fpath, jsref = pairrsplit(ref, "#")
    return relpath(fpath, where=where), jsref


def relpath(fpath, *, where):
    if not fpath:
        return where
    return os.path.normpath(os.path.join(os.path.dirname(where), fpath))


def normpath(relpath, *, where):
    return os.path.normpath(os.path.abspath(os.path.join(where, relpath)))
