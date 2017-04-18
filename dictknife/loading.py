# -*- coding:utf-8 -*-
import sys
import json
import yaml
import os.path
import logging
from io import StringIO
from collections import OrderedDict, defaultdict, ChainMap
logger = logging.getLogger(__name__)


class Format:
    yaml = "yaml"
    json = "json"
    unknown = "(unknown)"


class IgnoreReferenceDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True


def dispatch_by_format(filename, fn_map, default=Format.unknown):
    _, ext = os.path.splitext(filename)
    if ext in (".yaml", ".yml"):
        return fn_map[Format.yaml]
    elif ext in (".json", ".js"):
        return fn_map[Format.json]
    else:
        return fn_map[default]


def _json_load(fp):
    return json.load(fp, object_pairs_hook=OrderedDict)


def _json_dump(d, fp):
    return json.dump(d, fp, ensure_ascii=False, indent=2, default=str)


def _yaml_dump(d, fp):
    return yaml.dump(d, fp, allow_unicode=True, default_flow_style=False, Dumper=IgnoreReferenceDumper)


default_load_fnmap = {Format.yaml: yaml.load, Format.json: _json_load, Format.unknown: yaml.load}
default_dump_fnmap = {Format.yaml: _yaml_dump, Format.json: _json_dump, Format.unknown: _yaml_dump}


def loads(s, *args, **kwargs):
    return load(StringIO(s), *args, **kwargs)


def load(fp, format=None, fn_map=default_load_fnmap):
    if format is not None:
        loader = fn_map[format]
    else:
        fname = getattr(fp, "name", "(unknown)")
        loader = dispatch_by_format(fname, fn_map, default=loading_config.input_format)
    return loader(fp)


def dumps(d, *args, **kwargs):
    fp = StringIO()
    dump(d, fp, *args, **kwargs)
    return fp.getvalue()


def dump(d, fp, format=None, fn_map=default_dump_fnmap):
    if format is not None:
        dumper = fn_map[format]
    else:
        fname = getattr(fp, "name", "(unknown)")
        dumper = dispatch_by_format(fname, fn_map, default=loading_config.output_format)
    return dumper(d, fp)


def loadfile(filename=None, format=None, fn_map=default_load_fnmap):
    """load file or stdin"""
    if filename is None:
        return load(sys.stdin, format=format, fn_map=fn_map)
    else:
        with open(filename) as rf:
            return load(rf, format=format, fn_map=fn_map)


def dumpfile(d, filename=None, format=None, fn_map=default_dump_fnmap, _retry=False):
    """dump file or stdout"""
    if filename is None:
        return dump(d, sys.stdout, format=format, fn_map=fn_map)
    else:
        try:
            with open(filename, "w") as wf:
                return dump(d, wf, format=format, fn_map=fn_map)
        except FileNotFoundError:
            if _retry:
                raise
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            return dumpfile(d, filename, format=format, fn_map=fn_map, _retry=True)


class loading_config:
    input_format = Format.yaml
    output_format = Format.yaml


def setup(input=None, output=None, dict_classes=[OrderedDict, defaultdict, ChainMap]):
    global loading_config
    if input is not None:
        logger.debug("setup input format: %s", input)
        loading_config.input_format = input
    if output is not None:
        logger.debug("setup output format: %s", output)
        loading_config.output_format = output
    yaml.add_constructor('tag:yaml.org,2002:map', construct_odict)
    for dict_class in dict_classes:
        yaml.add_representer(dict_class, represent_odict)


def represent_odict(dumper, instance):
    return dumper.represent_mapping('tag:yaml.org,2002:map', instance.items())


def construct_odict(loader, node):
    return OrderedDict(loader.construct_pairs(node))
