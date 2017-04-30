import yaml
from collections import OrderedDict, defaultdict, ChainMap


class IgnoreReferenceDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


load = yaml.load


def dump(d, fp):
    return yaml.dump(d, fp, allow_unicode=True, default_flow_style=False, Dumper=IgnoreReferenceDumper)


def setup(dict_classes=[OrderedDict, defaultdict, ChainMap]):
    def _represent_odict(dumper, instance):
        return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

    def _construct_odict(loader, node):
        return OrderedDict(loader.construct_pairs(node))

    yaml.add_constructor('tag:yaml.org,2002:map', _construct_odict)
    for dict_class in dict_classes:
        yaml.add_representer(dict_class, _represent_odict)
