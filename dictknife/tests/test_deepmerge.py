import unittest


class TestDeepMerge(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife import deepmerge

        return deepmerge(*args, **kwargs)

    def test_it(self):
        d0 = {
            "a": {"x": 1},
            "b": {"y": 10},
        }
        d1 = {"a": {"x": 1}, "b": {"z": 10}, "c": 100}
        actual = self._callFUT(d0, d1)
        expected = {"a": {"x": 1}, "b": {"y": 10, "z": 10}, "c": 100}
        self.assertEqual(actual, expected)
        self.assertNotEqual(actual, d0, msg="not modified!!")

    def test_it__override(self):
        d0 = {
            "name": "foo",
            "object": {"x": 1, "z": 1},
            "children": [1],
        }
        d1 = {
            "name": "bar",
            "object": {"y": 2, "z": 3},
            "children": [1, 2, 3],
            "a": {"b": {"c": "d"}},
        }
        actual = self._callFUT(d0, d1, override=True)
        expected = {
            "name": "bar",
            "object": {"x": 1, "y": 2, "z": 3},
            "children": [1, 2, 3],
            "a": {"b": {"c": "d"}},
        }
        self.assertEqual(actual, expected)
        self.assertNotEqual(actual, d0, msg="not modified!!")

    def test_with_empty(self):
        from collections import namedtuple

        C = namedtuple("C", "d0 d1 override expected")

        candidates = [
            C(d0={1: 10}, d1=None, override=False, expected={1: 10}),
            C(d0={1: 10}, d1={}, override=False, expected={1: 10}),
            C(d0={1: 10}, d1=None, override=True, expected={1: 10}),
            C(d0={1: 10}, d1={}, override=True, expected={1: 10}),
        ]
        for c in candidates:
            with self.subTest(d0=c.d0, d1=c.d1):
                actual = self._callFUT(c.d0, c.d1, override=c.override)
                self.assertEqual(actual, c.expected)
