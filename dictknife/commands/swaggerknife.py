import os.path
import logging
import warnings
import contextlib
from dictknife import loading
from dictknife.cliutils import traceback_shortly
from magicalimport import import_symbol

logger = logging.getLogger(__name__)


def tojsonschema(*, src, dst, name):
    # todo: id
    d = loading.loadfile(src)
    root = d["definitions"].pop(name)
    root.update(d)
    loading.dumpfile(root, filename=dst)


def json2swagger(
    *,
    files,
    dst: str,
    output_format: str,
    name: str,
    detector,
    emitter,
    annotate,
    emit,
    with_minimap: bool,
    without_example: bool
):
    from prestring import Module
    from dictknife import DictWalker

    if annotate is not None:
        annotate = loading.loadfile(annotate)
    else:
        annotate = {}

    ns = "dictknife.swaggerknife.json2swagger"
    detector = import_symbol(detector, ns=ns)()
    emitter = import_symbol(emitter, ns=ns)(annotate)

    info = None
    for src in files:
        data = loading.loadfile(src)
        info = detector.detect(data, name, info=info)

    if emit == "info":
        loading.dumpfile(info, filename=dst)
    else:
        m = Module(indent="  ")
        m.stmt(name)
        emitter.emit(info, m)
        if with_minimap:
            print("# minimap ###")
            print("# *", end="")
            print("\n# ".join(str(m).split("\n")))

        if without_example:
            for _, d in DictWalker(["example"]).walk(emitter.doc):
                d.pop("example")
        loading.dumpfile(emitter.doc, filename=dst, format=output_format)


def merge(
    *,
    files: list,
    dst: str,
    style: str,  # flavor?, strategy?
    strict: bool = False,
    wrap: str = None,
    wrap_section: str = "definitions"
):
    """merge files"""
    from dictknife.langhelpers import make_dict, as_jsonpointer
    from dictknife import deepmerge

    if style == "ref":
        dstdir = dst and os.path.dirname(dst)

        r = make_dict()
        seen = {}
        for src in files:
            d = loading.loadfile(src)
            for ns, sd in d.items():
                for name in sd:
                    if ns not in r:
                        r[ns] = make_dict()
                        seen[ns] = make_dict()
                    if strict and name in r[ns]:
                        raise RuntimeError(
                            "{name} is already existed, (where={where} and {where2})".format(
                                name=name, where=seen[ns][name], where2=src
                            )
                        )
                    if dst is None:
                        where = ""
                    else:
                        where = os.path.relpath(src, start=dstdir)
                    r[ns][name] = {
                        "$ref": "{where}#/{ns}/{name}".format(
                            where=where, ns=ns, name=as_jsonpointer(name)
                        )
                    }
                    seen[ns][name] = src
    elif style == "whole":
        # TODO: strict support?
        data = [loading.loadfile(src) for src in files]
        r = deepmerge(*data, override=True)
    else:
        raise RuntimeError("invalid style: {}".format(style))

    if wrap is not None:
        wd = make_dict()
        wd["type"] = "object"
        wd["properties"] = make_dict()
        for name in r.get(wrap_section) or {}:
            wd["properties"][name] = {"$ref": "#/{wrap_section}/{name}".format(wrap_section=wrap_section, name=name)}
        r[wrap_section][wrap] = wd
    loading.dumpfile(r, dst)


def flatten(*, src: str, dst: str, input_format: str, output_format: str, format: str):
    """flatten jsonschema sub definitions"""
    from dictknife.swaggerknife.flatten import flatten

    input_format = input_format or format
    data = loading.loadfile(src, format=input_format)
    d = flatten(data)
    loading.dumpfile(d, dst, format=output_format or format)


def main():
    import argparse

    formats = loading.get_formats()

    parser = argparse.ArgumentParser()
    parser.print_usage = parser.print_help  # hack
    parser.add_argument(
        "--log",
        choices=list(logging._nameToLevel.keys()),
        default="INFO",
        dest="log_level",
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--debug", action="store_true")

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    # merge
    fn = merge
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("--strict", action="store_true")
    sparser.add_argument("--style", default="ref", choices=["ref", "whole"])
    sparser.add_argument("--wrap", default=None)
    sparser.add_argument("--wrap-section", default="definitions")
    # tojsonschema

    fn = tojsonschema
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("--name", default="top")

    # json2swagger
    fn = json2swagger
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("-o", "--output-format", default=None, choices=formats)
    sparser.add_argument("--name", default="top")
    sparser.add_argument("--detector", default="Detector")
    sparser.add_argument("--emitter", default="Emitter")
    sparser.add_argument("--annotate", default=None)
    sparser.add_argument("--emit", default="schema", choices=["schema", "info"])
    sparser.add_argument("--with-minimap", action="store_true")
    sparser.add_argument("--without-example", action="store_true")

    # flatten
    fn = flatten
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("src", nargs="?", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("-i", "--input-format", default=None, choices=formats)
    sparser.add_argument("-o", "--output-format", default=None, choices=formats)
    sparser.add_argument("-f", "--format", default=None, choices=formats)

    args = parser.parse_args()

    with contextlib.ExitStack() as s:
        params = vars(args)
        if params.pop("quiet"):
            args.log_level = logging._levelToName[logging.WARNING]
            s.enter_context(warnings.catch_warnings())
            warnings.simplefilter("ignore")
        logging.basicConfig(level=getattr(logging, params.pop("log_level")))
        with traceback_shortly(params.pop("debug")):
            return params.pop("subcommand")(**params)
