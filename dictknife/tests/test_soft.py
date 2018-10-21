import unittest


class Tests(unittest.TestCase):
    def _callFUT(self, x):
        from dictknife.sort import sort_flexibly
        return sort_flexibly(x)

    def test_it(self):
        from collections import namedtuple
        C = namedtuple("C", "msg, input, expected")
        candidates = [
            C(msg="int", input=1, expected=1),
            C(msg="str", input="foo", expected="foo"),
        ]
        for c in candidates:
            with self.subTest(msg=c.msg):
                got = self._callFUT(c.input)
                self.assertEqual(got, c.expected)


if __name__ == "__main__":
    unittest.main()
