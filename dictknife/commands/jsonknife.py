# -*- coding:utf-8 -*-
import logging
from collections import OrderedDict
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
from dictknife import deepmerge
from dictknife.jsonknife import JSONRefAccessor
from dictknife.jsonknife import lifting_jsonschema_definition


logger = logging.getLogger(__name__)


@click.group()
@click.option("--log", help="logging level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))
@click.pass_context
def main(ctx, log):
    logging.basicConfig(level=getattr(logging, log))
    loading.setup()


@main.command(help="extract")
@click.option("--src", default=None, type=click.Path(exists=True), required=True)
@click.option("--dst", default=None, type=click.Path())
@click.option("refs", "--ref", default=None, multiple=True)
@click.option("--with-name", is_flag=True, default=False)
def extract(src, dst, refs, with_name):
    accessor = JSONRefAccessor()
    with open(src) as rf:
        data = loading.load(rf)

    if not refs:
        d = accessor.expand(data, data)
    else:
        d = OrderedDict()
        for ref in refs:
            extracted = accessor.extract(data, ref)
            if with_name:
                d[ref.rsplit("/", 2)[-1]] = extracted
            else:
                d = deepmerge(d, extracted)
    if dst is None:
        loading.dump(d, sys.stdout)
    else:
        with open(dst, "w") as wf:
            loading.dump(d, wf)


@main.command(help="lifting jsonschema sub definition")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
def lift(src, dst):
    if src is None:
        data = loading.load(sys.stdin)
    else:
        with open(src) as rf:
            data = loading.load(rf)

    d = lifting_jsonschema_definition(data)

    if dst is None:
        loading.dump(d, sys.stdout)
    else:
        with open(dst, "w") as wf:
            loading.dump(d, wf)
