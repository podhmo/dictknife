from .util import LazyImporter
importer = LazyImporter()


@importer.setup
def import_toml():
    import toml
    return toml


@importer.use
def load(m, fp, *, loader=None, **kwargs):
    return m.load(fp, **kwargs)


@importer.use
def dump(m, *args, **kwargs):
    return m.dump(*args, **kwargs)
