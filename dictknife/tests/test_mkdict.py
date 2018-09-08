import unittest


class ParseTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.mkdict import parse
        return parse(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple
        C = namedtuple("C", "input, output")
        candidates = [
            C(input='"name" "foo"', output=["name", "foo"]),
            C(input='--name=foo', output=["name", "foo"]),
            C(input='--name foo', output=["name", "foo"]),
            C(input="--name 'foo=bar'", output=["name", "foo=bar"])
        ]
        for c in candidates:
            with self.subTest(input=c.input):
                got = list(self._callFUT(c.input))
                self.assertEqual(got, c.output)


if __name__ == "__main__":
    unittest.main()
