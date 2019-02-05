import unittest
import json
from collections import namedtuple


class Tests(unittest.TestCase):
    def _callFUT(self, src, dst):
        from dictknife.jsonknife.patch import make_jsonpatch
        return make_jsonpatch(src, dst)

    maxDiff = None

    def test(self):
        import jsonpatch

        C = namedtuple("C", "src, dst, want, skip_patch")
        cases = [
            C(
                src={"name": "foo"},
                dst={"name": "foo"},
                want=[],
                skip_patch=False,
            ),
            C(
                src={"name": "foo"},
                dst={"name": "bar"},
                want=[{
                    "op": "replace",
                    "path": "/name",
                    "value": "bar"
                }],
                skip_patch=False,
            ),
            C(
                src={"name": "foo"},
                dst={},
                want=[{
                    "op": "remove",
                    "path": "/name"
                }],
                skip_patch=False,
            ),
            C(
                src={},
                dst={"name": "bar"},
                want=[{
                    "op": "add",
                    "path": "/name",
                    "value": "bar"
                }],
                skip_patch=False,
            ),
            C(
                src={"point0": {
                    "value": 10
                }},
                dst={"point1": {
                    "value": 10
                }},
                # todo: move
                want=[
                    {
                        "op": "remove",
                        "path": "/point0",
                    },
                    {
                        "op": "add",
                        "path": "/point1",
                        "value": {
                            "value": 10
                        },
                    },
                ],
                skip_patch=False,
            ),
            C(
                src={"point0": {
                    "value": 10
                }},
                dst={"point0": {
                    "value": 20
                }},
                want=[
                    {
                        "op": "replace",
                        "path": "/point0/value",
                        "value": 20,
                    },
                ],
                skip_patch=False,
            ),
            C(
                src={"person": {
                    "name": "foo",
                    "age": 20,
                    "type": "P"
                }},
                dst={"person": {
                    "name": "bar",
                    "nickname": "B",
                    "type": "P"
                }},
                want=[
                    {
                        "op": "replace",
                        "path": "/person/name",
                        "value": "bar",
                    },
                    {
                        "op": "remove",
                        "path": "/person/age",
                    },
                    {
                        "op": "add",
                        "path": "/person/nickname",
                        "value": "B",
                    },
                ],
                skip_patch=False,
            ),
            C(
                src=[{}, {
                    "person": {
                        "name": "foo",
                        "age": 20,
                        "type": "P"
                    }
                }],
                dst=[{
                    "person": {
                        "name": "bar",
                        "nickname": "B",
                        "type": "P"
                    }
                }, {}],
                want=[
                    {
                        "path": "/0/person",
                        "op": "add",
                        "value": {
                            "name": "bar",
                            "nickname": "B",
                            "type": "P"
                        }
                    },
                    {
                        "path": "/1/person",
                        "op": "remove",
                    },
                ],
                skip_patch=False,
            ),
            C(
                src=None,
                dst=1,
                want=[{
                    "op": "add",
                    "path": "",  # root is ""
                    "value": 1
                }],
                skip_patch=True,
            ),
            ## runtime error
            # C(
            #     src={},
            #     dst=1,
            #     want=[{
            #         "op": "add",
            #         "path": "/",
            #         "value": 1
            #     }],
            #     skip_patch=True,
            # )
            C(
                src={"v": 1},
                dst={"v": [1]},
                want=[{
                    "op": "replace",
                    "path": "/v",
                    "value": [1],
                }],
                skip_patch=False,
            ),
            C(
                src={"v": [1]},
                dst={"v": 1},
                want=[{
                    "op": "replace",
                    "path": "/v",
                    "value": 1,
                }],
                skip_patch=False,
            ),
            C(
                src={
                    "name": "foo",
                    "age": 20
                },
                dst={"person": {
                    "name": "foo",
                    "age": 20
                }},
                # move ?
                want=[
                    {
                        "op": "add",
                        "path": "/person",
                        "value": {
                            "age": 20,
                            "name": "foo"
                        }
                    },
                    {
                        "op": "remove",
                        "path": "/age"
                    },
                    {
                        "op": "remove",
                        "path": "/name"
                    },
                ],
                skip_patch=False,
            ),
            C(
                src={
                    "person": {
                        "name": "foo",
                        "age": 20,
                    },
                },
                dst={
                    "name": "foo",
                    "age": 20
                },
                # move ?
                want=[
                    {
                        "op": "remove",
                        "path": "/person",
                    },
                    {
                        "op": "add",
                        "path": "/age",
                        "value": 20,
                    },
                    {
                        "op": "add",
                        "path": "/name",
                        "value": "foo"
                    },
                ],
                skip_patch=False,
            )
        ]

        for i, c in enumerate(cases):
            with self.subTest(i):
                got = list(self._callFUT(c.src, c.dst))
                if not c.skip_patch:
                    self.assertEqual(jsonpatch.JsonPatch(got).apply(c.src), c.dst)
                self.assertListEqual(
                    sorted([json.dumps(x, sort_keys=True) for x in got]),
                    sorted([json.dumps(x, sort_keys=True) for x in c.want])
                )
