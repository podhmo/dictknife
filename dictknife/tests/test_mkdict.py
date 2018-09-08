import unittest


class TokenizeTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.mkdict import tokenize
        return tokenize(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple
        C = namedtuple("C", "input, output")
        candidates = [
            C(input='name foo', output=["name", "foo"]),
            C(input='"name" "foo"', output=["name", "foo"]),
            C(input='--name=foo', output=["name", "foo"]),
            C(input='--name foo', output=["name", "foo"]),
            C(input="--name 'foo=bar'", output=["name", "foo=bar"]),
            C(input='name foo; name bar', output=["name", "foo", ";", "name", "bar"]),
        ]
        for c in candidates:
            with self.subTest(input=c.input):
                got = self._callFUT(c.input)
                self.assertEqual(list(got), c.output)


class MkDictTests(unittest.TestCase):
    def _getTarget(self):
        from dictknife.mkdict import _mkdict
        return _mkdict

    def _callFUT(self, tokens):
        from dictknife.accessing import Accessor
        from dictknife.guessing import guess
        return self._getTarget()(
            iter(tokens), delimiter=";", separator="/", accessor=Accessor(), guess=guess
        )

    def test_it(self):
        from collections import namedtuple
        C = namedtuple("C", "tokens, expected")
        # yapf: disable
        candidates = [
            C(tokens=["name", "foo"],
              expected={"name": "foo"}),
            C(tokens=["name", "foo", "age", "20"],
              expected={"name": "foo", "age": 20}),
            C(tokens=["name", "foo", "age", 20],
              expected={"name": "foo", "age": 20}),
            C(tokens=["name", "foo", "age", 20, "parent/name", "bar"],
              expected={"name": "foo", "age": 20, "parent": {"name": "bar"}}),
            C(tokens=["name", "foo", "age", 20, "parent/name", "bar", "parent/name", "*overwrite*"],
              expected={"name": "foo", "age": 20, "parent": {"name": "*overwrite*"}}),
            C(tokens=["name", "foo", ";", "name", "bar"],
              expected=[{"name": "foo"}, {"name": "bar"}]),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(tokens=c.tokens):
                got = self._callFUT(c.tokens)
                self.assertEqual(got, c.expected)


if __name__ == "__main__":
    unittest.main()
