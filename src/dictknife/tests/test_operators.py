import unittest
from collections import namedtuple


class OperatorsTests(unittest.TestCase):
    def _callFUT(self, op, value):
        from dictknife.operators import apply

        return apply(op, value)

    def test_it(self) -> None:
        C = namedtuple("C", "value, expected")

        candidates = [
            C(value="x", expected=False),
            C(value="xx", expected=True),
            C(value="xxx", expected=False),
        ]

        op = "xx"
        for c in candidates:
            with self.subTest(op=op, value=c.value):
                actual = self._callFUT(op, c.value)
                self.assertEqual(actual, c.expected)

    def test_and(self) -> None:
        from ..operators import And

        C = namedtuple("C", "value, expected")

        candidates = [
            C(value="x", expected=False),
            C(value="xx", expected=False),
            C(value="xxx", expected=False),
        ]

        op = And(["x", "xx", "xxx"])
        for c in candidates:
            with self.subTest(op=op, value=c.value):
                actual = self._callFUT(op, c.value)
                self.assertEqual(actual, c.expected)

    def test_or(self) -> None:
        from ..operators import Or

        C = namedtuple("C", "value, expected")

        candidates = [
            C(value="x", expected=True),
            C(value="xx", expected=True),
            C(value="xxx", expected=True),
        ]

        op = Or(["x", "xx", "xxx"])
        for c in candidates:
            with self.subTest(op=op, value=c.value):
                actual = self._callFUT(op, c.value)
                self.assertEqual(actual, c.expected)

    def test_and2(self) -> None:
        from ..operators import And, Not

        C = namedtuple("C", "value, expected")

        candidates = [
            C(value="x", expected=False),
            C(value="xx", expected=True),
            C(value="xxx", expected=False),
        ]

        op = And([Not("x"), "xx", Not("xxx")])
        for c in candidates:
            with self.subTest(op=op, value=c.value):
                actual = self._callFUT(op, c.value)
                self.assertEqual(actual, c.expected)
