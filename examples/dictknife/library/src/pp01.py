from dictknife import pp
from collections import Counter

d = dict()
d["x"] = dict([("i", 0), ("j", 1), ("k", 2)])
d["y"] = "y"
d["z"] = dict([("a", 0), ("b", 1), ("c", 2)])
d["c"] = Counter(j for i in range(10) for j in range(i))

# sort by keys
pp(d)
