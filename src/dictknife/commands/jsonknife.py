import logging
import contextlib
import warnings
from typing import List, Any, Optional
from dictknife.langhelpers import make_dict
from dictknife import loading
from dictknife import deepmerge
from dictknife.commands._cliutils import traceback_shortly

logger = logging.getLogger(__name__)


def cut(*, src: Optional[str], dst: Optional[str], refs: List[str]) -> None:
    from dictknife.accessing import Accessor

    d = loading.loadfile(src)
    accessor = Accessor(make_dict)
    for ref in refs:
        if ref.startswith("#/"):
            ref = ref[2:]
        accessor.maybe_remove(d, ref.split("/"))
    loading.dumpfile(d, dst)


def deref(*, src, dst, refs, unwrap, wrap, input_format, output_format, format):
    warnings.warn("deref() is deprecated, please using `select()` instead of it.")
    return select(
        src=src,
        dst=dst,
        refs=refs,
        unwrap=unwrap,
        wrap=wrap,
        input_format=input_format,
        output_format=output_format,
        format=format,
    )


def select(
    *,
    src: Optional[str],
    dst: Optional[str],
    refs: List[str],
    unwrap: Optional[str],
    wrap: Optional[str],
    input_format: Optional[str],
    output_format: Optional[str],
    format: Optional[str],
) -> None:
    from dictknife.jsonknife import Expander
    from dictknife.jsonknife.accessor import assign_by_json_pointer
    from dictknife.jsonknife import get_resolver

    input_format = input_format or format
    resolver = get_resolver(src)
    expander = Expander(resolver)
    if unwrap and not refs:
        refs = []
        refs.append(unwrap)

    if not refs:
        d = expander.expand()
    else:
        d = make_dict()
        for ref in refs:
            ref_wrap = wrap
            if "@" in ref:
                ref, ref_wrap = ref.split("@", 1)
            extracted = expander.expand_subpart(expander.access(ref))
            if ref_wrap:
                assign_by_json_pointer(d, ref_wrap, extracted)
            else:
                d = deepmerge(d, extracted)
    loading.dumpfile(d, dst, format=output_format or format)


def bundle(
    *,
    src: Optional[str],
    dst: Optional[str] = None,
    ref: Optional[str] = None,
    input_format: Optional[str],
    output_format: Optional[str],
    format: Optional[str],
    flavor: Optional[str],
    extras: Optional[List[str]] = None,
) -> None:
    from dictknife.jsonknife import bundle as bundle_module

    if ref is not None and src is not None:
        src = "{prefix}#/{name}".format(prefix=src, name=ref.lstrip("#/"))
    result = bundle_module(
        src, format=input_format or format, extras=extras, flavor=flavor
    )
    loading.dumpfile(result, dst, format=output_format or format)


def separate(
    *,
    src: Optional[str],
    dst: Optional[str] = None,
    input_format: Optional[str],
    output_format: Optional[str],
    format: Optional[str],
) -> None:
    from dictknife.jsonknife import separate

    separate(
        src,
        dst=dst,
        input_format=input_format or format,
        output_format=output_format or format,
    )


def examples(
    *,
    src: Optional[str],
    dst: Optional[str] = None,
    ref: Optional[str],
    limit: int,
    input_format: Optional[str],
    output_format: Optional[str],
    format: Optional[str],
    use_expand: bool = False,
) -> None:
    """output sample value from swagger's spec"""
    from dictknife.jsonknife import extract_example
    from dictknife.jsonknife.accessor import access_by_json_pointer

    data: Any
    if use_expand:
        from dictknife.jsonknife import bundle as bundle_module, expand

        if ref is not None and src is not None:
            src = "{prefix}#/{name}".format(prefix=src, name=ref.lstrip("#/"))
        data = bundle_module(src, format=input_format or format)
        data = expand(None, doc=data)
    else:
        data = loading.loadfile(src, format=input_format or format)

    actual_ref = ref
    if src and "#/" in src:
        _, actual_ref = src.split("#/", 1)
    if actual_ref is not None:
        data = access_by_json_pointer(data, actual_ref)
    d: Any = extract_example(data, limit=limit)
    loading.dumpfile(d, dst, format=output_format or format or "json")


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

    subparsers = parser.add_subparsers(dest="subcommand", title="subcommands")
    subparsers.required = True

    # cut
    def run_cut(args: argparse.Namespace) -> None:
        cut(src=args.src, dst=args.dst, refs=args.refs)

    fn = run_cut
    sparser = subparsers.add_parser(
        cut.__name__, help=cut.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("--ref", dest="refs", action="append", help="-")

    # deref
    def run_deref(args: argparse.Namespace) -> None:
        deref(
            src=args.src,
            dst=args.dst,
            refs=args.refs,
            unwrap=args.unwrap,
            wrap=args.wrap,
            input_format=args.input_format,
            output_format=args.output_format,
            format=args.format,
        )

    fn = run_deref
    sparser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("--ref", dest="refs", action="append", help="-")
    sparser.add_argument("--unwrap", default=None, help="-")
    sparser.add_argument("--wrap", default=None, help="-")
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )

    # select
    def run_select(args: argparse.Namespace) -> None:
        select(
            src=args.src,
            dst=args.dst,
            refs=args.refs,
            unwrap=args.unwrap,
            wrap=args.wrap,
            input_format=args.input_format,
            output_format=args.output_format,
            format=args.format,
        )

    fn = run_select
    sparser = subparsers.add_parser(
        select.__name__, help=select.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("--ref", dest="refs", action="append", help="-")
    sparser.add_argument("--unwrap", default=None, help="-")
    sparser.add_argument("--wrap", default=None, help="-")
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )

    # bundle
    def run_bundle(args: argparse.Namespace) -> None:
        bundle(
            src=args.src,
            dst=args.dst,
            ref=args.ref,
            input_format=args.input_format,
            output_format=args.output_format,
            format=args.format,
            flavor=args.flavor,
            extras=args.extras,
        )

    fn = run_bundle
    sparser = subparsers.add_parser(
        bundle.__name__, help=bundle.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("--ref", default=None, help="-")
    sparser.add_argument(
        "--flavor", choices=["openapiv3", "openapiv2"], default="openapiv3", help="-"
    )
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument("--extra", default=None, nargs="+", dest="extras", help="-")

    # separate
    def run_separate(args: argparse.Namespace) -> None:
        separate(
            src=args.src,
            dst=args.dst,
            input_format=args.input_format,
            output_format=args.output_format,
            format=args.format,
        )

    fn = run_separate
    sparser = subparsers.add_parser(
        separate.__name__, help=separate.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )

    # examples
    def run_examples(args: argparse.Namespace) -> None:
        examples(
            src=args.src,
            dst=args.dst,
            ref=args.ref,
            limit=args.limit,
            input_format=args.input_format,
            output_format=args.output_format,
            format=args.format,
            use_expand=args.use_expand,
        )

    fn = run_examples
    sparser = subparsers.add_parser(
        examples.__name__, help=examples.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("src", nargs="?", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("--ref", dest="ref", default=None, help="-")
    sparser.add_argument("--limit", dest="limit", default=5, type=int, help="-")
    sparser.add_argument("--expand", dest="use_expand", action="store_true", help="-")
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )

    args = parser.parse_args()

    with contextlib.ExitStack() as s:
        params = vars(args)
        if params.pop("quiet"):
            args.log_level = logging._levelToName[logging.WARNING]
            s.enter_context(warnings.catch_warnings())
            warnings.simplefilter("ignore")
        logging.basicConfig(level=getattr(logging, params.pop("log_level")))
        with traceback_shortly(params.pop("debug")):
            subcommand_func = params.pop("subcommand")
            return subcommand_func(argparse.Namespace(**params))
