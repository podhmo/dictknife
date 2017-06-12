from .util import LazyImporter

importer = LazyImporter()


@importer.setup
def import_yaml():
    from . import _yaml as m
    m.setup(m.Loader, m.Dumper)
    return m


@importer.use
def load(m, fp, *, loader=None, **kwargs):
    return m.load(fp, Loader=m.Loader, **kwargs)


@importer.use
def dump(m, d, fp):
    return m.dump(
        d, fp, allow_unicode=True, default_flow_style=False, Dumper=m.Dumper
    )
