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
from ..langhelpers import make_dict, pairrsplit
import os.path


def bundle(filename, onload=None, doc=None, format=None, extras=None):
    filename, jsonref = pairrsplit(filename, "#/")

    if jsonref:
        doc = make_dict()
        cwd = os.getcwd()

        ref = f"{os.path.relpath(filename, start=cwd)}#/{jsonref}"
        assign_by_json_pointer(doc, jsonref, {"$ref": ref})
        filename = os.path.join(cwd, f"*root*{os.path.splitext(filename)[1]}#/")

        # adding multi files
        if extras is not None:
            for efilename in extras:
                efilename, ejsonref = pairrsplit(efilename, "#/")
                if not ejsonref:
                    raise ValueError(
                        "{efilename!r} is not json reference. (please <filename>#/<reference>)"
                    )
                eref = f"{os.path.relpath(efilename, start=cwd)}#/{ejsonref}"
            assign_by_json_pointer(doc, ejsonref, {"$ref": eref})

    resolver = get_resolver(filename, doc=doc, onload=onload, format=None)
    bundler = Bundler(resolver)
    r = bundler.bundle(resolver.doc)
    return r
