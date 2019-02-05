from dictknife import deepequal
from collections import OrderedDict, Counter

d0 = {"a": 1, "b": {"x": OrderedDict({"i": 2}), "y": Counter({"j": 3})}}

d1 = {"a": 1, "b": {"x": Counter({"i": 2}), "y": {"j": 3}}}

# in almost case, this is ok.
print("==")
print("\t", d0 == d1)

print("deepequal")
print("\t", deepequal(d0, d1))
