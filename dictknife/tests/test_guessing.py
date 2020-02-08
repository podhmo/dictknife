import unittest


class Tests(unittest.TestCase):
    def _callFUT(self, v, *args, **kwargs):
        from dictknife.guessing import guess

        return guess(v, *args, **kwargs)

    def test_nan(self):
        import math

        v = {"nan": "nan"}
        got = self._callFUT(v)
        self.assertTrue(math.isnan(got["nan"]))

    def test_it(self):
        v = [
            {
                "ints": [{"zero": "0", "nums": ["10", "-2000"]}],
                "floatnums": [
                    {"full": "0.1", "mini": ".1", "epsilon": "5.551115123125783e-17"}
                ],
                "infs": ["inf", "-inf"],
            }
        ]
        got = self._callFUT(v)
        expected = [
            {
                "floatnums": [
                    {"full": 0.1, "mini": 0.1, "epsilon": 5.551115123125783e-17}
                ],
                "ints": [{"nums": [10, -2000], "zero": 0}],
                "infs": [float("inf"), float("-inf")],
            }
        ]

        self.assertEqual(got, expected)

    def test_mutable(self):
        v = [{"1": 2}]
        got = self._callFUT(v, mutable=True)
        self.assertEqual(id(got), id(v), msg="list")
        self.assertEqual(id(got[0]), id(v[0]), msg="dict")
        self.assertEqual(id(got[0]["1"]), id(v[0]["1"]), msg="item")

    def test_immutable(self):
        v = [{"1": 2}]
        got = self._callFUT(v, mutable=False)
        self.assertNotEqual(id(got), id(v), msg="list")
        self.assertNotEqual(id(got[0]), id(v[0]), msg="dict")
        # self.assertEqual(id(got[0]["1"]), id(v[0]["1"]), msg="item")
