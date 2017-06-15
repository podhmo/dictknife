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
logger = logging.getLogger(__name__)
loglevels = list(logging._nameToLevel.keys())


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option("--log", help="logging level", default="INFO", type=click.Choice(loglevels))
@click.pass_context
def main(ctx, log):
    logging.basicConfig(level=getattr(logging, log))
    loading.setup()


@main.command(help="json2swagger")
@click.argument("src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("--name", default="top")
@click.option("--annotations", default=None, type=click.Path(exists=True))
@click.option("--emit", default="schema", type=click.Choice(["schema", "info"]))
def json2swagger(src, dst, name, annotations, emit):
    from prestring import Module
    from dictknife.swaggerknife.json2swagger import Detector, Emitter

    if annotations is not None:
        annotations = loading.loadfile(annotations)
    else:
        annotations = {}

    detector = Detector()
    emitter = Emitter(annotations)

    data = loading.loadfile(src)
    info = detector.detect(data, name)

    if emit == "info":
        loading.dumpfile(info, filename=dst)
    else:
        m = Module(indent="  ")
        m.stmt(name)
        emitter.emit(info, m)
        loading.dumpfile(emitter.doc, filename=dst)
