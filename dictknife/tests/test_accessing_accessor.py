import unittest


class AssignTests(unittest.TestCase):
    def _callFUT(self, d, k, v):
        from dictknife import Accessor

        a = Accessor(make_dict=dict)
        return a.assign(d, k, v)

    def test_assign_dict(self) -> None:
        d: dict[str, object] = {}
        self._callFUT(d, ["x"], 1)
        expected = {"x": 1}
        self.assertDictEqual(d, expected)

    def test_assign_deeply(self) -> None:
        d: dict[int, object] = {}
        self._callFUT(d, [1, 2, 3, 4, 5, 6, 7, 8, 9], "foo")
        expected = {1: {2: {3: {4: {5: {6: {7: {8: {9: "foo"}}}}}}}}}
        self.assertDictEqual(d, expected)

    def test_assign_list(self) -> None:
        from collections import namedtuple

        C = namedtuple("C", "d, path, v, expected")
        cases = [
            C(d={"x": []}, path=["x", 0], v=1, expected={"x": [1]}),
            C(d={"x": []}, path=["x", 1], v=1, expected={"x": [None, 1]}),
            C(d={"x": [1, 2, 3]}, path=["x", 1], v=10, expected={"x": [1, 10, 3]}),
            C(
                d={"x": [1, 2, 3]},
                path=["x", 5],
                v=10,
                expected={"x": [1, 2, 3, None, None, 10]},
            ),
            C(
                d={"x": [1, 2]},
                path=["x", 1, "a"],
                v=10,
                expected={"x": [1, {"a": 10}]},
            ),
            C(
                d={"x": [1]},
                path=["x", 2, "a"],
                v=10,
                expected={"x": [1, {}, {"a": 10}]},
            ),
        ]
        for c in cases:
            with self.subTest(d=c.d, path=c.path, v=c.v):
                self._callFUT(c.d, c.path, c.v)
                self.assertDictEqual(c.d, c.expected)

    def test_assign_list2(self) -> None:
        d = {"x": [1]}
        self._callFUT(d, ["x", 2], 3)
        self._callFUT(d, ["x", 1, "a"], 10)
        expected = {"x": [1, {"a": 10}, 3]}
        self.assertDictEqual(d, expected)

    def test_assign_list_nested(self) -> None:
        from collections import namedtuple

        C = namedtuple("C", "d, path, v, expected")
        cases = [
            C(
                d={"x": []},
                path=["x", 0, "name"],
                v="foo",
                expected={"x": [{"name": "foo"}]},
            ),
            C(
                d={"x": []},
                path=["x", 1, "name"],
                v="foo",
                expected={"x": [{}, {"name": "foo"}]},
            ),
            C(
                d={"x": [{"name": "foo"}, {"name": "bar"}]},
                path=["x", 3, "name"],
                v="boo",
                expected={"x": [{"name": "foo"}, {"name": "bar"}, {}, {"name": "boo"}]},
            ),
        ]
        for c in cases:
            with self.subTest(d=c.d, path=c.path, v=c.v):
                self._callFUT(c.d, c.path, c.v)
                self.assertDictEqual(c.d, c.expected)

    def test_assign_list_nested2(self) -> None:
        d = {"x": [{"name": "foo"}]}
        self._callFUT(d, ["x", 3, "name"], "boo")
        self._callFUT(d, ["x", 1, "name"], "bar")
        expected = {"x": [{"name": "foo"}, {"name": "bar"}, {}, {"name": "boo"}]}
        self.assertDictEqual(d, expected)


class MaybeAccessTests(unittest.TestCase):
    def _callFUT(self, d, path):
        from dictknife import Accessor

        a = Accessor(make_dict=dict)
        return a.maybe_access(d, path)

    def test_maybe_access(self) -> None:
        from collections import namedtuple

        C = namedtuple("C", "d, path, expected")

        cases = [
            C(d=None, path=["k"], expected=None),
            C(d={"k": "v"}, path=["k"], expected="v"),
            C(d={"k": "v"}, path=["z"], expected=None),
            C(d=[], path=["k"], expected=None),
            C(d=[1], path=[0], expected=1),
            C(d=[1], path=[1], expected=None),
            C(d=[{"k": "v"}], path=[0, "k"], expected="v"),
            C(d=[{"k": "v"}], path=[0, "z"], expected=None),
        ]
        for c in cases:
            with self.subTest(d=c.d, path=c.path):
                got = self._callFUT(c.d, c.path)
                self.assertEqual(got, c.expected)


if __name__ == "__main__":
    unittest.main()
