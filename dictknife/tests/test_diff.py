import unittest
from collections import namedtuple, OrderedDict


class DiffRowsTests(unittest.TestCase):
    def _callFUT(self, d0, right):
        from dictknife.diff import diff_rows
        return diff_rows(d0, right)

    def test_primitives(self):
        C = namedtuple("C", "left, right, expected, msg")
        # yapf: disable
        candidates = [
            C(msg="str, without diff",
              left={"x": "10"}, right={"x": "10"}, expected=[{"name": "x", "left": "10", "right": "10", "diff": ""}]),
            C(msg="str, with diff",
              left={"x": "10"}, right={"x": "100"}, expected=[{"name": "x", "left": "10", "right": "100", "diff": "  1  0+ 0"}]),
            C(msg="int, without diff",
              left={"x": 10}, right={"x": 10}, expected=[{"name": "x", "left": 10, "right": 10, "diff": 0}]),
            C(msg="int, with diff",
              left={"x": 10}, right={"x": 9}, expected=[{"name": "x", "left": 10, "right": 9, "diff": -1}]),
            C(msg="missing right",
              left={"x": 10}, right={}, expected=[{"name": "x", "left": 10, "right": None, "diff": None}]),
            C(msg="missing left",
              left={}, right={"x": 10}, expected=[{"name": "x", "left": None, "right": 10, "diff": None}]),
            C(msg="nested",
              left={"a": {"b": {"c": "foo"}}}, right={"a": {"b": {"c": "bar"}}}, expected=[{"name": "a/b/c", "left": "foo", "right": "bar", "diff": "- f- o- o+ b+ a+ r"}]),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(msg=c.msg):
                got = self._callFUT(c.left, c.right)
                self.assertListEqual(got, c.expected)



if __name__ == "__main__":
    unittest.main()
