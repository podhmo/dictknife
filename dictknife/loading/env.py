import sys
import os.path
from collections import OrderedDict


def emit_environ(structure, make_dict, parse):
    if hasattr(structure, "keys"):
        d = make_dict()
        for k, v in structure.items():
            name, fn = parse(v)
            emitted = emit_environ(name, make_dict=make_dict, parse=parse)
            if emitted is None:
                continue
            if fn is not None:
                emitted = fn(emitted)
            d[k] = emitted
        return d
    elif isinstance(structure, (list, tuple)):
        return [emit_environ(x, make_dict=make_dict, parse=parse) for x in structure]
    else:
        return os.environ.get(structure)


def parse_value(v, builtins=sys.modules["builtins"]):
    if ":" not in v:
        return v, None

    name, fnname = v.rsplit(":", 1)
    if not hasattr(builtins, fnname):
        return v, None
    else:
        return name, getattr(builtins, fnname)


def load(fp, *, loader=None, make_dict=OrderedDict, parse=parse_value):
    fname = getattr(fp, "name", "(unknown)")
    basename = os.path.splitext(fname)[0]
    load = loader.dispatcher.dispatch(basename, loader.fn_map)
    template_dict = load(fp)
    return emit_environ(template_dict, make_dict=make_dict, parse=parse)
