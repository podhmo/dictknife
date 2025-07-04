import unittest
import os.path
import contextlib

here = os.path.abspath(os.path.dirname(__file__))


@contextlib.contextmanager
def _curdir(here):
    curdir = os.path.abspath(".")
    os.chdir(here)
    try:
        yield
    finally:
        os.chdir(curdir)


class fixRelpathTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.relpath import fixpath

        return fixpath(*args, **kwargs)

    def test_it(self) -> None:
        from collections import namedtuple

        C = namedtuple("C", "relpath, where, to, expected")
        with _curdir(here):
            # yapf: disable
            candidates = [
                C(relpath="../a.html", expected="../a.html", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(relpath="../a.html", expected="a.html", where="foo/bar/b.html", to="foo/c.html"),
                C(relpath="../a.html", expected="foo/a.html", where="foo/bar/b.html", to="c.html"),
                C(relpath="a.html", expected="a.html", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(relpath="a.html", expected="bar/a.html", where="foo/bar/b.html", to="foo/c.html"),
                C(relpath="a.html", expected="foo/bar/a.html", where="foo/bar/b.html", to="c.html"),
                C(relpath="boo/a.html", expected="boo/a.html", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(relpath="boo/a.html", expected="bar/boo/a.html", where="foo/bar/b.html", to="foo/c.html"),
                C(relpath="boo/a.html", expected="foo/bar/boo/a.html", where="foo/bar/b.html", to="c.html"),
                C(relpath="a.html", expected="a.html", where="b.html", to="c.html"),
                C(relpath="a.html", expected="a.html", where="b.html", to=os.path.abspath(os.path.join(here, "c.html"))),
                C(relpath="a.html", expected="a.html", where=os.path.abspath(os.path.join(here, "b.html")), to="c.html"),
                C(relpath="a.html", expected="jsonknife/foo/bar/a.html", where="foo/bar/b.html", to="../c.html"),
                C(relpath="a.html", expected="tests/jsonknife/foo/bar/a.html", where="foo/bar/b.html", to="../../c.html"),
            ]
            # yapf: enable
            for c in candidates:
                with self.subTest(relpath=c.relpath, where=c.where, to=c.to):
                    got = self._callFUT(c.relpath, where=c.where, to=c.to)
                    self.assertEqual(got, c.expected)


class fixRefTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.relpath import fixref

        return fixref(*args, **kwargs)

    def test_it(self) -> None:
        from collections import namedtuple

        C = namedtuple("C", "ref, where, to, expected")
        with _curdir(here):
            # yapf: disable
            candidates = [
                C(ref="a.html#/definitions/foo", expected="a.html#/definitions/foo", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(ref="#/definitions/foo", expected="b.html#/definitions/foo", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(ref="../a.html#/definitions/foo", expected="../a.html#/definitions/foo", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(ref="../a.html#/definitions/foo", expected="a.html#/definitions/foo", where="foo/bar/b.html", to="foo/c.html"),
                C(ref="../a.html#/definitions/foo", expected="foo/a.html#/definitions/foo", where="foo/bar/b.html", to="c.html"),
            ]
            # yapf: enable
            for c in candidates:
                with self.subTest(ref=c.ref, where=c.where, to=c.to):
                    got = self._callFUT(c.ref, where=c.where, to=c.to)
                    self.assertEqual(got, c.expected)


class relRefTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.relpath import relref

        return relref(*args, **kwargs)

    def test_it(self) -> None:
        from collections import namedtuple

        C = namedtuple("C", "ref, where, expected")
        with _curdir(here):
            # yapf: disable
            candidates = [
                C(ref="a.html#/definitions/foo", expected=("foo/bar/a.html", "/definitions/foo"), where="foo/bar/b.html"),
                C(ref="#/definitions/foo", expected=("foo/bar/b.html", "/definitions/foo"), where="foo/bar/b.html"),
                C(ref="../a.html#/definitions/foo", expected=("foo/a.html", "/definitions/foo"), where="foo/bar/b.html")
            ]
            # yapf: enable
            for c in candidates:
                with self.subTest(ref=c.ref, where=c.where):
                    got = self._callFUT(c.ref, where=c.where)
                    self.assertEqual(got, c.expected)


class NormpathTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.relpath import normpath

        return normpath(*args, **kwargs)

    def test_it(self) -> None:
        from collections import namedtuple

        C = namedtuple("C", "relpath, where, expected")
        with _curdir(here):
            # yapf: disable
            candidates = [
                C(relpath="a.html", expected=os.path.join(here, "a.html"), where="."),
                C(relpath="a.html", expected=os.path.normpath(os.path.join(here, "../", "a.html")), where="../"),
                C(relpath="a.html", expected=os.path.normpath(os.path.join(here, "foo", "a.html")), where="foo/"),
            ]
            # yapf: enable
            for c in candidates:
                with self.subTest(relpath=c.relpath, where=c.where):
                    got = self._callFUT(c.relpath, where=c.where)
                    self.assertEqual(got, c.expected)


if __name__ == "__main__":
    unittest.main()
