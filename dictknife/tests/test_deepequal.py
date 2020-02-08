# -*- coding:utf-8 -*-
import unittest


class ref(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == self.value


class DeepEqualTests(unittest.TestCase):
    def _callFUT(self, left, right, normalize):
        from dictknife import deepequal

        return deepequal(left, right, normalize=normalize)

    def test_it(self):
        d0 = {
            "a": ref(1),
            "b": {"x": {"i": ref(2)}, "y": {"j": ref(3)}},
        }
        d1 = {
            "a": ref(1),
            "b": {"x": {"i": ref(2)}, "y": {"j": ref(3)}},
        }
        self.assertEqual(ref(1), ref(1), msg="prepare")
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it2(self):
        d0 = {"color": {"type": "string", "enum": ["C", "M", "Y", "K"],}}
        d1 = {"color": {"type": "string", "enum": ["K", "Y", "M", "C"],}}
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it3(self):
        from dictknife.langhelpers import make_dict

        d0 = make_dict([("type", "string"), ("enum", ["C", "M", "Y", "K"])])
        d1 = make_dict([("type", "string"), ("enum", ["K", "Y", "M", "C"])])
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it4(self):
        d0 = [[[1, 2, 3], [1]], [[1, 2], [2, 3], [3, 4]]]
        d1 = [[[1], [1, 2, 3]], [[1, 2], [3, 4], [2, 3]]]
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it5(self):
        d0 = [
            {"xs": [{"name": "i"}, {"name": "j"}, {"name": "k"}]},
            {"xs": [{"name": "x"}, {"name": "y"}, {"name": "z"}]},
        ]
        d1 = [
            {"xs": [{"name": "y"}, {"name": "x"}, {"name": "z"}]},
            {"xs": [{"name": "k"}, {"name": "j"}, {"name": "i"}]},
        ]
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it6(self):
        d0 = [
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[10, 11, 12], [11, 12, 13], [12, 13, 14]],
            [[100, 101, 102], [101, 102, 103], [102, 103, 104]],
        ]
        d1 = [
            [[11, 12, 13], [12, 13, 14], [10, 11, 12]],
            [[2, 3, 4], [1, 2, 3], [0, 1, 2]],
            [[102, 103, 104], [100, 101, 102], [101, 102, 103]],
        ]
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))
