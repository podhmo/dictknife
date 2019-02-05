import sys
from dictknife.jsonknife import bundle
from dictknife import loading
loading.dumpfile(bundle(sys.argv[1]))
