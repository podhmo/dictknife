from dictknife import pp
from collections import OrderedDict, Counter

d = OrderedDict()
d["x"] = OrderedDict([("i", 0), ("j", 1), ("k", 2)])
d["y"] = "y"
d["z"] = OrderedDict([("a", 0), ("b", 1), ("c", 2)])
d["c"] = Counter(j for i in range(10) for j in range(i))

# sort by keys
pp(d)
