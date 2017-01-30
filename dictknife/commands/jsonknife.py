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
from dictknife import LooseDictWalkingIterator
from dictknife import Accessor
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


# todo: move
class JSONRefAccessor(object):
    def __init__(self):
        self.accessor = Accessor()
        self.ref_walking = LooseDictWalkingIterator(["$ref"])

    def access(self, fulldata, ref):
        # not support external file
        if not ref.startswith("#/"):
            raise ValueError("invalid ref {!r}".format(ref))
        path = ref[2:].split("/")
        return self.accessor.access(fulldata, path)

    def expand(self, fulldata, d):
        if "$ref" in d:
            original = self.access(fulldata, d["$ref"])
            d.pop("$ref")
            d.update(self.expand(fulldata, original))
            return d
        else:
            for path, sd in self.ref_walking.iterate(d):
                self.expand(fulldata, sd)
            return d

    def extract(self, fulldata, ref):
        return self.expand(fulldata, self.access(fulldata, ref))
