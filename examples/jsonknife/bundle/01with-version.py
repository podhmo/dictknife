import sys
from dictknife.jsonknife import bundle
from dictknife import loading


def onload(d, resolver):
    resolver.doc["version"] = 1.0  # infinite recursion


loading.dumpfile(bundle(sys.argv[1], onload=onload))
