# -*- coding:utf-8 -*-
import logging
import sys

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
