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
from . import spreadsheet  # optional

logger = logging.getLogger(__name__)
unknown = "(unknown)"


class Loader:
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.fn_map = {}
        self.opener_map = {}

    def add_format(self, fmt, fn, *, opener=None):
        self.fn_map[fmt] = fn
        if opener is not None:
            self.opener_map[fmt] = opener

    def loads(self, s, *args, **kwargs):
        return load(StringIO(s), *args, **kwargs)

    def load(self, fp, format=None, errors=None):
        if format is not None:
            load = self.fn_map[format]
        else:
            fname = getattr(fp, "name", "(unknown)")
            load = self.dispatcher.dispatch(fname, self.fn_map)
        return load(fp, loader=self, errors=errors)

    def loadfile(self, filename=None, format=None, opener=None, encoding=None, errors=None):
        """load file or stdin"""
        if filename is None:
            return self.load(sys.stdin, format=format)
        else:
            opener = opener or self.opener_map.get(format) or open
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

    def dumps(self, d, *, format=None, sort_keys=False, extra=None, **kwargs):
        fp = StringIO()
        self.dump(d, fp, format=format, sort_keys=sort_keys, extra=extra, **kwargs)
        return fp.getvalue()

    def dump(self, d, fp, *, format=None, sort_keys=False, extra=None):
        if format is not None:
            dumper = self.fn_map[format]
        else:
            fname = getattr(fp, "name", "(unknown)")
            dumper = self.dispatcher.dispatch(fname, self.fn_map)
        extra = extra or {}
        return dumper(d, fp, sort_keys=sort_keys, **extra)

    def dumpfile(self, d, filename=None, *, format=None, sort_keys=False, extra=None, _retry=False):
        """dump file or stdout"""
        if hasattr(d, "__next__"):  # iterator
            d = list(d)

        if filename is None:
            return self.dump(d, sys.stdout, format=format, sort_keys=sort_keys, extra=extra)
        else:
            try:
                with open(filename, "w") as wf:
                    return self.dump(d, wf, format=format, sort_keys=sort_keys, extra=extra)
            except FileNotFoundError:
                if _retry:
                    raise
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                return self.dumpfile(
                    d, filename, format=format, sort_keys=sort_keys, extra=extra, _retry=True
                )


class Dispatcher:
    loader_factory = Loader
    dumper_factory = Dumper

    def __init__(self):
        self.loader = self.loader_factory(self)
        self.dumper = self.dumper_factory(self)
        self.exts_matching = {}

    def guess_format(self, filename, *, default=unknown):
        _, ext = os.path.splitext(filename)
        return self.exts_matching.get(ext) or default

    def dispatch(self, filename, fn_map, default=unknown):
        fmt = self.guess_format(filename, default=default)
        return fn_map[fmt]

    def add_format(self, fmt, load, dump, *, exts=[], opener=None):
        self.loader.add_format(fmt, load, opener=opener)
        self.dumper.add_format(fmt, dump)
        for ext in exts:
            self.exts_matching[ext] = fmt


dispatcher = Dispatcher()
dispatcher.add_format("yaml", yaml.load, yaml.dump, exts=(".yaml", ".yml"))
dispatcher.add_format("json", json.load, json.dump, exts=(".json", ".js"))
dispatcher.add_format("toml", toml.load, toml.dump, exts=(".toml", ))
dispatcher.add_format("csv", csv.load, csv.dump, exts=(".csv", ))
dispatcher.add_format("tsv", tsv.load, tsv.dump, exts=(".tsv", ))
dispatcher.add_format("raw", raw.load, raw.dump, exts=[])
dispatcher.add_format("env", env.load, None, exts=(".env", ".environ"))
dispatcher.add_format("md", md.load, md.dump, exts=(".md", ".mdtable"))
dispatcher.add_format("markdown", md.load, md.dump, exts=[])
dispatcher.add_format("spreadsheet", spreadsheet.load, None, exts=[], opener=spreadsheet.not_open)
dispatcher.add_format(unknown, yaml.load, yaml.dump, exts=[])

# short cuts
load = dispatcher.loader.load
loads = dispatcher.loader.loads
loadfile = dispatcher.loader.loadfile
dump = dispatcher.dumper.dump
dumps = dispatcher.dumper.dumps
dumpfile = dispatcher.dumper.dumpfile


def get_opener(*, format=None, filename=None, default=open, dispatcher=dispatcher):
    if format is None and filename is not None:
        if hasattr(filename, "name"):
            filename = filename.name  # IO
        format = dispatcher.guess_format(filename)

    opener = dispatcher.loader.opener_map.get(format)
    if opener is None:
        return default
    return opener


def get_formats(dispatcher=dispatcher):
    return [fmt for fmt in dispatcher.loader.fn_map.keys() if fmt != unknown]


def setup(input=None, output=None, dispatcher=dispatcher, unknown=unknown):
    global loading_config
    if input is not None:
        logger.debug("setup input format: %s", input)
        dispatcher.loader.add_format(unknown, input)
    if output is not None:
        logger.debug("setup output format: %s", output)
        dispatcher.dumper.add_format(unknown, output)
