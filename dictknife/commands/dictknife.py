import logging
import sys
import warnings
import contextlib
import itertools
from dictknife.langhelpers import make_dict
from dictknife.commandline import SubCommandParser
from dictknife import loading
from dictknife.langhelpers import traceback_shortly

logger = logging.getLogger(__name__)


def _open(f, encoding=None, errors=None):
    if f == sys.stdin:
        return contextlib.closing(f)
    else:
        return open(f, encoding=encoding, errors=errors)


def concat(**kwargs):
    warnings.warn("concat() is deprecated, please using `cat` instead of it.")
    return cat(**kwargs)


def cat(
    *,
    files,
    dst,
    format,
    input_format,
    output_format,
    debug,
    sort_keys,
    encoding=None,
    errors=None,
    size=None,
    slurp=False
):
    from dictknife import deepmerge

    input_format = input_format or format
    with traceback_shortly(debug):
        d = make_dict()
        for f in files:
            logger.debug("merge: %s", f)
            with _open(f, encoding=encoding, errors=errors) as rf:
                if slurp:
                    sd = (loading.loads(line, format=input_format) for line in rf)
                else:
                    sd = loading.load(rf, format=input_format, errors=errors)

                if size is not None:
                    sd = itertools.islice(sd, size)

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


def diff(
    *,
    normalize: bool,
    sort_keys: bool,
    left: dict,
    right: dict,
    n: int,
    debug: bool,
    output_format: str = "diff"
):
    from dictknife.diff import diff, diff_rows
    with traceback_shortly(debug):
        with open(left) as rf:
            left_data = loading.load(rf)
        with open(right) as rf:
            right_data = loading.load(rf)

        if output_format == "diff":
            for line in diff(
                left_data,
                right_data,
                fromfile=left,
                tofile=right,
                n=n,
                normalize=normalize,
                sort_keys=sort_keys,
            ):
                print(line)
        else:
            if output_format == "dict":
                output_format = "json"
            rows = diff_rows(
                left_data,
                right_data,
                fromfile=left,
                tofile=right,
                diff_key="diff",
                normalize=normalize
            )
            loading.dumpfile(rows, format=output_format)


def linecat(src=None, **kwargs):
    warnings.warn("concat() is deprecated, please using `cat --slurp` instead of it.")
    if src is not None:
        kwargs["files"] = [src]
    kwargs["slurp"] = True
    return cat(**kwargs)


def shape(
    *, files, input_format, output_format, squash, skiplist, separator, with_type, with_example,
    full, debug
):
    from dictknife import shape
    with traceback_shortly(debug):
        dataset = []
        for f in files:
            with _open(f) as rf:
                d = loading.load(rf, format=input_format)
                if squash:
                    dataset.extend(d)
                else:
                    dataset.append(d)
        rows = shape(dataset, squash=True, skiplist=skiplist, separator=separator)

        r = []
        for row in rows:
            d = make_dict()
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

    parser.add_argument(
        "--log", choices=list(logging._nameToLevel.keys()), default="INFO", dest="log_level"
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    formats = loading.get_formats()

    for cmd in [cat, concat, linecat]:
        with parser.subcommand(cmd, description="concat dicts") as add_argument:
            if cmd == linecat:
                add_argument("--src", nargs="?", default=None)  # xxx: backward compatibility
            add_argument("files", nargs="*", default=[sys.stdin])
            add_argument("--slurp", action="store_true")

            add_argument("--size", type=int, default=None)
            add_argument("--dst", default=None)
            add_argument("-f", "--format", default=None, choices=formats)
            add_argument("-i", "--input-format", default=None, choices=formats)
            add_argument("-o", "--output-format", default=None, choices=formats)
            add_argument("--encoding", default=None)
            add_argument(
                "--errors",
                default=None,
                choices=[
                    "strict", "ignore", "replace", "surrogateescape", "xmlcharrefreplace",
                    "backslashreplace", "namereplace"
                ],
                help="see pydoc codecs.Codec",
            )
            add_argument("--debug", action="store_true")
            add_argument("-S", "--sort-keys", action="store_true")

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
        add_argument("-S", "--sort-keys", action="store_true")

    with parser.subcommand(diff, description="diff dict") as add_argument:
        add_argument("--normalize", action="store_true")
        add_argument("left")
        add_argument("right")
        add_argument("--n", default=3, type=int)
        add_argument("-o", "--output-format", choices=["diff", "dict", "md", "tsv"], default="diff")
        add_argument("--debug", action="store_true")
        add_argument("-S", "--sort-keys", action="store_true")

    with parser.subcommand(shape) as add_argument:
        add_argument("files", nargs="*", default=[sys.stdin])
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

    with contextlib.ExitStack() as s:
        if args.quiet:
            args.log_level = logging._levelToName[logging.WARNING]
            s.enter_context(warnings.catch_warnings())
            warnings.simplefilter("ignore")
        logging.basicConfig(level=getattr(logging, args.log_level))
        return args.fn(args)
