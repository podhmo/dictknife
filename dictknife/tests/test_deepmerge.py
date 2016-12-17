import unittest


class TestDeepMerge(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife import deepmerge
        return deepmerge(*args, **kwargs)

    def test_it(self):
        d0 = {
            "a": {
                "x": 1
            },
            "b": {
                "y": 10
            },
        }
        d1 = {
            "a": {
                "x": 1
            },
            "b": {
                "z": 10
            },
            "c": 100
        }
        actual = self._callFUT(d0, d1)
        expected = {
            "a": {
                "x": 1
            },
            "b": {
                "y": 10,
                "z": 10
            },
            "c": 100
        }
        self.assertEqual(actual, expected)
        self.assertNotEqual(actual, d0, msg="not modified!!")
