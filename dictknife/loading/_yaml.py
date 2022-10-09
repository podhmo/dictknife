import ruamel.yaml

# dumping spec
# ----------------------------------------
#
# - ignore aliases
# - string representation
#   - use '|' when multi-line string
#   - quoted when contains '#' or ':'
# - Mapping type is treated as dict (e.g. defaultdict, ChainMap, OrderedDict)

_pool = {}  # xxx: memory leak


def load(fp, *args, typ="rt", **kwargs):
    yaml = ruamel.yaml.YAML(typ=typ)  # use round trip loader
    # use plugins?
    d = yaml.load(fp)
    _pool[id(d)] = yaml
    return d


def dump(d, fp, *args, typ="rt", **kwargs):
    yaml = _pool.get(id(d)) or ruamel.yaml.YAML(typ=typ)
    # use plugins?
    return yaml.dump(d, fp)
