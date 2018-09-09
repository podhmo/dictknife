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
        from dictknife.mkdict import _AccessorSupportList as Accessor
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
            # array
            C(tokens=["xs/", "a", "xs/", "b", "xs/", "c"],
              expected={"xs": ["a", "b", "c"]}),
            C(tokens=["xs//name", "a", "xs//name", "b", "xs//name", "c"],
              expected={"xs": [{"name": "a"}, {"name": "b"}, {"name": "c"}]}),
            C(tokens=["xs//name", "a", "xs/-1/age", 20, "xs//name", "b", "xs/-1/age", 10],
              expected={"xs": [{"name": "a", "age": 20}, {"name": "b", "age": 10}]}),
            C(tokens=["xs//name", "a", "xs/0/age", 20, "xs//name", "b", "xs/1/age", 10],
              expected={"xs": [{"name": "a", "age": 20}, {"name": "b", "age": 10}]}),
            C(tokens=["xs/0/name", "a", "xs/0/age", 20, "xs/1/name", "b", "xs/1/age", 10],
              expected={"xs": [{"name": "a", "age": 20}, {"name": "b", "age": 10}]}),
            C(tokens=["xs//name", "a", "xs//age", 20, "xs//name", "b", "xs//age", 10],
              expected={"xs": [{"name": "a"}, {"age": 20}, {"name": "b"}, {"age": 10}]}),
            C(tokens=["xs//name", "a", "xs/-1/age", 20, "xs/-1/name", "b", "xs/-1/age", 10],
              expected={"xs": [{"name": "b", "age": 10}]}),
            C(tokens=[
                "@xs/", "a", "@xs/", "b", "@xs/", "c",
                "ys", "&xs",
                "zs/0", "&xs/0", "zs/1", "&xs/-1"],
              expected={"ys": ["a", "b", "c"], "zs": ["a", "c"]}),
            C(tokens=[
                "@xs/0/name", "a", "@xs/0/age", 20, "@xs/1/name", "b", "@xs/1/age", 10,
                "names/", "&xs/0/name", "names/", "&xs/1/name"],
              expected={"names": ["a", "b"]}),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(tokens=c.tokens):
                got = self._callFUT(c.tokens)
                self.assertEqual(_to_dict(got), c.expected)


def _to_dict(d):
    if isinstance(d, (list, tuple)):
        return [_to_dict(x) for x in d]
    elif hasattr(d, "keys"):
        return {k: _to_dict(v) for k, v in d.items()}
    else:
        return d


if __name__ == "__main__":
    unittest.main()
