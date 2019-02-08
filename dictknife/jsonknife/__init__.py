from .expander import Expander  # noqa
from .bundler import Bundler  # noqa
from .resolver import (  # noqa
    get_resolver,
    get_resolver_from_filename,  # backward compatibility
    build_subset,
)
from .example import extract as extract_example  # noqa
from .accessor import (  # noqa
    access_by_json_pointer,
    assign_by_json_pointer,
    path_to_json_pointer,
)


def bundle(filename, *, jsonref=None, onload=None, doc=None, format=None):
    if "#/" in filename:
        filename, jsonref = filename.rsplit("#/", 1)
    resolver = get_resolver_from_filename(filename, doc=doc, onload=onload, format=None)
    bundler = Bundler(resolver)
    doc = resolver.doc
    if jsonref is not None:
        doc = build_subset(resolver, jsonref)
    return bundler.bundle(doc)
