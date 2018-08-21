# -*- coding:utf-8 -*-
import sys
import os.path
import logging
from io import StringIO
from . import json
from . import raw
from . import env
from . import yaml
from . import toml
from . import tsv
from . import csv
from . import md

logger = logging.getLogger(__name__)
unknown = "(unknown)"


class Loader:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.fn_map = {}

    def add_format(self, fmt, fn):
        self.fn_map[fmt] = fn

    def loads(self, s, *args, **kwargs):
        return load(StringIO(s), *args, **kwargs)

    def load(self, fp, format=None, errors=None):
        if format is not None:
            load = self.fn_map[format]
        else:
            fname = getattr(fp, "name", "(unknown)")
            load = self.dispatcher.dispatch(fname, self.fn_map)
        return load(fp, loader=self, errors=errors)

    def loadfile(self, filename=None, format=None, opener=open, encoding=None, errors=None):
        """load file or stdin"""
        if filename is None:
            return self.load(sys.stdin, format=format)
        else:
            with opener(filename, encoding=encoding, errors=errors) as rf:
                r = self.load(rf, format=format, errors=errors)
                if not hasattr(r, "keys") and hasattr(r, "__iter__"):
                    r = list(r)
                return r


class Dumper:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.fn_map = {}

    def add_format(self, fmt, fn):
        self.fn_map[fmt] = fn

    def dumps(self, d, *args, **kwargs):
        fp = StringIO()
        self.dump(d, fp, *args, **kwargs)
        return fp.getvalue()

    def dump(self, d, fp, format=None, sort_keys=False):
        if format is not None:
            dumper = self.fn_map[format]
        else:
            fname = getattr(fp, "name", "(unknown)")
            dumper = self.dispatcher.dispatch(fname, self.fn_map)
        return dumper(d, fp, sort_keys=sort_keys)

    def dumpfile(self, d, filename=None, format=None, sort_keys=False, _retry=False):
        """dump file or stdout"""
        if filename is None:
            return self.dump(d, sys.stdout, format=format, sort_keys=sort_keys)
        else:
            try:
                with open(filename, "w") as wf:
                    return self.dump(d, wf, format=format, sort_keys=sort_keys)
            except FileNotFoundError:
                if _retry:
                    raise
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                return self.dumpfile(d, filename, format=format, sort_keys=sort_keys, _retry=True)


class Dispatcher:
    loader_factory = Loader
    dumper_factory = Dumper

    def __init__(self):
        self.loader = self.loader_factory(self)
        self.dumper = self.dumper_factory(self)
        self.exts_matching = {}

    def dispatch(self, filename, fn_map, default=unknown):
        _, ext = os.path.splitext(filename)
        fmt = self.exts_matching.get(ext) or default
        return fn_map[fmt]

    def add_format(self, fmt, load, dump, exts):
        self.loader.add_format(fmt, load)
        self.dumper.add_format(fmt, dump)
        for ext in exts:
            self.exts_matching[ext] = fmt


dispather = Dispatcher()
dispather.add_format("yaml", yaml.load, yaml.dump, exts=(".yaml", ".yml"))
dispather.add_format("json", json.load, json.dump, exts=(".json", ".js"))
dispather.add_format("toml", toml.load, toml.dump, exts=(".toml", ))
dispather.add_format("csv", csv.load, csv.dump, exts=(".csv", ))
dispather.add_format("tsv", tsv.load, tsv.dump, exts=(".tsv", ))
dispather.add_format("raw", raw.load, raw.dump, exts=[])
dispather.add_format("env", env.load, None, exts=(".env", ".environ"))
dispather.add_format("md", md.load, md.dump, exts=(".md", ".mdtable"))
dispather.add_format(unknown, yaml.load, yaml.dump, exts=[])

# short cuts
load = dispather.loader.load
loads = dispather.loader.loads
loadfile = dispather.loader.loadfile
dump = dispather.dumper.dump
dumps = dispather.dumper.dumps
dumpfile = dispather.dumper.dumpfile


def get_formats(dispather=dispather):
    return [fmt for fmt in dispather.loader.fn_map.keys() if fmt != unknown]


def setup(input=None, output=None, dispather=dispather, unknown=unknown):
    global loading_config
    if input is not None:
        logger.debug("setup input format: %s", input)
        dispather.loader.add_format(unknown, input)
    if output is not None:
        logger.debug("setup output format: %s", output)
        dispather.dumper.add_format(unknown, output)
