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
    yaml.preserve_quotes = True
    # use plugins?
    d = yaml.load(fp)
    _pool[id(d)] = yaml
    return d


def dump(d, fp, *args, typ="rt", **kwargs):
    yaml = _pool.get(id(d)) or ruamel.yaml.YAML(typ=typ)

    def ignore_aliases(data) -> bool:
        return True

    yaml.indent(mapping=2, sequence=2, offset=0)
    yaml.representer.ignore_aliases = ignore_aliases
    # use plugins?
    return yaml.dump(d, fp)
