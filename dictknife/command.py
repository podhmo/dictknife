# -*- coding:utf-8 -*-
import logging
import sys
from functools import partial
try:
    import click
except ImportError as e:
    sys.stderr.write(str(e))
    sys.stderr.write("\n")
    sys.stderr.write("please install via `pip install dictknife[command]`")
    sys.stderr.write("\n")
    sys.exit(-1)
from dictknife import loading
logger = logging.getLogger(__name__)


@click.group()
@click.option("--log", help="logging level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))
@click.pass_context
def command(ctx, log):
    logging.basicConfig(level=getattr(logging, log))
    loading.setup()


@command.command(help="concat dicts")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
def concat(files):
    from collections import OrderedDict
    from . import deepmerge
    d = OrderedDict()
    for f in files:
        logger.debug("merge: %s", f)
        with open(f) as rf:
            d = deepmerge(d, loading.load(rf))
    loading.dump(d, sys.stdout)


@command.command(help="transform dict")
@click.option("--name", default="NAME")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path(exists=True))
@click.option("--code", default=None)
@click.option("--function", default="dictknife.transform:identity")
def transform(name, src, dst, code, function):
    from magicalimport import import_symbol

    if code is not None:
        transform = eval(code)
    else:
        transform = import_symbol(function)

    if src:
        with open(src) as rf:
            data = loading.load(rf)
    else:
        data = loading.load(sys.stdin)

    result = partial(transform, name=name)(data)

    if dst:
        with open(dst, "w") as wf:
            loading.dump(result, wf)
    else:
        loading.dump(result, sys.stdout)
