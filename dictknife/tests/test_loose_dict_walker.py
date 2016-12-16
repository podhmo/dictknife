import unittest
from collections import namedtuple


class WalkerTests(unittest.TestCase):
    def _getTargetClass(self):
        from dictknife import LooseDictWalker
        return LooseDictWalker

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_it__on_container(self):
        C = namedtuple("C", "qs, d, expected_path, expected_container")
        candidates = [
            C(qs=[],
              d={"a": {"b": {"c": {"d": 10}}}},
              expected_path=None,
              expected_container=None),
            C(qs=["b", "d"],
              d={"a": {"b": {"c": {"d": 10}}}},
              expected_path=["a", "b", "c", "d"],
              expected_container={"d": 10}),
            C(qs=["b", "c"],
              d={"a": {"b": {"c": {"d": 10}}}},
              expected_path=["a", "b", "c"],
              expected_container={"c": {"d": 10}}),
            C(qs=["x"],
              d={"a": {"b": {"c": {"d": 10}}}},
              expected_path=None,
              expected_container=None)
        ]
        for c in candidates:
            with self.subTest(qs=c.qs, d=c.d):
                called = [False]

                def on_container(path, d):
                    called[0] = True
                    self.assertEqual(path, c.expected_path)
                    self.assertEqual(d, c.expected_container)

                w = self._makeOne(on_container=on_container)
                w.walk(c.qs, c.d)
                self.assertEqual(called[0], c.expected_path is not None)

    def test_it__on_data(self):
        C = namedtuple("C", "qs, d, expected_path, expected_data")
        candidates = [
            C(qs=["a"],
              d={"a": {"b": {"c": {"d": 10}}}},
              expected_path=["a"],
              expected_data={"b": {"c": {"d": 10}}}),
            C(qs=["b", "d"],
              d={"a": {"b": {"c": {"d": 10}}}},
              expected_path=["a", "b", "c", "d"],
              expected_data=10),
            C(qs=["b", "c"],
              d={"a": {"b": {"c": {"d": 10}}}},
              expected_path=["a", "b", "c"],
              expected_data={"d": 10}),
            C(qs=["x"],
              d={"a": {"b": {"c": {"d": 10}}}},
              expected_path=None,
              expected_data=None)
        ]
        for c in candidates:
            with self.subTest(qs=c.qs, d=c.d):
                called = [False]

                def on_data(path, d):
                    called[0] = True
                    self.assertEqual(path, c.expected_path)
                    self.assertEqual(d, c.expected_data)

                w = self._makeOne(on_data=on_data)
                w.walk(c.qs, c.d)
                self.assertEqual(called[0], c.expected_path is not None)

    def test_it_ntimes(self):
        C = namedtuple("C", "qs, d, expected_path, expected_container")
        candidates = [
            C(qs=["a"],
              d={"a": {"b": {"a": {"b": {"a": 10}}}}},
              expected_path=["a"],
              expected_container={"a": {"b": {"a": {"b": {"a": 10}}}}}),
            C(qs=["a", "a"],
              d={"a": {"b": {"a": {"b": {"a": 10}}}}},
              expected_path=["a", "b", "a"],
              expected_container={"a": {"b": {"a": 10}}}),
            C(qs=["a", "a", "a"],
              d={"a": {"b": {"a": {"b": {"a": 10}}}}},
              expected_path=["a", "b", "a", "b", "a"],
              expected_container={"a": 10}),
            C(qs=["a", "a", "a", "a"],
              d={"a": {"b": {"a": {"b": {"a": 10}}}}},
              expected_path=None,
              expected_container=None),
        ]
        for c in candidates:
            with self.subTest(qs=c.qs, d=c.d):
                called = [False]

                def on_container(path, d):
                    called[0] = True
                    self.assertEqual(path, c.expected_path)
                    self.assertEqual(d, c.expected_container)

                w = self._makeOne(on_container=on_container)
                w.walk(c.qs, c.d)
                self.assertEqual(called[0], c.expected_path is not None)

    def test_it_depth(self):
        C = namedtuple("C", "qs, depth, d, expected_path, expected_container")
        candidates = [
            C(qs=["a", "a", "a"], depth=1,
              d={"a": {"b": {"a": {"b": {"a": 10}}}}},
              expected_path=None,
              expected_container=None),
            C(qs=["a", "a", "a"], depth=2,
              d={"a": {"b": {"a": {"b": {"a": 10}}}}},
              expected_path=None,
              expected_container=None),
            C(qs=["a", "a", "a"], depth=3,
              d={"a": {"b": {"a": {"b": {"a": 10}}}}},
              expected_path=["a", "b", "a", "b", "a"],
              expected_container={"a": 10}),
        ]
        for c in candidates:
            with self.subTest(qs=c.qs, d=c.d, depth=c.depth):
                called = [False]

                def on_container(path, d):
                    called[0] = True
                    self.assertEqual(path, c.expected_path)
                    self.assertEqual(d, c.expected_container)

                w = self._makeOne(on_container=on_container)
                w.walk(c.qs, c.d, depth=c.depth)
                self.assertEqual(called[0], c.expected_path is not None)

    def test_chains(self):
        from ..operators import ANY
        s = []

        def first(path, value):
            s.append(value)

            def second(path, value):
                s.append(value)

                def third(path, value):
                    s.append(value)

                self._makeOne(on_container=third).walk([ANY, "b"], value)

            self._makeOne(on_container=second).walk([ANY, "b"], value)

        d = {"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}}
        self._makeOne(on_container=first).walk(["b"], d)

        expected = [
            {'b': {'a': {'b': {'a': {'b': 10}}}}},
            {'b': {'a': {'b': 10}}},
            {'b': 10}
        ]

        self.assertEqual(s, expected)
