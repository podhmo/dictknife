# -*- coding:utf-8 -*-
import logging
from dictknife import loading
from dictknife.commandline import SubCommandParser
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


def flatten(*, src, dst, position):
    from dictknife.swaggerknife.flatten import flatten
    from dictknife.swaggerknife.inspection import get_inspector
    d = loading.loadfile(src)
    inspector = get_inspector(d)
    d = flatten(d, position=inspector.inspect_default_position())
    loading.dumpfile(d, dst)


def bundle(*, src, dst, flatten=False):
    from dictknife.swaggerknife.inspection import get_inspector
    from dictknife.jsonknife import get_resolver_from_filename
    from dictknife.jsonknife.bundler import Bundler, fix_on_conflict

    resolver = get_resolver_from_filename(src)
    inspector = get_inspector(resolver.doc)
    bundler = Bundler(resolver)
    d = bundler.bundle_doc(
        resolver.doc,
        fix_ref=inspector.repository.localref_fixer,
        fix_conflict=fix_on_conflict,
    )
    # flatten
    if flatten:
        from dictknife.swaggerknife.flatten import flatten
        d = flatten(d, position=inspector.inspect_default_position())
    loading.dumpfile(d, dst)


def main():
    parser = SubCommandParser()

    parser.add_argument("--log", choices=list(logging._nameToLevel.keys()), default="INFO")

    with parser.subcommand(tojsonschema) as add_argument:
        add_argument("--src", default=None)
        add_argument("--dst", default=None)
        add_argument("--name", default="top")

    with parser.subcommand(json2swagger) as add_argument:
        add_argument("files", nargs="*", default=None)
        add_argument("--dst", default=None)
        add_argument("--name", default="top")
        add_argument("--detector", default="Detector")
        add_argument("--emitter", default="Emitter")
        add_argument("--annotate", default=None)
        add_argument("--emit", default="schema", choices=["schema", "info"])
        add_argument("--with-minimap", action="store_true")

    with parser.subcommand(
        flatten, description="flatten jsonschema sub definitions"
    ) as add_argument:
        add_argument("src", nargs="?", default=None)
        add_argument("--position", default="#/definitions")
        add_argument("--dst", default=None)

    with parser.subcommand(bundle) as add_argument:
        add_argument("--src", default=None)
        add_argument("--dst", default=None)
        add_argument("--flatten", action="store_true")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log))
    return args.fn(args)
