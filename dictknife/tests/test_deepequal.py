# -*- coding:utf-8 -*-
import unittest


class ref(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == self.value


class DeepEqualTests(unittest.TestCase):
    def _callFUT(self, left, right):
        from dictknife import deepequal
        return deepequal(left, right)

    def test_it(self):
        d0 = {
            "a": ref(1),
            "b": {
                "x": {
                    "i": ref(2)
                },
                "y": {
                    "j": ref(3)
                }
            }
        }
        d1 = {
            "a": ref(1),
            "b": {
                "x": {
                    "i": ref(2)
                },
                "y": {
                    "j": ref(3)
                }
            }
        }
        self.assertEqual(ref(1), ref(1), msg="prepare")
        self.assertEqual(d0, d1)
