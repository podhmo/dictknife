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
            C(
                input='"@x" val use "&x" dont-ref "&&x" "@@dont-assign" "v"',
                output=["@x", "val", "use", "&x", "dont-ref", "&&x", "@@dont-assign", "v"]
            ),
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
            C(tokens=[
                "@ob/name", "foo", "@ob/age", 40,
                "name", "bar", "age", 20, "parent", "&ob", ";",
                "name", "boo", "age", 18, "parent", "&ob"
            ],
              expected=[
                  {"name": "bar", "age": 20, "parent": {"name": "foo", "age": 40}},
                  {"name": "boo", "age": 18, "parent": {"name": "foo", "age": 40}},
              ]),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(tokens=c.tokens):
                got = self._callFUT(c.tokens)
                # self.assertEqual(_to_dict(got), c.expected)
                print(got)


def _to_dict(d):
    if isinstance(d, (list, tuple)):
        return [_to_dict(x) for x in d]
    elif hasattr(d, "keys"):
        return {k: _to_dict(v) for k, v in d.items()}
    else:
        return d


if __name__ == "__main__":
    unittest.main()
