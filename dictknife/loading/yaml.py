from collections import OrderedDict, defaultdict, ChainMap
from .util import LazyImporter, ImportPromise

importer = LazyImporter()


@importer.setup
def import_yaml():
    import yaml

    class IgnoreReferenceDumper(yaml.Dumper):
        def ignore_aliases(self, data):
            return True

    yaml.IgnoreReferenceDumper = IgnoreReferenceDumper
    return ImportPromise(module=yaml, cont=setup)


@importer.use
def load(m, fp, *, loader=None, **kwargs):
    return m.load(fp, **kwargs)


@importer.use
def dump(m, d, fp):
    return m.dump(
        d, fp, allow_unicode=True, default_flow_style=False, Dumper=m.IgnoreReferenceDumper
    )


@importer.use
def setup(m, dict_classes=[OrderedDict, defaultdict, ChainMap]):
    def _represent_odict(dumper, instance):
        return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())

    def _construct_odict(loader, node):
        return OrderedDict(loader.construct_pairs(node))

    def _represent_str(dumper, instance):
        if "\n" in instance:
            return dumper.represent_scalar('tag:yaml.org,2002:str', instance, style='|')
        else:
            return dumper.represent_scalar('tag:yaml.org,2002:str', instance)

    m.add_constructor('tag:yaml.org,2002:map', _construct_odict)
    for dict_class in dict_classes:
        m.add_representer(dict_class, _represent_odict)
    m.add_representer(str, _represent_str)
