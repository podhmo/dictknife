import logging
import warnings
import contextlib
from dictknife import loading
from dictknife.cliutils import traceback_shortly
from magicalimport import import_symbol
logger = logging.getLogger(__name__)


def tojsonschema(*, src, dst, name):
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
