from collections import namedtuple
diff = namedtuple("diff", "op, value, x_from, x_to")


def make_jsonpatch(src, dst, *, verbose=False):
    # iterator?
    if hasattr(src, "__next__"):
        src = list(src)
    if hasattr(dst, "__next__"):
        dst = list(dst)

    r = _Walker().walk(src, dst)
    rows = _merge(r)

    if not verbose:
        for row in rows:
            if row["op"] == "remove":
                row.pop("value", None)
            for k in list(row.keys()):
                if k.startswith("x_"):
                    row.pop(k)
            yield row
    else:
        for row in rows:
            if row["op"] == "remove":
                row.pop("value", None)
                row.pop("x_to", None)
            elif row["op"] == "add":
                row.pop("x_from", None)
                row.pop("x_to", None)
            elif row["op"] == "replace":
                row.pop("x_to", None)
            for k in list(row.keys()):
                if not k.startswith("x_"):
                    continue
                row[k.replace("x_", "x-")] = row.pop(k)
            yield row


def _merge(r):
    if r is None:
        return []
    if not hasattr(r, "keys"):
        yield {"path": "", **r._asdict()}
    else:
        for k, v in r.items():
            prefix = str(k).replace("~", "~0").replace("/", "~1")
            for sv in _merge(v):
                sv["path"] = "/{prefix}/{subpath}".format(prefix=prefix, subpath=sv['path'].lstrip('/')).rstrip("/")
                yield sv


class _Walker:
    # two path scan move, copy
    def __init__(self):
        self.move_map = {}  # todo:

    def walk(self, src, dst):
        # xxx: src and dst is None
        if hasattr(src, "keys"):
            return self._walk_dict(src, dst)
        elif isinstance(src, (list, tuple)):
            return self._walk_list(src, dst)
        else:
            return self._walk_atom(src, dst)

    def _walk_list(self, src, dst):
        r = {}
        try:
            n = min(len(src), len(dst))
        except TypeError:
            return diff(op="replace", value=dst, x_from=src, x_to=dst)
        for i in range(n):
            r[str(i)] = self.walk(src[i], dst[i])

        if n == len(dst):
            for i in range(n, len(src)):
                r[str(i)] = diff(op="remove", value=None, x_from=src[i], x_to=None)
        else:
            for i in range(n, len(dst)):
                r[str(i)] = diff(op="add", value=dst[i], x_from=None, x_to=dst[i])
        return r

    def _walk_dict(self, src, dst):
        r = {}
        for k, v in src.items():
            if k in dst:
                r[k] = self.walk(v, dst[k])
            else:
                r[k] = diff("remove", value=None, x_from=v, x_to=None)
        for k, v in dst.items():
            if k in r:
                continue
            r[k] = diff("add", value=v, x_from=None, x_to=v)
        return r

    def _walk_atom(self, src, dst):
        if src is None:
            return diff(op="add", value=dst, x_from=None, x_to=dst)
        elif dst is None:
            return diff(op="remove", value=None, x_from=src, x_to=None)
        elif src != dst:
            return diff(op="replace", value=dst, x_from=src, x_to=dst)
        else:
            return None
