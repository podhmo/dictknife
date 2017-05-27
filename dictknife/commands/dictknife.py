# -*- coding:utf-8 -*-
import logging
import sys
try:
    import click
except ImportError as e:
    print(e, file=sys.stderr)
    print("please install via `pip install dictknife[command]`", file=sys.stderr)
    sys.exit(1)
from dictknife import loading
from dictknife.langhelpers import traceback_shortly

logger = logging.getLogger(__name__)
loglevels = list(logging._nameToLevel.keys())


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option("--log", help="logging level", default="INFO", type=click.Choice(loglevels))
@click.pass_context
def main(ctx, log):
    logging.basicConfig(level=getattr(logging, log))
    loading.setup()


@main.command(help="concat dicts")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("-f", "--format", default=None, type=click.Choice(loading.get_formats()))
@click.option("--input-format", default=None, type=click.Choice(loading.get_formats()))
@click.option("--output-format", default=None, type=click.Choice(loading.get_formats()))
@click.option("--debug", is_flag=True)
def concat(files, dst, format, input_format, output_format, debug):
    from collections import OrderedDict
    from .. import deepmerge
    with traceback_shortly(debug):
        d = OrderedDict()
        for f in files:
            logger.debug("merge: %s", f)
            with open(f) as rf:
                sd = loading.load(rf, format=input_format or format)
            if isinstance(sd, (list, tuple)):
                if not isinstance(d, (list, tuple)):
                    d = [d] if d else []
                d.extend(sd)
            else:
                d = deepmerge(d, sd)
        loading.dumpfile(d, dst, format=output_format or format)


@main.command(help="transform dict")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("--config", default="{}")
@click.option("--config-file", default=None, type=click.Path(exists=True))
@click.option("--code", default=None)
@click.option("--function", default="dictknife.transform:identity")
@click.option("--input-format", default=None, type=click.Choice(loading.get_formats()))
@click.option("--output-format", default=None, type=click.Choice(loading.get_formats()))
@click.option("-f", "--format", default=None, type=click.Choice(loading.get_formats()))
@click.option("--debug", is_flag=True)
def transform(
    src, dst, config, config_file, code, function, input_format, output_format, format, debug
):
    from magicalimport import import_symbol
    from .. import deepmerge
    with traceback_shortly(debug):
        if code is not None:
            transform = eval(code)
        else:
            transform = import_symbol(function)

        input_format = input_format or format
        kwargs = loading.loads(config, format=input_format)

        if config_file:
            with open(config_file) as rf:
                kwargs = deepmerge(kwargs, loading.load(rf, format=input_format))

        data = loading.loadfile(src, input_format)
        result = transform(data, **kwargs)
        loading.dumpfile(result, dst, format=output_format or format)


@main.command(help="diff dict")
@click.option("--normalize", is_flag=True, default=False)
@click.argument("left", required=True, type=click.Path(exists=True))
@click.argument("right", required=True, type=click.Path(exists=True))
@click.argument("n", required=False, type=click.INT, default=3)
@click.option("--debug", is_flag=True)
def diff(normalize, left, right, n, debug):
    from dictknife import diff
    with traceback_shortly(debug):
        with open(left) as rf:
            left_data = loading.load(rf)
        with open(right) as rf:
            right_data = loading.load(rf)
        for line in diff(
            left_data, right_data, fromfile=left, tofile=right, n=n, normalize=normalize
        ):
            print(line)


@main.command(help="line cat")
@click.option("--src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("--input-format", default=None, type=click.Choice(loading.get_formats()))
@click.option("--output-format", default=None, type=click.Choice(loading.get_formats()))
@click.option("-f", "--format", default=None, type=click.Choice(loading.get_formats()))
@click.option("--debug", is_flag=True)
def linecat(src, dst, input_format, output_format, format, debug):
    input_format = input_format or format
    output_format = output_format or format

    def consume(itr):
        r = []
        for line in itr:
            r.append(loading.loads(line, format=input_format))
        loading.dumpfile(r, dst, format=output_format)

    with traceback_shortly(debug):
        if src is None:
            consume(iter(sys.stdin))
        else:
            with open(src) as rf:
                consume(iter(rf))
