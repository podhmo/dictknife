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

    def test_rec(self):
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
        self._makeOne(on_container=first).walk([ANY, "b"], d)

        expected = [
            {'b': {'a': {'b': {'a': {'b': 10}}}}},
            {'b': {'a': {'b': 10}}},
            {'b': 10}
        ]

        self.assertEqual(s, expected)

    def test_rec2(self):
        from ..contexts import SimpleContext
        from ..operators import ANY

        class RecContext(SimpleContext):
            def __init__(self, qs):
                self.qs = qs[:]

            def __call__(self, walker, fn, value):
                return fn(walker, self, value)

        s = []

        def matched(walker, ctx, value):
            s.append(value)
            walker.walk(ctx.qs[:], value, ctx=ctx)

        d = {"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}}
        qs = [ANY, "b"]
        self._makeOne(on_container=matched).walk(qs, d, ctx=RecContext(qs))

        expected = [
            {'b': {'a': {'b': {'a': {'b': 10}}}}},
            {'b': {'a': {'b': 10}}},
            {'b': 10}
        ]

        self.assertEqual(s, expected)


class ChainTests(unittest.TestCase):
    def _getTargetClass(self):
        from dictknife import ChainSource
        return ChainSource

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_value(self):
        C = namedtuple("C", "d, method, expected")
        candidates = [
            C(method="on_container",
              d={"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}},
              expected=[
                  {'b': {'a': {'b': {'a': {'b': 10}}}}},
                  {'b': {'a': {'b': 10}}},
                  {'b': 10}
              ]),
            C(method="on_data",
              d={"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}},
              expected=[
                  {'a': {'b': {'a': {'b': 10}}}},
                  {'a': {'b': 10}},
                  10,
              ]),
        ]
        for c in candidates:
            with self.subTest(d=c.d, method=c.method):
                s = []

                def on_match(ctx, walker, value):
                    s.append(value)

                chain = self._makeOne().chain(["b"]).chain(["b"]).chain(["b"])
                chain.walk(c.d, **{c.method: on_match})
                self.assertEqual(s, c.expected)

    def test_path(self):
        C = namedtuple("C", "d, method, expected")
        candidates = [
            C(method="on_container",
              d={"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}},
              expected=[
                  ["a", "b"],
                  ["a", "b", "a", "b"],
                  ["a", "b", "a", "b", "a", "b"],
              ]),
            C(method="on_data",
              d={"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}},
              expected=[
                  ["a", "b"],
                  ["a", "b", "a", "b"],
                  ["a", "b", "a", "b", "a", "b"],
              ]),
        ]
        for c in candidates:
            with self.subTest(d=c.d, method=c.method):
                s = []

                def on_match(ctx, walker, value):
                    s.append(ctx.path[:])

                chain = self._makeOne().chain(["b"]).chain(["b"]).chain(["b"])
                chain.walk(c.d, **{c.method: on_match})
                self.assertEqual(s, c.expected)

    def test_other_methods(self):
        d = {"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}}
        s = []

        def on_match0(ctx, walker, value):
            s.append(("0", ctx.path[:]))

        def on_match1(ctx, walker, value):
            s.append(("1", ctx.path[:]))

        def on_match2(ctx, walker, value):
            s.append(("2", ctx.path[:]))

        def on_match(ctx, walker, value):
            s.append(("default", ctx.path[:]))

        chain = (self._makeOne()
                 .chain(["b"], on_container=on_match0)
                 .chain(["b"], on_container=on_match1)
                 .chain(["b"], on_container=on_match2))
        chain.walk(d, on_container=on_match)
        expected = [
            ("0", ["a", "b"]),
            ("1", ["a", "b", "a", "b"]),
            ("2", ["a", "b", "a", "b", "a", "b"]),
        ]
        self.assertEqual(s, expected)

    def test_other_methods__break(self):
        d = {"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}}
        s = []

        def on_match0(ctx, walker, value):
            s.append(("0", ctx.path[:]))

        def on_match1(ctx, walker, value):
            s.append(("1", ctx.path[:]))
            return False

        def on_match2(ctx, walker, value):
            s.append(("2", ctx.path[:]))

        def on_match(ctx, walker, value):
            s.append(("default", ctx.path[:]))

        chain = (self._makeOne()
                 .chain(["b"], on_container=on_match0)
                 .chain(["b"], on_container=on_match1)
                 .chain(["b"], on_container=on_match2))
        chain.walk(d, on_container=on_match)
        expected = [
            ("0", ["a", "b"]),
            ("1", ["a", "b", "a", "b"]),
        ]
        self.assertEqual(s, expected)

    def test_other_methods__callable_qs(self):
        from ..operators import ANY

        d = {"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}}
        s = []

        def on_match0(ctx, walker, value):
            s.append(("0", ctx.path[:]))

        def step1(new_ctx, walker, value):
            s.append("hai")
            walker.walk([ANY, "b"], value, ctx=new_ctx)

        def on_match1(ctx, walker, value):
            s.append(("1", ctx.path[:]))

        def step2(new_ctx, walker, value):
            s.append("hoi")
            walker.walk([ANY, "b"], value, ctx=new_ctx)

        def on_match2(ctx, walker, value):
            s.append(("2", ctx.path[:]))

        def on_match(ctx, walker, value):
            s.append(("default", ctx.path[:]))

        chain = (self._makeOne()
                 .chain(["b"], on_container=on_match0)
                 .chain(step1, on_container=on_match1)
                 .chain(step2, on_container=on_match2))
        chain.walk(d, on_container=on_match)
        expected = [
            ("0", ["a", "b"]),
            "hai",
            ("1", ["a", "b", "a", "b"]),
            "hoi",
            ("2", ["a", "b", "a", "b", "a", "b"]),
            "hoi",
        ]
        self.assertEqual(s, expected)
