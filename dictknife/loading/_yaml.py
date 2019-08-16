import re
from collections import defaultdict, ChainMap, OrderedDict
from dictknife.langhelpers import make_dict
import yaml
from yaml.representer import SafeRepresenter

load = yaml.load
dump = yaml.dump


class Dumper(yaml.Dumper):
    def _iterate_dict(self, d):
        return d.items()

    def ignore_aliases(self, data):
        return True


class Loader(yaml.Loader):
    pass


def setup(Loader, Dumper, dict_classes=[defaultdict, ChainMap, OrderedDict]):
    def _construct_odict(loader, node):
        return make_dict(loader.construct_pairs(node))

    def _represent_str(dumper, instance, _rx=re.compile("[#:]")):
        style = None
        if "\n" in instance:
            style = "|"
        else:
            m = _rx.search(instance)
            if m is not None:
                style = "'"
        return dumper.represent_scalar("tag:yaml.org,2002:str", instance, style=style)

    Loader.add_constructor("tag:yaml.org,2002:map", _construct_odict)
    for dict_class in dict_classes:
        Dumper.add_representer(dict_class, SafeRepresenter.represent_dict)
    Dumper.add_representer(str, _represent_str)
