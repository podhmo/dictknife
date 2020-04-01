import logging
import sys
import warnings
import contextlib
import itertools
from dictknife.langhelpers import make_dict
from dictknife import loading
from dictknife.cliutils import traceback_shortly
from dictknife.commands._monkeypatch import (
    apply_loading_format_extra_arguments_parser,
    apply_rest_arguments_as_extra_arguments_parser,
)

logger = logging.getLogger(__name__)


def _open(f, encoding=None, errors=None):
    if f == sys.stdin:
        return contextlib.closing(f)
    else:
        return open(f, encoding=encoding, errors=errors)


def concat(**kwargs):
    """concat dicts"""
    warnings.warn("concat() is deprecated, please using `cat` instead of it.")
    return cat(**kwargs)


def cat(
    *,
    files,
    dst,
    format,
    input_format,
    output_format,
    sort_keys,
    encoding=None,
    errors=None,
    size=None,
    slurp=False,
    extra=None,
    merge_method="addtoset"
):
    from dictknife import deepmerge

    input_format = input_format or format
    d = make_dict()
    with contextlib.ExitStack() as s:
        for f in files:
            logger.debug("merge: %s", f)
            opener = loading.get_opener(filename=f, format=input_format, default=_open)
            rf = s.enter_context(opener(f, encoding=encoding, errors=errors))
            if slurp:
                sd = (loading.loads(line, format=input_format) for line in rf)
            else:
                sd = loading.load(rf, format=input_format, errors=errors)
            if size is not None:
                sd = itertools.islice(sd, size)

            if hasattr(sd, "keys"):
                d = deepmerge(d, sd, method=merge_method)
            elif len(files) == 1:
                d = sd
            else:
                if not isinstance(d, (list, tuple)):
                    d = [d] if d else []
                d = deepmerge(d, sd, method=merge_method)

        loading.dumpfile(
            d, dst, format=output_format or format, sort_keys=sort_keys, extra=extra
        )


def transform(
    *,
    src: str,
    dst: str,
    config: str,
    config_file: str,
    code: str,
    functions: str,
    input_format: str,
    output_format: str,
    format: str,
    sort_keys: str
):
    """transform dict"""
    from magicalimport import import_symbol
    from dictknife import deepmerge

    if code is not None:
        transform = eval(code)
    elif functions:

        def transform(d):
            for fn in functions:
                if "." not in fn:
                    fn = "dictknife.transform:{}".format(fn)
                d = import_symbol(fn)(d)
            return d

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
    skip_empty: bool,
    left: dict,
    right: dict,
    n: int,
    input_format: str,
    output_format: str = "diff",
    verbose: bool = False
):
    """diff dict"""
    from dictknife.diff import diff, diff_rows, make_jsonpatch

    with open(left) as rf:
        left_data = loading.load(rf, format=input_format)
        with open(right) as rf:
            right_data = loading.load(rf, format=input_format)

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
            elif output_format == "jsonpatch":
                r = make_jsonpatch(left_data, right_data, verbose=verbose)
                loading.dumpfile(list(r), format="json")
            else:
                if output_format == "dict":
                    output_format = "json"
                diff_key = "diff"
                rows = diff_rows(
                    left_data,
                    right_data,
                    fromfile=left,
                    tofile=right,
                    diff_key=diff_key,
                    normalize=normalize,
                )
                if skip_empty:
                    rows = [row for row in rows if row[diff_key] not in ("", 0)]
                loading.dumpfile(rows, format=output_format)


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
    full
):
    """shape"""
    from dictknife import shape

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
        loading.dumpfile(r, format=output_format)


def shrink(
    *,
    files: list,
    input_format: str,
    output_format: str,
    max_length_of_string: int,
    cont_suffix: str,
    max_length_of_list: int,
    with_tail: bool
):
    """shrink"""
    from dictknife.transform import shrink

    for f in files:
        with _open(f) as rf:
            d = loading.load(rf, format=input_format)
            format = output_format or input_format or loading.guess_format(f)
            r = shrink(
                d,
                max_length_of_list=max_length_of_list,
                max_length_of_string=max_length_of_string,
                cont_suffix=cont_suffix,
                with_tail=with_tail,
            )
            loading.dumpfile(r, format=format)


def mkdict(
    *,
    output_format: str,
    separator: str,
    delimiter: str,
    sort_keys: bool,
    squash: bool,
    extra
):
    from dictknife.mkdict import mkdict

    if not extra:
        r = []
        variables = {}
        for code in sys.stdin:
            d = mkdict(code, separator=separator, shared=variables)
            if not d:
                continue
            if isinstance(d, list):
                r.extend(d)
            else:
                r.append(d)
        if len(r) == 1:
            r = r[0]
    else:
        args = []
        for x in extra:
            if "=" not in x:
                args.append(repr(x))
            else:
                for e in x.split("=", 1):
                    args.append(repr(e))
        r = mkdict(" ".join(args), separator=separator)

    if squash:
        for row in r:
            loading.dumpfile(row, format=output_format, sort_keys=sort_keys)
            sys.stdout.write("\n")
    else:
        loading.dumpfile(r, format=output_format, sort_keys=sort_keys)
        sys.stdout.write("\n")


def main():
    import argparse

    formats = loading.get_formats()

    parser = argparse.ArgumentParser(
        formatter_class=type(
            "_HelpFormatter",
            (argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter),
            {},
        )
    )
    parser.print_usage = parser.print_help  # hack
    parser.add_argument(
        "--log",
        choices=list(logging._nameToLevel.keys()),
        default="INFO",
        dest="log_level",
        help="-",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="-")
    parser.add_argument("--debug", action="store_true", help="-")

    # modification
    parser.add_argument(
        "--compact", action="store_true", dest="modification_compact", help="-"
    )
    parser.add_argument(
        "--flatten", action="store_true", dest="modification_flatten", help="-"
    )
    parser.add_argument(
        "--unescape",
        default=None,
        dest="modification_unescape",
        choices=["unicode", "url"],
        help="-",
    )

    subparsers = parser.add_subparsers(dest="subcommand", title="subcommands")
    subparsers.required = True

    # cat
    fn = cat
    sparser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    apply_loading_format_extra_arguments_parser(sparser)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=[sys.stdin], help="-")
    sparser.add_argument("--slurp", action="store_true", help="-")

    sparser.add_argument("--size", type=int, default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "--encoding", help="input encoding. (e.g. utf-8, cp932, ...)", default=None,
    )
    sparser.add_argument(
        "--errors",
        default=None,
        choices=[
            "strict",
            "ignore",
            "replace",
            "surrogateescape",
            "xmlcharrefreplace",
            "backslashreplace",
            "namereplace",
        ],
        help="see pydoc codecs.Codec",
    )
    sparser.add_argument("-S", "--sort-keys", action="store_true", help="-")
    sparser.add_argument(
        "--merge-method",
        choices=["addtoset", "append", "merge", "replace"],
        default="addtoset",
        help="-",
    )

    # concat (deprecated)
    fn = concat
    sparser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    apply_loading_format_extra_arguments_parser(sparser)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=[sys.stdin], help="-")
    sparser.add_argument("--slurp", action="store_true", help="-")

    sparser.add_argument("--size", type=int, default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "--encoding", help="input encoding. (e.g. utf-8, cp932, ...)", default=None,
    )
    sparser.add_argument(
        "--errors",
        default=None,
        choices=[
            "strict",
            "ignore",
            "replace",
            "surrogateescape",
            "xmlcharrefreplace",
            "backslashreplace",
            "namereplace",
        ],
        help="see pydoc codecs.Codec",
    )
    sparser.add_argument("-S", "--sort-keys", action="store_true", help="-")
    sparser.add_argument(
        "--merge-method",
        choices=["addtoset", "append", "merge", "replace"],
        default="addtoset",
        help="-",
    )

    # transform
    fn = transform
    sparser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )

    def print_help(*, file=None, self=sparser):
        if file is None:
            file = sys.stdout
        # overwrite help
        for ac in self._actions:
            if ac.dest == "functions":
                import dictknife.transform as m

                callables = [
                    k
                    for k, v in m.__dict__.items()
                    if not k.startswith("_") and callable(v)
                ]
                ac.help = "(e.g. {}, ... or <module>:<fn name> (e.g. dictknife.transform:flatten))".format(
                    ", ".join(sorted(callables))
                )
        self._print_message(self.format_help(), file)

    sparser.print_help = print_help
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("--config", default="{}", help="-")
    sparser.add_argument("--config-file", default=None, help="-")
    sparser.add_argument("--code", default=None, help="-")
    sparser.add_argument(
        "--fn", "--function", default=[], action="append", dest="functions", help="-"
    )
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")
    sparser.add_argument("-S", "--sort-keys", action="store_true", help="-")

    # diff
    fn = diff
    sparser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--normalize", action="store_true", help="-")
    sparser.add_argument("--verbose", action="store_true", help="-")
    sparser.add_argument("left", help="-")
    sparser.add_argument("right", help="-")
    sparser.add_argument("--n", default=3, type=int, help="-")
    sparser.add_argument("--skip-empty", action="store_true", help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o",
        "--output-format",
        choices=["diff", "dict", "md", "tsv", "jsonpatch"],
        default="diff",
        help="-",
    )
    sparser.add_argument("-S", "--sort-keys", action="store_true", help="-")

    # shape
    fn = shape
    sparser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=[sys.stdin], help="-")
    sparser.add_argument("--squash", action="store_true", help="-")
    sparser.add_argument("--skiplist", action="store_true", help="-")
    sparser.add_argument("--full", action="store_true", help="-")
    sparser.add_argument("--with-type", action="store_true", help="-")
    sparser.add_argument("--with-example", action="store_true", help="-")
    sparser.add_argument("--separator", default="/", help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )

    # shrink
    fn = shrink
    sparser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=[sys.stdin], help="-")
    sparser.add_argument("--max-length-of-string", type=int, default=100, help="-")
    sparser.add_argument("--max-length-of-list", type=int, default=3, help="-")
    sparser.add_argument("--cont-suffix", default="...", help="-")
    sparser.add_argument("--with-tail", action="store_true", help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )

    # mkdict
    fn = mkdict
    sparser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    apply_rest_arguments_as_extra_arguments_parser(sparser)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--squash", action="store_true", help="-")
    sparser.add_argument(
        "-o", "--output-format", default="json", choices=formats, help="-"
    )
    sparser.add_argument("--separator", default="/", help="-")
    sparser.add_argument("--delimiter", default=";", help="-")
    sparser.add_argument("-S", "--sort-keys", action="store_true", help="-")

    args = parser.parse_args()
    params = vars(args)

    with contextlib.ExitStack() as s:
        if params.pop("quiet"):
            args.log_level = logging._levelToName[logging.WARNING]
            s.enter_context(warnings.catch_warnings())
            warnings.simplefilter("ignore")

        logging.basicConfig(level=getattr(logging, params.pop("log_level")))

        with traceback_shortly(params.pop("debug")):
            # apply modification
            for k in list(params.keys()):
                if k.startswith("modification_"):
                    v = params.pop(k)
                    if v:
                        from importlib import import_module

                        if isinstance(v, str):
                            module_path = "dictknife.loading.{}_{}".format(
                                k.replace("_", "."), v
                            )
                        else:
                            module_path = "dictknife.loading.{}".format(
                                k.replace("_", ".")
                            )
                        logger.info("apply %s.setup()", module_path)

                        m = import_module(module_path)
                        if not hasattr(m, "setup"):
                            raise RuntimeError(
                                "{}:setup() is not found".format(module_path)
                            )
                        m.setup(loading.dispatcher)
            return params.pop("subcommand")(**params)
