from dictknife.jsonknife.lifting import Flattener, Handler


def flatten(data, replace=True):
    if "definitions" not in data:
        return data
    w = Flattener(replace=replace)
    for name in list(data["definitions"].keys()):
        prop = data["definitions"].pop(name)
        extracted = w.extract(prop, Handler([name]))
        extracted[name] = prop
        data["definitions"].update(reversed(extracted.items()))
    return data
