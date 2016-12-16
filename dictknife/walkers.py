from collections import deque
from .operators import apply


class LooseDictWalker(object):
    def __init__(self, on_container=None, on_data=None):
        self.on_container = on_container
        self.on_data = on_data

    def on_found(self, path, d, k):
        if self.on_container is not None:
            self.on_container(path, d)
        if self.on_data is not None:
            self.on_data(path, d[k])

    def walk(self, qs, d, depth=-1):
        return self._walk([], deque(qs), d, depth=depth)

    def _walk(self, path, qs, d, depth):
        if depth == 0:
            return

        if not qs:
            return

        if hasattr(d, "keys"):
            for k in list(d.keys()):
                path.append(k)
                if apply(qs[0], k):
                    q = qs.popleft()
                    self._walk(path, qs, d[k], depth - 1)
                    if len(qs) == 0:
                        self.on_found(path, d, k)
                    qs.appendleft(q)
                else:
                    self._walk(path, qs, d[k], depth)
                path.pop()
            return d
        elif isinstance(d, (list, tuple)):
            path.append("[]")
            for e in d:
                self._walk(path, qs, e, depth)
            path.pop()
            return d
        else:
            return d
