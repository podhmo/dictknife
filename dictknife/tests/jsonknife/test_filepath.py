import unittest
import os.path
here = os.path.abspath(os.path.dirname(__file__))


class fixRelpathTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.filepath import fix_relpath
        return fix_relpath(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple

        C = namedtuple("C", "relpath, where, to, expected")
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


class NormpathTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.filepath import normpath
        return normpath(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple

        C = namedtuple("C", "relpath, where, expected")
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
