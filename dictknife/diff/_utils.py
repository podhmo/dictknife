def _normalize_dict(d):  # side effect!
    if hasattr(d, "keys"):
        for k, v in list(d.items()):
            d[str(k)] = d.pop(k)
            _normalize_dict(v)
    elif isinstance(d, (list, tuple)):
        for x in d:
            _normalize_dict(x)
