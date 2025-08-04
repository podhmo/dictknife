import unittest
from collections import OrderedDict, namedtuple


class WrapTests(unittest.TestCase):
    def _callFUT(self, x):
        from dictknife.sort import _wrap
        return _wrap(x)

    def test_it(self):
        C = namedtuple("C", "input, expected")
        # yapf: disable
        candidates = [
            C(input=[1, 2, 10], expected=[1, 2, 10]),
            C(input=[1, 2, "10"], expected=["10", 1, 2]),
            C(input=["1", "2", "10"], expected=["1", "10", "2"]),
            C(input=["2", 1, None], expected=["2", 1, None]),
            C(input=[1, [1]], expected=[1, [1]]),
            C(input=[1, [1], ["1"]], expected=[["1"], 1, [1]]),
            C(input=[1, [1], [[4, 2, 3], [1, 2, 3]], ["1"]], expected=[["1"], 1, [1], [[1, 2, 3], [2, 3, 4, ]]]),
            C(input=[1, [], {}], expected=[1, {}, []]),
            C(input=[1, [1], ["1"], "1", {"name": "foo"}, {"age": 10}], expected=["1", {"name": "foo"}, ["1"], 1, {"age": 10}, [1]]),
            C(
                input=[{"name": "x"}, {}, {"name": "x", "age": 20}, {"name": "x", "age": 10}, {"name": "x", "age": None}],
                expected=[{"name": "x"}, {"name": "x", "age": 10}, {"name": "x", "age": 20}, {"name": "x", "age": None}, {}],
            )
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(msg=str(c.input)):
                ws = [self._callFUT(x) for x in c.input]
                got = [x.unwrap() for x in sorted(ws, key=lambda x: x.uid)]
                self.assertEqual(got, c.expected)


class Tests(unittest.TestCase):
    maxDiff = None

    def _callFUT(self, x):
        from dictknife.sort import sort_flexibly
        return sort_flexibly(x)

    def test_it(self):
        C = namedtuple("C", "msg, input, expected")
        # yapf: disable
        candidates = [
            C(msg="int", input=1, expected=1),
            C(msg="str", input="foo", expected="foo"),
            C(msg="list, primitive", input=[1, 3, 2], expected=[1, 2, 3]),
            C(msg="dict, primitive",
              input=OrderedDict([("name", "foo"), ("age", 20)]),
              expected=OrderedDict([("age", 20), ("name", "foo")])),
            C(msg="list, dict",
              input=[
                  {"name": "foo", "age": 10},
                  {"name": "bar", "age": 9},
                  {"name": "z", "age": 1},
              ], expected=[
                  {"name": "bar", "age": 9},
                  {"name": "foo", "age": 10},
                  {"name": "z", "age": 1},
              ]),
            C(msg="list, dict, missing",
              input=[
                  {"name": "x"},
                  {"name": "y", "age": 1},
                  {"name": "y", "age": None},
                  {"name": "y"},
              ], expected=[
                  {"name": "x"},
                  {"name": "y", "age": 1},
                  {"name": "y", "age": None},
                  {"name": "y"},
              ]),
            C(msg="list, dict, nested",
              input=[
                  {
                      "dimensions": [{"name": "x"}, {"name": "y"}, {"name": "z"}],
                      "value": 0,
                  },
                  {
                      "dimensions": [{"name": "a"}, {"name": "y"}, {"name": "z"}],
                      "value": 1000,
                  },
                  {
                      "dimensions": [{"name": "x"}, {"name": "a"}, {"name": "z"}],
                      "value": 2000,
                  },
                  {
                      "dimensions": [{"name": "x"}, {"name": "y"}, {"name": "a"}],
                      "value": 3000,
                  },
              ], expected=[
                  {
                      "dimensions": [{"name": "a"}, {"name": "x"}, {"name": "y"}],
                      "value": 3000,
                  },
                  {
                      "dimensions": [{"name": "a"}, {"name": "x"}, {"name": "z"}],
                      "value": 2000,
                  },
                  {
                      "dimensions": [{"name": "a"}, {"name": "y"}, {"name": "z"}],
                      "value": 1000,
                  },
                  {
                      "dimensions": [{"name": "x"}, {"name": "y"}, {"name": "z"}],
                      "value": 0,
                  },
              ]),
            # nested
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(msg=c.msg):
                got = self._callFUT(c.input)
                self.assertEqual(got, c.expected)


if __name__ == "__main__":
    unittest.main()
