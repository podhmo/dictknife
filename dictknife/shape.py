from functools import partial
from collections import defaultdict


class _State:
    def __init__(self):
        self.xs = []
        self.c = defaultdict(int)
        self.i = 0

    def add(self, x):
        x = tuple(x[:])
        if x not in self.c:
            self.xs.append(x)
        self.c[x] += 1

    def __iter__(self):
        return iter(self.xs)


class Traverser:
    def __init__(self, iterate=partial(sorted, key=str)):
        self.iterate = iterate

    def traverse(self, d):
        s = _State()
        self._traverse(d, s, [])
        return s

    def _traverse(self, d, s, path):
        if hasattr(d, "keys"):
            self._traverse_dict(d, s, path)
        elif isinstance(d, (list, tuple)):
            self._traverse_list(d, s, path)
        else:
            self._traverse_atom(d, s, path)

    def _traverse_dict(self, d, s, path):
        s.add(path)
        for k in self.iterate(d.keys()):
            path.append(k)
            self._traverse(d[k], s, path)
            path.pop()

    def _traverse_list(self, xs, s, path):
        s.add(path)
        path.append("[]")
        for x in xs:
            self._traverse(x, s, path)
        path.pop()

    def _traverse_atom(self, v, s, path):
        s.add(path)


def convert_pathlist_from_state(s, *, squash=False, skiplist=False):
    r = []
    for path in s.xs:
        if not path:
            continue
        if skiplist and path[-1] == "[]":
            continue
        parent_frequency = s.c[path[:-1]]
        frequency = s.c[path]
        if len(path) > 2 and path[-2] == "[]" and (len(path) == 2 or path[-3] != "[]"):
            parent_frequency -= 1

        is_optional = parent_frequency - frequency > 0
        fmt = "{}"
        if is_optional:
            fmt = "?{}"
        if squash and path[0] == "[]":
            path = path[1:]
            if not path:
                continue
        r.append(fmt.format("/".join(path)))
    return r


def shape(
    d,
    traverse=Traverser().traverse,
    aggregate=convert_pathlist_from_state,
    squash=False,
    skiplist=False
):
    return aggregate(traverse(d), squash=squash, skiplist=skiplist)
