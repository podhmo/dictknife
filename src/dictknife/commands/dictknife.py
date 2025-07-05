import logging
import sys
import io
import warnings
import contextlib
import itertools
from dictknife.langhelpers import make_dict
from dictknife.commands._cliutils import traceback_shortly
from dictknife import loading
from dictknife.commands._monkeypatch import (
    apply_loading_format_extra_arguments_parser,
    apply_rest_arguments_as_extra_arguments_parser,
)
from typing import Optional, Any, List, Dict

logger = logging.getLogger(__name__)


def _open(f, encoding=None, errors=None):
    if f == sys.stdin:
        return contextlib.closing(f)
    else:
        return open(f, encoding=encoding, errors=errors)


def cat(
    *,
    files: List[Any],
    dst: Optional[str],
    format: Optional[str],
    input_format: Optional[str],
    output_format: Optional[str],
    sort_keys: bool,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    size: Optional[int] = None,
    slurp: bool = False,
    extra: Optional[Dict[str, Any]] = None,
    merge_method: str = "addtoset",
) -> None:
    from dictknife import deepmerge

    actual_input_format = input_format or format
    d: Any = make_dict()
    with contextlib.ExitStack() as s:
        for f in files:
            logger.debug("merge: %s", f)
            opener = loading.get_opener(
                filename=f, format=actual_input_format, default=_open
            )
            rf = s.enter_context(opener(f, encoding=encoding, errors=errors))
            sd: Any
            if slurp:
                sd = (loading.loads(line, format=actual_input_format) for line in rf)
            else:
                sd = loading.load(rf, format=actual_input_format, errors=errors)
            if size is not None:
                sd = itertools.islice(sd, size)

            if len(files) == 1:
                d = sd
            elif hasattr(sd, "keys"):
                d = deepmerge(d, sd, method=merge_method)
            else:
                if not isinstance(d, (list, tuple)):
                    d = [d] if d else []
                d = deepmerge(
                    d,
                    (
                        list(sd)
                        if hasattr(sd, "__iter__")
                        and not isinstance(sd, (list, tuple, dict))
                        else sd
                    ),
                    method=merge_method,
                )

        loading.dumpfile(
            d, dst, format=(output_format or format), sort_keys=sort_keys, extra=extra
        )


def transform(
    *,
    src: Optional[str],
    dst: Optional[str],
    code: Optional[str],
    functions: List[str],
    input_format: Optional[str],
    output_format: Optional[str],
    format: Optional[str],
    sort_keys: bool,
) -> None:
    """transform dict"""
    from magicalimport import import_symbol

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
    data = loading.loadfile(src, input_format)
    result = transform(data)
    loading.dumpfile(
        result, dst, format=output_format or input_format or format, sort_keys=sort_keys
    )


def diff(
    *,
    normalize: bool,
    sort_keys: bool,
    skip_empty: bool,
    left: str,
    right: str,
    n: int,
    input_format: Optional[str],
    output_format: Optional[str] = "diff",
    verbose: bool = False,
) -> None:
    """diff dict"""
    from dictknife.diff import diff as diff_module, diff_rows, make_jsonpatch

    with open(left) as rf_left:
        left_data = loading.load(rf_left, format=input_format)
        with open(right) as rf_right:
            right_data = loading.load(rf_right, format=input_format)

            if output_format == "diff":
                for line in diff_module(
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
                loading.dumpfile(list(r), filename=None, format="json")
            elif output_format == "pair":
                # iterator?
                if hasattr(left_data, "__next__"):
                    left_data = list(left_data)
                if hasattr(right_data, "__next__"):
                    right_data = list(right_data)
                o = io.StringIO()
                loading.dump(left_data, o, format="json", sort_keys=sort_keys)
                o.seek(0)
                pad_size = len(max(o, key=len)) + 1
                o.seek(0)
                o2 = io.StringIO()
                loading.dump(right_data, o2, format="json", sort_keys=sort_keys)
                o2.seek(0)
                for left_line, right_line in itertools.zip_longest(o, o2):
                    print(left_line.rstrip().ljust(pad_size), end="")
                    print(right_line, end="")
                print("")
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
    files: List[Any],
    input_format: Optional[str],
    output_format: Optional[str],
    squash: bool,
    skiplist: bool,
    separator: str,
    with_type: bool,
    with_example: bool,
    full: bool,
) -> None:
    """shape"""
    from dictknife import shape as shape_module

    dataset: List[Any] = []
    for f in files:
        with _open(f) as rf:
            loaded_data = loading.load(rf, format=input_format)
            if squash:
                dataset.extend(loaded_data)
            else:
                dataset.append(loaded_data)
    rows: List[Any] = shape_module(
        dataset, squash=True, skiplist=skiplist, separator=separator
    )

    r: List[Dict[str, Any]] = []
    for row in rows:
        d: Dict[str, Any] = make_dict()
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
        for item_d in r:
            print(*item_d.values())
    else:
        loading.dumpfile(r, filename=None, format=output_format)


def shrink(
    *,
    files: List[Any],
    input_format: Optional[str],
    output_format: Optional[str],
    max_length_of_string: int,
    cont_suffix: str,
    max_length_of_list: int,
    with_tail: bool,
) -> None:
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
    extra: List[str],
) -> None:
    from dictknife.mkdict import mkdict as mkdict_module

    r: Any
    if not extra:
        r_list: List[Any] = []
        variables: Dict[str, Any] = {}
        for code_line in sys.stdin:
            d: Any = mkdict_module(
                code_line.strip(), separator=separator, shared=variables
            )
            if not d:
                continue
            if isinstance(d, list):
                r_list.extend(d)
            else:
                r_list.append(d)
        if len(r_list) == 1:
            r = r_list[0]
        else:
            r = r_list
    else:
        args: List[str] = []
        for x_item in extra:
            if "=" not in x_item:
                args.append(repr(x_item))
            else:
                for e_item in x_item.split("=", 1):
                    args.append(repr(e_item))
        r = mkdict_module(" ".join(args), separator=separator)

    if squash and isinstance(r, list):
        for row_item in r:
            loading.dumpfile(
                row_item, filename=None, format=output_format, sort_keys=sort_keys
            )
            sys.stdout.write("\n")
    else:
        loading.dumpfile(r, filename=None, format=output_format, sort_keys=sort_keys)
        sys.stdout.write("\n")


def main():
    import argparse

    class HelpFormatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
    ):
        pass

    formats = loading.get_formats()

    parser = argparse.ArgumentParser(formatter_class=HelpFormatter)
    # parser.print_usage = parser.print_help  # hack # mypy: error: Cannot assign to a method
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
    def run_cat(args: argparse.Namespace) -> None:
        cat(
            files=args.files,
            dst=args.dst,
            format=args.format,
            input_format=args.input_format,
            output_format=args.output_format,
            sort_keys=args.sort_keys,
            encoding=args.encoding,
            errors=args.errors,
            size=args.size,
            slurp=args.slurp,
            extra=getattr(
                args, "extra", None
            ),  # apply_loading_format_extra_arguments_parserで追加される想定
            merge_method=args.merge_method,
        )

    fn = run_cat
    sparser = subparsers.add_parser(
        cat.__name__, help=cat.__doc__, formatter_class=parser.formatter_class
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
        "--encoding",
        help="input encoding. (e.g. utf-8, cp932, ...)",
        default=None,
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
    def run_transform(args: argparse.Namespace) -> None:
        transform(
            src=args.src,
            dst=args.dst,
            code=args.code,
            functions=args.functions,
            input_format=args.input_format,
            output_format=args.output_format,
            format=args.format,
            sort_keys=args.sort_keys,
        )

    fn = run_transform
    sparser = subparsers.add_parser(
        transform.__name__,
        help=transform.__doc__,
        formatter_class=parser.formatter_class,
    )

    def print_help(*, file=None, self=sparser) -> None:
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

    # sparser.print_help = print_help # mypy: error: Cannot assign to a method
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("src", nargs="?", help="-")
    sparser.add_argument("--dst", default=None, help="-")
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
    def run_diff(args: argparse.Namespace) -> None:
        diff(
            normalize=args.normalize,
            sort_keys=args.sort_keys,
            skip_empty=args.skip_empty,
            left=args.left,
            right=args.right,
            n=args.n,
            input_format=args.input_format,
            output_format=args.output_format,
            verbose=args.verbose,
        )

    fn = run_diff
    sparser = subparsers.add_parser(
        diff.__name__, help=diff.__doc__, formatter_class=parser.formatter_class
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
        choices=["diff", "dict", "md", "tsv", "jsonpatch", "pair"],
        default="diff",
        help="-",
    )
    sparser.add_argument("-S", "--sort-keys", action="store_true", help="-")

    # shape
    def run_shape(args: argparse.Namespace) -> None:
        shape(
            files=args.files,
            input_format=args.input_format,
            output_format=args.output_format,
            squash=args.squash,
            skiplist=args.skiplist,
            separator=args.separator,
            with_type=args.with_type,
            with_example=args.with_example,
            full=args.full,
        )

    fn = run_shape
    sparser = subparsers.add_parser(
        shape.__name__, help=shape.__doc__, formatter_class=parser.formatter_class
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
    def run_shrink(args: argparse.Namespace) -> None:
        shrink(
            files=args.files,
            input_format=args.input_format,
            output_format=args.output_format,
            max_length_of_string=args.max_length_of_string,
            cont_suffix=args.cont_suffix,
            max_length_of_list=args.max_length_of_list,
            with_tail=args.with_tail,
        )

    fn = run_shrink
    sparser = subparsers.add_parser(
        shrink.__name__, help=shrink.__doc__, formatter_class=parser.formatter_class
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
    def run_mkdict(args: argparse.Namespace) -> None:
        mkdict(
            output_format=args.output_format,
            separator=args.separator,
            delimiter=args.delimiter,
            sort_keys=args.sort_keys,
            squash=args.squash,
            extra=args.extra,
        )

    fn = run_mkdict
    sparser = subparsers.add_parser(
        mkdict.__name__, help=mkdict.__doc__, formatter_class=parser.formatter_class
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

            subcommand_func = params.pop("subcommand")
            # argparse.Namespace 型を期待するラッパー関数を呼び出す
            return subcommand_func(argparse.Namespace(**params))
