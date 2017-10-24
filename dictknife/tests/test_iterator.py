import unittest


class IteratorTests(unittest.TestCase):
    def _getTargetClass(self):
        from dictknife import LooseDictWalkingIterator
        return LooseDictWalkingIterator

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_rec(self):
        from dictknife.operators import ANY
        s = []

        d = {"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}}
        iterator = self._makeOne([ANY, "b"])
        for path, value in iterator.iterate(d):
            s.append(value)
            for path, value in iterator.iterate(value):
                s.append(value)
                for path, value in iterator.iterate(value):
                    s.append(value)

        expected = [{'b': {'a': {'b': {'a': {'b': 10}}}}}, {'b': {'a': {'b': 10}}}, {'b': 10}]

        self.assertEqual(s, expected)

    def test_has(self):
        doc = {
            "paths": {
                "/": {
                    "get": {
                        "operationId": "index",
                        "responses": {
                            "200": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {
                                            "type": "string"
                                        },
                                        "age": {
                                            "type": "integer"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        iterator = self._makeOne(["operationId"])
        iterator2 = self._makeOne(["schema"])
        for path, d in iterator.iterate(doc):
            operation_id = d["operationId"]
            for path2, sd in iterator2.iterate(d):
                name = "{}Schema".format(operation_id)
                doc["definitions"] = {name: sd["schema"]}
                sd["schema"] = {"$ref": "#/definitions/{}".format(name)}

        self.assertEqual(
            doc["paths"]["/"]["get"]["responses"]["200"]["schema"],
            {"$ref": "#/definitions/indexSchema"}
        )
        self.assertIn("name", doc["definitions"]["indexSchema"]["properties"])
        self.assertIn("age", doc["definitions"]["indexSchema"]["properties"])
