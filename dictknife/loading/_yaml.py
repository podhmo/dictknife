import yaml
import re
from collections import defaultdict, ChainMap, OrderedDict
from dictknife.langhelpers import make_dict

load = yaml.load
dump = yaml.dump


class Dumper(yaml.Dumper):
    def _iterate_dict(self, d):
        return d.items()

    def ignore_aliases(self, data):
        return True


class SortedDumper(Dumper):
    def _iterate_dict(self, d):
        return sorted(d.items())


class Loader(yaml.Loader):
    pass


def setup(Loader, Dumper, dict_classes=[defaultdict, ChainMap, OrderedDict]):
    def _represent_odict(dumper, instance):
        return dumper.represent_mapping('tag:yaml.org,2002:map', dumper._iterate_dict(instance))

    def _construct_odict(loader, node):
        return make_dict(loader.construct_pairs(node))

    def _represent_str(dumper, instance, _rx=re.compile("[\n#]")):
        m = _rx.search(instance)
        if m is None:
            return dumper.represent_scalar('tag:yaml.org,2002:str', instance)
        elif m.group(0) == "#":
            return dumper.represent_scalar('tag:yaml.org,2002:str', instance, style="'")
        else:
            return dumper.represent_scalar('tag:yaml.org,2002:str', instance, style="#")

    Loader.add_constructor('tag:yaml.org,2002:map', _construct_odict)
    for dict_class in dict_classes:
        Dumper.add_representer(dict_class, _represent_odict)
    Dumper.add_representer(str, _represent_str)
