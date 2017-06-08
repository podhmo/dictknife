from dictknife import pp
from dictknife import deepmerge

d0 = {
    "name": "foo",
    "object": {
        "x": 1,
        "z": 1,
    },
    "children": [10],
    "a": {
        "b": {
            "x": "y"
        }
    },
}
d1 = {
    "name": "bar",
    "object": {
        "y": 2,
        "z": 3,
    },
    "children": [1, 2, 3],
    "a": {
        "b": {
            "c": "d",
            "x": "z",
        }
    },
}

pp(deepmerge(d0, d1, override=True))
