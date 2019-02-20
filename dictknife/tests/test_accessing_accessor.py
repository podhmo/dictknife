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

    def test_assign_list2(self):
        d = {"x": [1, 2, 3]}
        self._callFUT(d, ["x", 1], 10)
        expected = {"x": [1, 10, 3]}
        self.assertDictEqual(d, expected)

    def test_assign_list3(self):
        d = {"x": [1, 2, 3]}
        self._callFUT(d, ["x", 5], 10)
        expected = {"x": [1, 2, 3, None, None, 10]}
        self.assertDictEqual(d, expected)

    def test_assign_list4(self):
        d = {"x": [1, 2]}
        self._callFUT(d, ["x", 1, "a"], 10)
        expected = {"x": [1, {"a": 10}]}
        self.assertDictEqual(d, expected)

    def test_assign_list5(self):
        d = {"x": [1]}
        self._callFUT(d, ["x", 2], 3)
        self._callFUT(d, ["x", 1, "a"], 10)
        expected = {"x": [1, {"a": 10}, 3]}
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

    def test_assign_list_nested3(self):
        d = {"x": [{"name": "foo"}, {"name": "bar"}]}
        self._callFUT(d, ["x", 3, "name"], "boo")
        expected = {"x": [{"name": "foo"}, {"name": "bar"}, {}, {"name": "boo"}]}
        self.assertDictEqual(d, expected)

    def test_assign_list_nested4(self):
        d = {"x": [{"name": "foo"}]}
        self._callFUT(d, ["x", 3, "name"], "boo")
        self._callFUT(d, ["x", 1, "name"], "bar")
        expected = {"x": [{"name": "foo"}, {"name": "bar"}, {}, {"name": "boo"}]}
        self.assertDictEqual(d, expected)

    def test_assign_deeply(self):
        d = {}
        self._callFUT(d, [1, 2, 3, 4, 5, 6, 7, 8, 9], "foo")
        expected = {1: {2: {3: {4: {5: {6: {7: {8: {9: "foo"}}}}}}}}}
        self.assertDictEqual(d, expected)


if __name__ == "__main__":
    unittest.main()
