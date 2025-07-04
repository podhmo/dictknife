import unittest


class Tests(unittest.TestCase):
    def _getTarget(self):
        from dictknife import loading

        return loading.dumpfile

    def _callFUT(self, d, *, format):
        from contextlib import redirect_stdout
        from io import StringIO

        o = StringIO()
        with redirect_stdout(o):
            self._getTarget()(d, format=format)
        return o.getvalue()

    def test_dumpfile_with_iterator(self) -> None:
        from collections import namedtuple

        def iterator():
            yield {"name": "foo"}
            yield {"name": "bar"}
            yield {"name": "boo"}

        C = namedtuple("C", "format, output, input")
        # yapf: disable
        candidates = [
            C(format="csv", input=iterator(), output='''"name"\r\n"foo"\r\n"bar"\r\n"boo"\r\n'''),
            C(format="json", input=iterator(), output='''[\n  {\n    "name": "foo"\n  },\n  {\n    "name": "bar"\n  },\n  {\n    "name": "boo"\n  }\n]\n'''),
            C(format="yaml", input=iterator(), output='''- name: foo\n- name: bar\n- name: boo\n'''),
            C(format="md", input=iterator(), output='''| name |\n| :--- |\n| foo |\n| bar |\n| boo |\n'''),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(format=c.format):
                got = self._callFUT(c.input, format=c.format)
                self.assertEqual(got.strip(), c.output.strip())


if __name__ == "__main__":
    unittest.main()
