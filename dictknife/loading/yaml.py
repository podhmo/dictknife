import yaml
from collections import OrderedDict, defaultdict, ChainMap


class IgnoreReferenceDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


def load(fp, *, loader=None, **kwargs):
    return yaml.load(fp, **kwargs)


def dump(d, fp):
    return yaml.dump(
        d, fp, allow_unicode=True, default_flow_style=False, Dumper=IgnoreReferenceDumper
    )


def setup(dict_classes=[OrderedDict, defaultdict, ChainMap]):
    def _represent_odict(dumper, instance):
        return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

    def _construct_odict(loader, node):
        return OrderedDict(loader.construct_pairs(node))

    def _represent_str(dumper, instance):
        if "\n" in instance:
            return dumper.represent_scalar('tag:yaml.org,2002:str', instance, style='|')
        else:
            return dumper.represent_scalar('tag:yaml.org,2002:str', instance)

    yaml.add_constructor('tag:yaml.org,2002:map', _construct_odict)
    for dict_class in dict_classes:
        yaml.add_representer(dict_class, _represent_odict)
    yaml.add_representer(str, _represent_str)
