# -*- coding:utf-8 -*-
import logging
from collections import OrderedDict
import sys
try:
    import click
except ImportError as e:
    print(e, file=sys.stderr)
    print("please install via `pip install dictknife[command]`", file=sys.stderr)
    sys.exit(1)
from dictknife import loading
from dictknife import deepmerge
from dictknife.accessor import Accessor
from dictknife.jsonknife import Expander
from dictknife.jsonknife import Bundler
from dictknife.jsonknife import SampleValuePlotter
from dictknife.jsonknife.resolver import get_resolver_from_filename
from dictknife.jsonknife.accessor import assign_by_json_pointer, access_by_json_pointer

logger = logging.getLogger(__name__)
loglevels = list(logging._nameToLevel.keys())


@click.group(context_settings={'help_option_names': ['-h', '--help']})
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
@click.option("--unwrap", default=None)
@click.option("--wrap", default=None)
def deref(src, dst, refs, unwrap, wrap):
    resolver = get_resolver_from_filename(src)
    expander = Expander(resolver)
    if unwrap and not refs:
        refs = list(refs)
        refs.append(unwrap)

    if not refs:
        d = expander.expand()
    else:
        d = OrderedDict()
        for ref in refs:
            ref_wrap = wrap
            if "@" in ref:
                ref, ref_wrap = ref.split("@", 1)
            extracted = expander.expand_subpart(expander.access(ref))
            if ref_wrap:
                assign_by_json_pointer(d, ref_wrap, extracted)
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


@main.command(help="output sample value from swagger's spec")
@click.argument("src", type=click.Path(exists=True), default=None, required=False)
@click.option("--ref", default=None)
@click.option("-f", "--format", type=click.Choice(loading.get_formats()), default="json")
def examples(src, ref, format):
    data = loading.loadfile(src)
    if ref is not None:
        data = access_by_json_pointer(data, ref)
    plotter = SampleValuePlotter()
    d = plotter.plot(data)
    loading.dumpfile(d, format=format)
