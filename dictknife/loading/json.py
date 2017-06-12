from collections import OrderedDict
from .util import LazyImporter
importer = LazyImporter()


@importer.setup
def import_json():
    import json
    return json


@importer.use
def load(m, fp, *, loader=None):
    return m.load(fp, object_pairs_hook=OrderedDict)


@importer.use
def dump(m, d, fp):
    return m.dump(d, fp, ensure_ascii=False, indent=2, default=str)
