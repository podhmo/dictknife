import unittest
from collections import namedtuple, OrderedDict


class DiffRowsTests(unittest.TestCase):
    maxDiff = None

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
            C(msg="list, primitive",
              left=[1, 2, 3], right=[2, 2, 2], expected=[
                  {"name": "0", "left": 1, "right": 2, "diff": 1},
                  {"name": "1", "left": 2, "right": 2, "diff": 0},
                  {"name": "2", "left": 3, "right": 2, "diff": -1},
              ]),
            C(msg="list, mismatched",
              left=[1, 2], right=[2], expected=[
                  {"name": "0", "left": 1, "right": 2, "diff": 1},
                  {"name": "1", "left": 2, "right": 0, "diff": -2},
              ]),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(msg=c.msg):
                got = self._callFUT(c.left, c.right)
                self.assertListEqual(got, c.expected)

    def test_it(self):
        left = OrderedDict(
            [
                ("x", 10),
                ("y", 100),
                (
                    "nested",
                    OrderedDict(
                        [
                            ("v1", 0),
                            ("v2", 1),
                            ("vs", [0, 1, 2, 3]),
                            ("vs2", [{
                                "z": "foo"
                            }]),
                        ]
                    )
                ),
            ]
        )
        right = OrderedDict(
            [
                ("x", 10),
                ("y", 110),
                (
                    "nested",
                    OrderedDict(
                        [
                            ("v1", 10),
                            ("v2", -1),
                            ("vs", [0, 2, 2, 2]),
                            ("vs2", [{
                                "z": "bar"
                            }]),
                        ]
                    )
                ),
            ]
        )
        got = self._callFUT(left, right)
        # yapf: disable
        expected = [
            {'name': 'x', 'left': 10, 'right': 10, 'diff': 0},
            {'name': 'y', 'left': 100, 'right': 110, 'diff': 10},
            {'name': 'nested/v1', 'left': 0, 'right': 10, 'diff': 10},
            {'name': 'nested/v2', 'left': 1, 'right': -1, 'diff': -2},
            {'name': 'nested/vs/0', 'left': 0, 'right': 0, 'diff': 0},
            {'name': 'nested/vs/1', 'left': 1, 'right': 2, 'diff': 1},
            {'name': 'nested/vs/2', 'left': 2, 'right': 2, 'diff': 0},
            {'name': 'nested/vs/3', 'left': 3, 'right': 2, 'diff': -1},
            {'name': 'nested/vs2/0/z', 'left': "foo", 'right': "bar", 'diff': '- f- o- o+ b+ a+ r'},
        ]
        # yapf: enable
        self.assertListEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
