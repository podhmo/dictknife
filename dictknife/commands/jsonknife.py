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
from dictknife.accessor import Accessor
from dictknife.jsonknife import Expander
from dictknife.jsonknife import Bundler
from dictknife.jsonknife import lifting_jsonschema_definition
from dictknife.jsonknife.resolver import get_resolver_from_filename
from dictknife.jsonknife import SampleValuePlotter


logger = logging.getLogger(__name__)
loglevels = list(logging._nameToLevel.keys())


@click.group()
@click.option("--log", help="logging level", default="INFO", type=click.Choice(loglevels))
@click.pass_context
def main(ctx, log):
    logging.basicConfig(level=getattr(logging, log))
    loading.setup()


@main.command(help="cut")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("refs", "--ref", default=None, multiple=True)
def cut(src, dst, refs):
    d = loading.loadfile(src)
    accessor = Accessor(OrderedDict)
    for ref in refs:
        if ref.startswith("#/"):
            ref = ref[2:]
        accessor.maybe_remove(d, ref.split("/"))
    loading.dumpfile(d, dst)


@main.command(help="deref")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("refs", "--ref", default=None, multiple=True)
@click.option("--with-name", is_flag=True, default=False)
def deref(src, dst, refs, with_name):
    return _deref(src, dst, refs, with_name)


@main.command(help="extract(deprecated, this is same as deref)")
@click.option("--src", default=None, type=click.Path(exists=True), required=True)
@click.option("--dst", default=None, type=click.Path())
@click.option("refs", "--ref", default=None, multiple=True)
@click.option("--with-name", is_flag=True, default=False)
def extract(src, dst, refs, with_name):
    # deprecated
    return _deref(src, dst, refs, with_name)


def _deref(src, dst, refs, with_name):
    resolver = get_resolver_from_filename(src)
    expander = Expander(resolver)
    if not refs:
        d = expander.expand()
    else:
        d = OrderedDict()
        for ref in refs:
            extracted = expander.expand_subpart(expander.access(ref))
            if with_name:
                d[ref.rsplit("/", 2)[-1]] = extracted
            else:
                d = deepmerge(d, extracted)
    loading.dumpfile(d, dst)


@main.command(help="bundle")
@click.option("--src", default=None, type=click.Path(exists=True), required=True)
@click.option("--dst", default=None, type=click.Path())
def bundle(src, dst):
    resolver = get_resolver_from_filename(src)
    bundler = Bundler(resolver)
    d = bundler.bundle()
    loading.dumpfile(d, dst)


@main.command(help="flatten jsonschema sub definitions")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
def flatten(src, dst):
    data = loading.loadfile(src)
    d = lifting_jsonschema_definition(data)
    loading.dumpfile(d, dst)


@main.command(help="flatten jsonschema sub definitions(deprecated)")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
def lift(src, dst):
    return flatten(src, dst)


@main.command(help="output sample value from swagger's spec")
@click.argument("src", type=click.Path(exists=True))
def samplevalue(src):
    data = loading.loadfile(src)
    plotter = SampleValuePlotter()
    d = plotter.plot(data)
    loading.dumpfile(d, format="json")
