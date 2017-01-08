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
