from .expander import Expander  # noqa
from .bundler import Bundler  # noqa
from .resolver import (  # noqa
    get_resolver,
    get_resolver_from_filename,  # backward compatibility
)
from .example import extract as extract_example  # noqa
from .accessor import (  # noqa
    access_by_json_pointer,
    assign_by_json_pointer,
    path_to_json_pointer,
)
from ..langhelpers import make_dict
import os.path


def bundle(filename, *, jsonref=None, onload=None, doc=None, format=None):
    if "#/" in filename:
        filename, jsonref = filename.rsplit("#/", 1)

    if jsonref is not None:
        doc = make_dict()
        assign_by_json_pointer(
            doc,
            jsonref,
            {"$ref": f"{os.path.relpath(filename, start=os.getcwd())}#/{jsonref}"},
        )
        filename = os.path.join(os.getcwd(), f"*root*{os.path.splitext(filename)[1]}#/")
    resolver = get_resolver(filename, doc=doc, onload=onload, format=None)
    bundler = Bundler(resolver)
    r = bundler.bundle(resolver.doc)
    return r
