# -*- coding:utf-8 -*-
import logging
import sys
try:
    import click
except ImportError as e:
    print(e, file=sys.stderr)
    print("please install via `pip install dictknife[command]`", file=sys.stderr)
    sys.exit(1)
from dictknife import loading
from magicalimport import import_symbol
logger = logging.getLogger(__name__)
loglevels = list(logging._nameToLevel.keys())


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option("--log", help="logging level", default="INFO", type=click.Choice(loglevels))
@click.pass_context
def main(ctx, log):
    logging.basicConfig(level=getattr(logging, log))
    loading.setup()


@main.command(help="tojsonschema")
@click.argument("src", default=None, type=click.Path(exists=True), required=False)
@click.option("--dst", default=None, type=click.Path())
@click.option("--name", default="top")
def tojsonschema(src, dst, name):
    d = loading.loadfile(src)
    root = d["definitions"].pop(name)
    root.update(d)
    loading.dumpfile(root, filename=dst)


@main.command(help="json2swagger")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("--name", default="top")
@click.option("--detector", default="Detector")
@click.option("--emitter", default="Emitter")
@click.option("--annotate", default=None, type=click.Path(exists=True))
@click.option("--emit", default="schema", type=click.Choice(["schema", "info"]))
@click.option("--with-minimap", is_flag=True)
def json2swagger(files, dst, name, detector, emitter, annotate, emit, with_minimap):
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


@main.command(help="flatten jsonschema sub definitions")
@click.argument("src", default=None, type=click.Path(exists=True), required=False)
@click.option("--dst", default=None, type=click.Path())
def flatten(src, dst):
    from dictknife.swaggerknife.flatten import flatten
    data = loading.loadfile(src)
    d = flatten(data)
    loading.dumpfile(d, dst)
