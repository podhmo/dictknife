from .expander import Expander  # noqa
from .bundler import Bundler  # noqa
from .resolver import get_resolver, get_resolver_from_filename  # noqa
from .example import extract as extract_example  # noqa
from .accessor import (  # noqa
    access_by_json_pointer,
    assign_by_json_pointer,
    path_to_json_pointer,
)


def bundle(filename, *, onload=None, doc=None):
    resolver = get_resolver_from_filename(filename, doc=doc, onload=onload)
    bundler = Bundler(resolver)
    return bundler.bundle()
