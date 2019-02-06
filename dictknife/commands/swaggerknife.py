import os
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


def json2swagger(*, files, dst, name, detector, emitter, annotate, emit, with_minimap):
    from prestring import Module

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
        loading.dumpfile(emitter.doc, filename=dst)


def merge(
    files: list,
    dst: str,
    style: str,  # flavor?, strategy?
    strict: bool = False,
):
    """merge files"""
    from dictknife.langhelpers import make_dict, as_jsonpointer
    from dictknife import deepmerge
    from dictknife.jsonknife.relpath import fixpath
    if style == "ref":
        cwd = os.getcwd()
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
                                name=name,
                                where=seen[ns][name],
                                where2=src,
                            )
                        )
                    if dst is None:
                        where = ""
                    else:
                        where = fixpath(src, where=cwd, to=dstdir)
                    r[ns][name] = {
                        "$ref":
                        "{where}#/{ns}/{name}".format(where=where, ns=ns, name=as_jsonpointer(name))
                    }
                    seen[ns][name] = src
    elif style == "whole":
        # TODO: strict support?
        data = [loading.loadfile(src) for src in files]
        r = deepmerge(*data, override=True)
    else:
        raise RuntimeError("invalid style: {}".format(style))
    loading.dumpfile(r, dst)


def flatten(src, dst):
    """flatten jsonschema sub definitions"""
    from dictknife.swaggerknife.flatten import flatten
    data = loading.loadfile(src)
    d = flatten(data)
    loading.dumpfile(d, dst)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.print_usage = parser.print_help  # hack
    parser.add_argument(
        "--log", choices=list(logging._nameToLevel.keys()), default="INFO", dest="log_level"
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
    # tojsonschema

    fn = tojsonschema
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None)
    sparser.add_argument("--dst", default=None)

    # json2swagger
    fn = json2swagger
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("--name", default="top")
    sparser.add_argument("--detector", default="Detector")
    sparser.add_argument("--emitter", default="Emitter")
    sparser.add_argument("--annotate", default=None)
    sparser.add_argument("--emit", default="schema", choices=["schema", "info"])
    sparser.add_argument("--with-minimap", action="store_true")

    # flatten
    fn = flatten
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("src", nargs="?", default=None)
    sparser.add_argument("--dst", default=None)

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
