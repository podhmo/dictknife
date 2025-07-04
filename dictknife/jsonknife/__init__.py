from .expander import Expander  # noqa
from .bundler import Bundler, create_scanner_factory_from_flavor  # noqa
from .separator import Separator  # noqa
from .resolver import (  # noqa
    get_resolver,
    get_resolver_from_filename,  # backward compatibility
)
from .example import extract as extract_example  # noqa
from .accessor import (  # noqa
    access_by_json_pointer,
    assign_by_json_pointer,
    path_to_json_pointer,
    json_pointer_to_path,
)
from ..langhelpers import make_dict, pairrsplit
import os.path


def expand(filename, *, onload=None, doc=None, format=None):
    resolver = get_resolver(filename, doc=doc, onload=onload, format=format)
    expander = Expander(resolver)
    return expander.expand()


def bundle(
    filename,
    *,
    onload=None,
    doc=None,
    format=None,
    extras=None,
    flavor: str = "openapiv2",
):
    jsonref = ""
    if filename:
        filename, jsonref = pairrsplit(filename, "#/")

    if jsonref:
        doc = make_dict()
        cwd = os.getcwd()

        ref = "{prefix}#/{jsonref}".format(
            prefix=os.path.relpath(filename, start=cwd), jsonref=jsonref
        )
        assign_by_json_pointer(doc, jsonref, {"$ref": ref})
        filename = os.path.join(
            cwd, "*root*{name}#/".format(name=os.path.splitext(filename)[1])
        )

        # adding multi files
        if extras is not None:
            for efilename in extras:
                efilename, ejsonref = pairrsplit(efilename, "#/")
                if not ejsonref:
                    raise ValueError(
                        "{efilename!r} is not json reference. (please <filename>#/<reference>)"
                    )
                eref = "{prefix}#/{ejsonref}".format(
                    prefix=os.path.relpath(efilename, start=cwd), ejsonref=ejsonref
                )
            assign_by_json_pointer(doc, ejsonref, {"$ref": eref})

    resolver = get_resolver(filename, doc=doc, onload=onload, format=format)
    bundler = Bundler(
        resolver, scanner_factory=create_scanner_factory_from_flavor(flavor)
    )
    r = bundler.bundle(resolver.doc)
    return r


def separate(
    src: str, *, dst: str = None, input_format=None, output_format=None
) -> None:
    resolver = get_resolver(src, format=input_format)
    separator = Separator(resolver, format=output_format, here=dst or None)
    separator.separate(name="main", dst=dst)
