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
@click.option("--dst", default=None, type=click.Path())
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
def concat(dst, files):
    from collections import OrderedDict
    from . import deepmerge
    d = OrderedDict()
    for f in files:
        logger.debug("merge: %s", f)
        with open(f) as rf:
            d = deepmerge(d, loading.load(rf))
    if dst:
        with open(dst, "w") as wf:
            loading.dump(d, wf)
    else:
        loading.dump(d, sys.stdout)


@command.command(help="transform dict")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("--config", default="{}")
@click.option("--config-file", default=None, type=click.Path(exists=True))
@click.option("--code", default=None)
@click.option("--function", default="dictknife.transform:identity")
def transform(src, dst, config, config_file, code, function):
    import json
    from functools import partial
    from magicalimport import import_symbol
    from . import deepmerge

    if code is not None:
        transform = eval(code)
    else:
        transform = import_symbol(function)

    kwargs = json.loads(config)

    if config_file:
        with open(config_file) as rf:
            kwargs = deepmerge(kwargs, loading.load(rf))

    if src:
        with open(src) as rf:
            data = loading.load(rf)
    else:
        data = loading.load(sys.stdin)

    result = partial(transform, **kwargs)(data)

    if dst:
        with open(dst, "w") as wf:
            loading.dump(result, wf)
    else:
        loading.dump(result, sys.stdout)


@command.command(help="diff dict")
@click.option("--sort-keys", is_flag=True, default=False)
@click.argument("left", required=True, type=click.Path(exists=True))
@click.argument("right", required=True, type=click.Path(exists=True))
def diff(sort_keys, left, right):
    import json
    import difflib
    with open(left) as rf:
        left_output = json.dumps(loading.load(rf), ensure_ascii=False, indent=2, sort_keys=sort_keys)
    with open(right) as rf:
        right_output = json.dumps(loading.load(rf), ensure_ascii=False, indent=2, sort_keys=sort_keys)
    iterator = difflib.unified_diff(
        left_output.splitlines(keepends=True),
        right_output.splitlines(keepends=True),
        fromfile=left,
        tofile=right,
    )
    for line in iterator:
        sys.stdout.write(line)
