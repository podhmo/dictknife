from functools import partial
from collections import defaultdict, namedtuple
Row = namedtuple("Row", "path, type, example")


class _State:
    def __init__(self):
        self.paths = []
        self.examples = defaultdict(list)

    def emit(self, path, example):
        path = tuple(path[:])
        if path not in self.examples:
            self.paths.append(path)
        self.examples[path].append(example)

    def count(self, path):
        return len(self.examples[path])

    def __iter__(self):
        return iter(self.paths)


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
        s.emit(path, dict(d))
        for k in self.iterate(d.keys()):
            path.append(k)
            self._traverse(d[k], s, path)
            path.pop()

    def _traverse_list(self, xs, s, path):
        s.emit(path, list(xs))
        path.append("[]")
        for x in xs:
            self._traverse(x, s, path)
        path.pop()

    def _traverse_atom(self, v, s, path):
        s.emit(path, v)


def convert_pathlist_from_state(s, *, squash=False, skiplist=False, separator="/"):
    r = []
    for path in s.paths:
        if not path:
            continue
        if skiplist and path[-1] == "[]":
            continue
        rawpath = path

        parent_frequency = s.count(path[:-1])
        frequency = s.count(path)
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

        types = sorted(set([type(v).__name__ for v in s.examples[rawpath]]))
        r.append(
            Row(
                path=fmt.format(separator.join(map(str, path))),
                type=types[0] if len(types) == 1 else types,
                example=s.examples[rawpath][0]
            )
        )
    return r


def shape(
    d,
    traverse=Traverser().traverse,
    aggregate=convert_pathlist_from_state,
    squash=False,
    skiplist=False,
    separator="/",
):
    return aggregate(
        traverse(d),
        squash=squash,
        skiplist=skiplist,
        separator=separator,
    )
