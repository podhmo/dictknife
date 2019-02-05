import sys
from dictknife.jsonknife import bundle
from dictknife import loading
from dictknife import DictWalker


def onload(d, resolver, w=DictWalker(["$xref"])):
    for path, sd in w.walk(d):
        subresolver, jsonref = resolver.resolve(sd.pop("$xref"))
        value = subresolver.access_by_json_pointer(jsonref)
        resolver.assign(path[:-1], value)


loading.dumpfile(bundle(sys.argv[1], onload=onload))
