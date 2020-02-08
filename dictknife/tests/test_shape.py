import unittest
from collections import namedtuple


class Tests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.shape import shape

        return shape(*args, **kwargs)

    def test_it(self):
        C = namedtuple("C", "input, output, squash, skiplist")
        candidates = [
            C(input={}, output=[], squash=False, skiplist=False),
            C(input={"name": "foo"}, output=["name"], squash=False, skiplist=False),
            C(
                input={"name": "foo", "skills": []},
                output=["name", "skills"],
                squash=False,
                skiplist=False,
            ),
            C(
                input={"name": "foo", "skills": ["x"]},
                output=["name", "skills", "skills/[]"],
                squash=False,
                skiplist=False,
            ),
            C(
                input={"name": "foo", "age": 10},
                output=["age", "name"],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[
                    {"name": "foo", "age": 10},
                    {"nickname": "BIGb", "name": "bar", "age": 10},
                ],
                output=["[]", "[]/age", "[]/name", "?[]/nickname"],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[
                    [
                        {"name": "foo", "age": 10},
                        {"nickname": "BIGb", "name": "bar", "age": 10},
                    ]
                ],
                output=["[]", "[]/[]", "[]/[]/age", "[]/[]/name", "?[]/[]/nickname"],
                squash=False,
                skiplist=False,
            ),
            C(
                input={"person": {"name": "foo", "age": 10}},
                output=["person", "person/age", "person/name"],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[{"person": {"name": "foo", "age": 10}}],
                output=["[]", "[]/person", "[]/person/age", "[]/person/name"],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10}},
                    {"person": {"nickname": "BIGb", "name": "bar", "age": 10}},
                ],
                output=[
                    "[]",
                    "[]/person",
                    "[]/person/age",
                    "[]/person/name",
                    "?[]/person/nickname",
                ],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10}},
                    {"person": {"nickname": "BIGb", "name": "bar", "age": 10}},
                ],
                output=["person", "person/age", "person/name", "?person/nickname"],
                squash=True,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10, "skills": []}},
                    {"person": {"name": "bar", "age": 10, "skills": ["x"]}},
                ],
                output=[
                    "person",
                    "person/age",
                    "person/name",
                    "person/skills",
                    "?person/skills/[]",
                ],
                squash=True,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10}},
                    {"person": {"name": "bar", "age": 10, "skills": ["x"]}},
                ],
                output=[
                    "person",
                    "person/age",
                    "person/name",
                    "?person/skills",
                    "person/skills/[]",  # xxx
                ],
                squash=True,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10}},
                    {"person": {"name": "bar", "age": 10, "skills": ["x"]}},
                ],
                output=["person", "person/age", "person/name", "?person/skills"],
                squash=True,
                skiplist=True,
            ),
        ]
        for c in candidates:
            with self.subTest(input=c.input, squash=c.squash, skiplist=c.skiplist):
                got = self._callFUT(c.input, squash=c.squash, skiplist=c.skiplist)
                got = [row.path for row in got]
                self.assertEqual(c.output, got)
