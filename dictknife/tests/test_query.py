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

    def test_multi_keys(self):
        class data:
            classes = [
                {"id": 1, "year": "1", "name": "A"},
                {"id": 2, "year": "1", "name": "B"},
                {"id": 3, "year": "1", "name": "C"},
                {"id": 4, "year": "2", "name": "A"},
                {"id": 5, "year": "2", "name": "B"},
            ]
            students = [
                {"id": 1, "year": "1", "class": "A", "cid": 1, "name": "foo"},
                {"id": 2, "year": "1", "class": "A", "cid": 1, "name": "bar"},
                {"id": 3, "year": "1", "class": "B", "cid": 2, "name": "boo"},
                {"id": 4, "year": "1", "class": "C", "cid": 3, "name": "yoo"},
            ]

        class copied:
            classes = copy.deepcopy(data.classes)
            students = copy.deepcopy(data.students)

        C = namedtuple("C", "msg, args, kwargs, want")
        cases = [
            C(
                msg="inner join",
                args=[data.classes, data.students],
                kwargs={"left_on": "id", "right_on": "cid"},
                want=[
                    (
                        {"id": 1, "year": "1", "name": "A"},
                        {"id": 1, "year": "1", "class": "A", "cid": 1, "name": "foo"},
                    ),
                    (
                        {"id": 1, "year": "1", "name": "A"},
                        {"id": 2, "year": "1", "class": "A", "cid": 1, "name": "bar"},
                    ),
                    (
                        {"id": 2, "year": "1", "name": "B"},
                        {"id": 3, "year": "1", "class": "B", "cid": 2, "name": "boo"},
                    ),
                    (
                        {"id": 3, "year": "1", "name": "C"},
                        {"id": 4, "year": "1", "class": "C", "cid": 3, "name": "yoo"},
                    ),
                ],
            ),
            C(
                msg="inner join with multi keys",
                args=[data.classes, data.students],
                kwargs={"left_on": ("year", "name"), "right_on": ("year", "class")},
                want=[
                    (
                        {"id": 1, "year": "1", "name": "A"},
                        {"id": 1, "year": "1", "class": "A", "cid": 1, "name": "foo"},
                    ),
                    (
                        {"id": 1, "year": "1", "name": "A"},
                        {"id": 2, "year": "1", "class": "A", "cid": 1, "name": "bar"},
                    ),
                    (
                        {"id": 2, "year": "1", "name": "B"},
                        {"id": 3, "year": "1", "class": "B", "cid": 2, "name": "boo"},
                    ),
                    (
                        {"id": 3, "year": "1", "name": "C"},
                        {"id": 4, "year": "1", "class": "C", "cid": 3, "name": "yoo"},
                    ),
                ],
            ),
            C(
                msg="inner join with multi keys2",
                args=[data.students, data.classes],
                kwargs={"left_on": ("year", "class"), "right_on": ("year", "name")},
                want=[
                    (
                        {"id": 1, "year": "1", "class": "A", "cid": 1, "name": "foo"},
                        {"id": 1, "year": "1", "name": "A"},
                    ),
                    (
                        {"id": 2, "year": "1", "class": "A", "cid": 1, "name": "bar"},
                        {"id": 1, "year": "1", "name": "A"},
                    ),
                    (
                        {"id": 3, "year": "1", "class": "B", "cid": 2, "name": "boo"},
                        {"id": 2, "year": "1", "name": "B"},
                    ),
                    (
                        {"id": 4, "year": "1", "class": "C", "cid": 3, "name": "yoo"},
                        {"id": 3, "year": "1", "name": "C"},
                    ),
                ],
            ),
        ]
        for c in cases:
            with self.subTest(msg=c.msg, kwargs=c.kwargs):
                got = self._callFUT(*c.args, **c.kwargs)

                self.assertTrue(
                    got == c.want, msg=_DifferenceReportText(got=got, want=c.want)
                )

                self.assertTrue(data.students == copied.students, "not modified")
                self.assertTrue(data.classes == copied.classes, "not modified")


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
