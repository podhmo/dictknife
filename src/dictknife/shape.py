from functools import partial
from collections import defaultdict, namedtuple
from .langhelpers import as_jsonpointer
from typing import Iterator

Row = namedtuple("Row", "path, type, example")


class _State:
    def __init__(self) -> None:
        self.paths: list = []
        self.examples: defaultdict = defaultdict(list)

    def emit(self, path, example) -> None:
        path = tuple(path[:])
        if path not in self.examples:
            self.paths.append(path)
        self.examples[path].append(example)

    def count(self, path):
        return len(self.examples[path])

    def __iter__(self) -> Iterator:
        return iter(self.paths)


class Traverser:
    def __init__(self, iterate=partial(sorted, key=str)) -> None:
        self.iterate = iterate

    def traverse(self, d):
        s = _State()
        self._traverse(d, s, [])
        return s

    def _traverse(self, d, s, path) -> None:
        if hasattr(d, "keys"):
            self._traverse_dict(d, s, path)
        elif isinstance(d, (list, tuple)):
            self._traverse_list(d, s, path)
        else:
            self._traverse_atom(d, s, path)

    def _traverse_dict(self, d, s, path) -> None:
        s.emit(path, dict(d))
        for k in self.iterate(d.keys()):
            path.append(k)
            self._traverse(d[k], s, path)
            path.pop()

    def _traverse_list(self, xs, s, path) -> None:
        s.emit(path, list(xs))
        path.append("[]")
        for x in xs:
            self._traverse(x, s, path)
        path.pop()

    def _traverse_atom(self, v, s, path) -> None:
        s.emit(path, v)


def _build_pathlist_from_state(
    s,
    *,
    squash: bool = False,
    skiplist: bool = False,
    separator: str = "/",
    transform=str,
):  # str or _default_transform
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

        r.append(
            Row(
                path=fmt.format(separator.join(map(transform, path))),
                type=sorted(set([type(v) for v in s.examples[rawpath]]), key=str),
                example=s.examples[rawpath][0],
            )
        )
    return r


def shape(
    d,
    traverse=Traverser().traverse,
    aggregate=_build_pathlist_from_state,
    *,
    squash: bool = False,
    skiplist: bool = False,
    separator: str = "/",
    transform=as_jsonpointer,
):
    """Generates a summary of the structure (shape) of a dictionary-like object.

    It traverses the input object and identifies the paths to all elements,
    along with their types and an example value.

    Args:
        d: The dictionary-like object to analyze.
        traverse (callable, optional): A function that traverses the input object
            and returns an intermediate representation (_State object).
            Defaults to Traverser().traverse.
        aggregate (callable, optional): A function that processes the intermediate
            representation and returns the final list of Row namedtuples.
            Defaults to _build_pathlist_from_state.
        squash (bool, optional): If True, removes the initial "[]" from paths
            if the root is a list. Defaults to False.
        skiplist (bool, optional): If True, skips paths that end with "[]" (lists themselves).
            Defaults to False.
        separator (str, optional): The separator character to use when joining path segments.
            Defaults to "/".
        transform (callable, optional): A function to transform each path segment before joining.
            Defaults to `as_jsonpointer`.

    Returns:
        list[Row]: A list of Row namedtuples, where each Row represents a unique path
                   and contains `path` (str), `type` (list of types), and `example` (value).
    """
    return aggregate(
        traverse(d),
        squash=squash,
        skiplist=skiplist,
        separator=separator,
        transform=transform,
    )
