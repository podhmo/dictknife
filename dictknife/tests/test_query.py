import unittest
from collections import namedtuple
import itertools
import copy
import os

COLSIZE = int(os.environ.get("COLSIZE") or "60")


class JoinTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.query import join

        return list(join(*args, **kwargs))

    def test_it(self):
        from dictknife import query

        class data:
            x_packages = [
                {"version": "2.7", "downloads": 1000},
                {"version": "3.5", "downloads": 2000},
                {"version": "3.6", "downloads": 3000},
                {"version": "3.7", "downloads": 3000},
            ]
            y_packages = [
                {"version": "3.5", "downloads": 2000},
                {"version": "3.6", "downloads": 2000},
                {"version": "3.7", "downloads": 2000},
                {"version": "3.8", "downloads": 500},
            ]

        class copied:
            x_packages = copy.deepcopy(data.x_packages)
            y_packages = copy.deepcopy(data.y_packages)

        C = namedtuple("C", "msg, args, kwargs, want")
        cases = [
            C(
                msg="inner join",
                args=["x_packages", "y_packages"],
                kwargs={"on": "version"},
                want=[
                    (
                        {"version": "3.5", "downloads": 2000},
                        {"version": "3.5", "downloads": 2000},
                    ),
                    (
                        {"version": "3.6", "downloads": 3000},
                        {"version": "3.6", "downloads": 2000},
                    ),
                    (
                        {"version": "3.7", "downloads": 3000},
                        {"version": "3.7", "downloads": 2000},
                    ),
                ],
            ),
            C(
                msg="left outer join",
                args=["x_packages", "y_packages"],
                kwargs={"on": "version", "how": query.how_left_outer_join},
                want=[
                    ({"version": "2.7", "downloads": 1000}, None),
                    (
                        {"version": "3.5", "downloads": 2000},
                        {"version": "3.5", "downloads": 2000},
                    ),
                    (
                        {"version": "3.6", "downloads": 3000},
                        {"version": "3.6", "downloads": 2000},
                    ),
                    (
                        {"version": "3.7", "downloads": 3000},
                        {"version": "3.7", "downloads": 2000},
                    ),
                ],
            ),
            C(
                msg="right outer join",
                args=["x_packages", "y_packages"],
                kwargs={"on": "version", "how": query.how_right_outer_join},
                want=[
                    (
                        {"version": "3.5", "downloads": 2000},
                        {"version": "3.5", "downloads": 2000},
                    ),
                    (
                        {"version": "3.6", "downloads": 3000},
                        {"version": "3.6", "downloads": 2000},
                    ),
                    (
                        {"version": "3.7", "downloads": 3000},
                        {"version": "3.7", "downloads": 2000},
                    ),
                    (None, {"version": "3.8", "downloads": 500}),
                ],
            ),
            C(
                msg="full outer join",
                args=["x_packages", "y_packages"],
                kwargs={"on": "version", "how": query.how_full_outer_join},
                want=[
                    ({"version": "2.7", "downloads": 1000}, None),
                    (
                        {"version": "3.5", "downloads": 2000},
                        {"version": "3.5", "downloads": 2000},
                    ),
                    (
                        {"version": "3.6", "downloads": 3000},
                        {"version": "3.6", "downloads": 2000},
                    ),
                    (
                        {"version": "3.7", "downloads": 3000},
                        {"version": "3.7", "downloads": 2000},
                    ),
                    (None, {"version": "3.8", "downloads": 500}),
                ],
            ),
        ]
        for c in cases:
            with self.subTest(msg=c.msg, args=c.args, kwargs=c.kwargs):
                args = [getattr(data, name) for name in c.args]
                got = self._callFUT(*args, **c.kwargs)
                self.assertTrue(
                    got == c.want, msg=_DifferenceReportText(got=got, want=c.want)
                )
                self.assertEqual(got, c.want)
                self.assertTrue(data.x_packages == copied.x_packages, "not modified")
                self.assertTrue(data.y_packages == copied.y_packages, "not modified")


class _DifferenceReportText:
    def __init__(self, *, got, want):
        self.got = got
        self.want = want

    def __str__(self):
        import json

        fmt = "{left:%d}\t{right:%d}" % (COLSIZE, COLSIZE)
        r = [
            "",
            fmt.format(left="want", right="got"),
            "----------------------------------------------------------------------",
        ]
        for lhs, rhs in itertools.zip_longest(self.want, self.got):
            r.append(
                fmt.format(
                    left=json.dumps(lhs, sort_keys=True),
                    right=json.dumps(rhs, sort_keys=True),
                )
            )
        return "\n".join(r)


if __name__ == "__main__":
    unittest.main()
