from .expander import Expander  # NOQA
from .bundler import Bundler  # NOQA
from .resolver import get_resolver_from_filename  # NOQA
from .example import extract as extract_example  # NOQA
from .accessor import (  # NOQA
    access_by_json_pointer,
    assign_by_json_pointer,
    path_to_json_pointer,
)


def bundle(filename, *, onload=None, doc=None):
    resolver = get_resolver_from_filename(filename, doc=doc, onload=onload)
    bundler = Bundler(resolver)
    return bundler.bundle()
