import unittest


class AssignTests(unittest.TestCase):
    def _callFUT(self, d, k, v):
        from dictknife import Accessor

        a = Accessor(make_dict=dict)
        return a.assign(d, k, v)

    def test_assign_dict(self):
        d = {}
        self._callFUT(d, ["x"], 1)
        expected = {"x": 1}
        self.assertDictEqual(d, expected)

    def test_assign_dict_nested(self):
        d = {}
        self._callFUT(d, ["x", "y"], 1)
        expected = {"x": {"y": 1}}
        self.assertDictEqual(d, expected)

    def test_assign_list(self):
        d = {"x": []}
        self._callFUT(d, ["x", 0], 1)
        expected = {"x": [1]}
        self.assertDictEqual(d, expected)

    def test_assign_list(self):
        d = {"x": []}
        self._callFUT(d, ["x", 1], 1)
        expected = {"x": [None, 1]}
        self.assertDictEqual(d, expected)

    def test_assign_list_nested(self):
        d = {"x": []}
        self._callFUT(d, ["x", 0, "name"], "foo")
        expected = {"x": [{"name": "foo"}]}
        self.assertDictEqual(d, expected)

    def test_assign_list_nested2(self):
        d = {"x": []}
        self._callFUT(d, ["x", 1, "name"], "foo")
        expected = {"x": [{}, {"name": "foo"}]}
        self.assertDictEqual(d, expected)


if __name__ == "__main__":
    unittest.main()
