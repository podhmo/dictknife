import os.path


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


def normpath(relpath, *, where):
    return os.path.normpath(os.path.abspath(os.path.join(where, relpath)))
