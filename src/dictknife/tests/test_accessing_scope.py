import unittest


class Tests(unittest.TestCase):
    def _makeOne(self, init):
        from dictknife.accessing import Scope

        return Scope(init)

    def test_access(self) -> None:
        s = self._makeOne({"x": 10})
        self.assertEqual(s[["x"]], 10)

    def test_key_error(self) -> None:
        s = self._makeOne({})
        with self.assertRaises(KeyError):
            s[["x"]]

    def test_access_nested(self) -> None:
        s = self._makeOne({"x": {"y": 10}})
        self.assertEqual(s[["x", "y"]], 10)

    def test_access_stacked(self) -> None:
        s = self._makeOne({"x": 10})
        s.push({"x": 100})
        self.assertEqual(s[["x"]], 100)

    def test_access_stacked_nested(self) -> None:
        s = self._makeOne({"x": {"y": 10}})
        s.push({"x": {"y": 100}})
        self.assertEqual(s[["x", "y"]], 100)

    def test_access_stacked_nested__but_not_wrapped(self) -> None:
        s = self._makeOne({"x": {"y": 10}})
        s.push({"x": {"z": 100}})
        self.assertEqual(s[["x", "y"]], 10)

    def test_access_with_scope(self) -> None:
        s = self._makeOne({"x": {"y": 10}})
        with s.scope({"x": {"y": 100}}):
            self.assertEqual(s[["x", "y"]], 100)
        self.assertEqual(s[["x", "y"]], 10)
