import unittest


class IteratorTests(unittest.TestCase):
    def _getTargetClass(self):
        from dictknife import DictWalker

        return DictWalker

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_rec(self):
        from ..operators import ANY

        s = []

        d = {"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}}
        iterator = self._makeOne([ANY, "b"])
        for path, value in iterator.iterate(d):
            s.append(value)
            for path, value in iterator.iterate(value):
                s.append(value)
                for path, value in iterator.iterate(value):
                    s.append(value)

        expected = [
            {"b": {"a": {"b": {"a": {"b": 10}}}}},
            {"b": {"a": {"b": 10}}},
            {"b": 10},
        ]

        self.assertEqual(s, expected)
