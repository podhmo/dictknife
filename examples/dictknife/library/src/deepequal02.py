from dictknife import deepequal

d0 = [[[1, 2, 3], [1]], [[1, 2], [2, 3], [3, 4]]]
d1 = [[[1], [1, 2, 3]], [[1, 2], [3, 4], [2, 3]]]

print("=")
print(d0 == d1)
print("deepequal")
print(deepequal(d0, d1, normalize=True))
