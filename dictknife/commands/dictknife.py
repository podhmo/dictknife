# -*- coding:utf-8 -*-
import logging
import sys
from collections import OrderedDict
from dictknife.commandline import SubCommandParser
from dictknife import loading
from dictknife.langhelpers import traceback_shortly

logger = logging.getLogger(__name__)



def concat(*, files, dst, format, input_format, output_format, debug):
    from dictknife import deepmerge
=======
def concat(*, files, dst, format, input_format, output_format, debug, sort_keys):
    from collections import OrderedDict
    from .. import deepmerge
>>>>>>> 1cd72b1... --sort-keys
    with traceback_shortly(debug):
        d = OrderedDict()
        for f in files:
            logger.debug("merge: %s", f)
            with open(f) as rf:
                sd = loading.load(rf, format=input_format or format)
                if hasattr(sd, "keys"):
                    d = deepmerge(d, sd)
                else:
                    if not isinstance(d, (list, tuple)):
                        d = [d] if d else []
                    d.extend(sd)
        loading.dumpfile(d, dst, format=output_format or format, sort_keys=sort_keys)


def transform(
    *, src, dst, config, config_file, code, function, input_format, output_format, format, debug,
    sort_keys
):
    from magicalimport import import_symbol
    from dictknife import deepmerge
    with traceback_shortly(debug):
        if code is not None:
            transform = eval(code)
        elif function is not None:
            transform = import_symbol(function)
        else:
            transform = lambda x: x  # NOQA

        input_format = input_format or format
        kwargs = loading.loads(config, format=input_format)

        if config_file:
            with open(config_file) as rf:
                kwargs = deepmerge(kwargs, loading.load(rf, format=input_format))

        data = loading.loadfile(src, input_format)
        result = transform(data, **kwargs)
        loading.dumpfile(result, dst, format=output_format or format, sort_keys=sort_keys)


def diff(*, normalize, left, right, n, debug):
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


def linecat(*, src, dst, input_format, output_format, format, debug):
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


def shape(
    *,
    files,
    input_format,
    output_format,
    squash,
    skiplist,
    separator,
    with_type,
    with_example,
    full,
    debug,
):
    from dictknife import shape
    input_format = input_format or format
    with traceback_shortly(debug):
        if not files:
            files = [None]
        dataset = []
        for f in files:
            d = loading.loadfile(f)
            if squash:
                dataset.extend(d)
            else:
                dataset.append(d)
        rows = shape(dataset, squash=True, skiplist=skiplist, separator=separator)

        r = []
        for row in rows:
            d = OrderedDict()
            d["path"] = row.path
            if with_type:
                typenames = [t.__name__ for t in row.type]
                d["type"] = typenames[0] if len(typenames) == 1 else typenames
            if with_example:
                if full:
                    d["example"] = row.example
                elif not any(t in (list, dict) for t in row.type):
                    d["example"] = row.example
                elif output_format in ("csv", "tsv"):
                    d["example"] = ""  # xxx
            r.append(d)

        if output_format is None:
            for d in r:
                print(*d.values())
        else:
            loading.dumpfile(r, None, format=output_format)


def main():
    parser = SubCommandParser()

    parser.add_argument("--log", choices=list(logging._nameToLevel.keys()), default="INFO")
    formats = loading.get_formats()

    with parser.subcommand(concat, description="concat dicts") as add_argument:
        add_argument("files", nargs="*", default=sys.stdin)
        add_argument("--dst", default=None)
        add_argument("-f", "--format", default=None, choices=formats)
        add_argument("-i", "--input-format", default=None, choices=formats)
        add_argument("-o", "--output-format", default=None, choices=formats)
        add_argument("--debug", action="store_true")
        add_argument("--sort-keys", action="store_true")

    with parser.subcommand(transform, description="transform dict") as add_argument:
        add_argument("--src", default=None)
        add_argument("--dst", default=None)
        add_argument("--config", default="{}")
        add_argument("--config-file", default=None)
        add_argument("--code", default=None)
        add_argument("--function", default=None)
        add_argument("-i", "--input-format", default=None, choices=formats)
        add_argument("-o", "--output-format", default=None, choices=formats)
        add_argument("-f", "--format", default=None, choices=formats)
        add_argument("--debug", action="store_true")
        add_argument("--sort-keys", action="store_true")

    with parser.subcommand(diff, description="diff dict") as add_argument:
        add_argument("--normalize", action="store_true")
        add_argument("left")
        add_argument("right")
        add_argument("--n", default=3, type=int)
        add_argument("--debug", action="store_true")

    with parser.subcommand(linecat) as add_argument:
        add_argument("files", nargs="*", default=sys.stdin)
        add_argument("--dst", default=None)
        add_argument("-i", "--input-format", default=None, choices=formats)
        add_argument("-o", "--output-format", default=None, choices=formats)
        add_argument("-f", "--format", default=None, choices=formats)
        add_argument("--debug", action="store_true")

    with parser.subcommand(shape) as add_argument:
        add_argument("files", nargs="*", default=sys.stdin)
        add_argument("--squash", action="store_true")
        add_argument("--skiplist", action="store_true")
        add_argument("--full", action="store_true")
        add_argument("--with-type", action="store_true")
        add_argument("--with-example", action="store_true")
        add_argument("--separator", default="/")
        add_argument("-i", "--input-format", default=None, choices=formats)
        add_argument("-o", "--output-format", default=None, choices=formats)
        add_argument("--debug", action="store_true")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log))
    return args.fn(args)
