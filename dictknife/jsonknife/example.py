from dictknife.langhelpers import make_dict


class State:
    def __init__(self, *, limit=5):
        self.max_examples = 1
        self.limit = limit
        self.i = 0


def _extract(state, d, *, path=None):
    path = path or []
    typ = d.get("type")
    if "properties" in d or typ == "object":
        return _extract_object(
            state, d.get("properties") or {}, r=make_dict(), path=path
        )
    elif typ == "array":
        return _extract_array(state, d["items"], r=[], path=path)
    elif "example" in d:
        if isinstance(d["example"], (list, tuple)) and d["type"] != "array":
            size = min(state.limit, len(d["example"]))
            state.max_examples = max(state.max_examples, size)
            return d["example"][min(state.i, len(d["example"]) - 1)]
        return d["example"]
    elif "enum" in d:
        size = min(state.limit, len(d["enum"]))
        state.max_examples = max(state.max_examples, size)
        return d["enum"][min(state.i, len(d["enum"]) - 1)]
    elif "default" in d:
        return d["default"]
    else:
        return "<>"


def _extract_object(state, props, *, r, path):
    for name, value in props.items():
        path.append(name)
        r[name] = _extract(state, value, path=path)
        path.pop()
    return r


def _extract_array(state, items, *, r, path):
    for i, item in enumerate(items):
        path.append(str(i))
        r.append(_extract(state, items, path=path))
        path.pop()
    return r


def extract(d, *, limit=5):
    """example value from swagger's example and default"""
    s = State(limit=limit)
    r = _extract(s, d)
    if s.max_examples > 1:
        r = [r]
        for i in range(1, s.max_examples):
            s.i = i
            r.append(_extract(s, d))
    return r
