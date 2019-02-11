import logging
import contextlib
import warnings
from dictknife.langhelpers import make_dict
from dictknife import loading
from dictknife import deepmerge
from dictknife.cliutils import traceback_shortly

logger = logging.getLogger(__name__)


def cut(*, src, dst, refs):
    from dictknife.accessing import Accessor

    d = loading.loadfile(src)
    accessor = Accessor(make_dict)
    for ref in refs:
        if ref.startswith("#/"):
            ref = ref[2:]
        accessor.maybe_remove(d, ref.split("/"))
    loading.dumpfile(d, dst)


def deref(*, src, dst, refs, unwrap, wrap):
    warnings.warn("deref() is deprecated, please using `select()` instead of it.")
    return select(src=src, dst=dst, refs=refs, unwrap=unwrap, wrapped=wrapped)


def select(
    *,
    src: str,
    dst: str,
    refs,
    unwrap,
    wrap,
    input_format: str,
    output_format: str,
    format: str
):
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
    src: str,
    dst: str = None,
    ref: str = None,
    input_format: str,
    output_format: str,
    format: str,
    extras: list = None
):
    from dictknife.jsonknife import bundle

    if ref is not None:
        src = "{prefix}#/{name}".format(prefix=src, name=ref.lstrip('#/'))
    loading.dumpfile(
        bundle(src, format=input_format or format, extras=extras),
        dst,
        format=output_format or format,
    )


def examples(
    *,
    src: str,
    dst: str = None,
    ref: str,
    limit: int,
    input_format: str,
    output_format: str,
    format: str,
    use_expand: bool = False
):
    """output sample value from swagger's spec"""
    from dictknife.jsonknife import extract_example
    from dictknife.jsonknife.accessor import access_by_json_pointer

    if use_expand:
        from dictknife.jsonknife import bundle, expand

        if ref is not None:
            src = "{prefix}#/{name}".format(prefix=src, name=ref.lstrip('#/'))
        data = bundle(src, format=input_format or format)
        data = expand(None, doc=data)
    else:
        data = loading.loadfile(src, format=input_format or format)

    if src and "#/" in src:
        _, ref = src.split("#/", 1)
    if ref is not None:
        data = access_by_json_pointer(data, ref)
    d = extract_example(data, limit=limit)
    loading.dumpfile(d, dst, format=output_format or format or "json")


def main():
    import argparse

    formats = loading.get_formats()

    parser = argparse.ArgumentParser()
    parser.print_usage = parser.print_help  # hack
    parser.add_argument(
        "--log",
        choices=list(logging._nameToLevel.keys()),
        default="INFO",
        dest="log_level",
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--debug", action="store_true")

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    # cut
    fn = cut
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("--ref", dest="refs", action="append")

    # deref
    fn = deref
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("--ref", dest="refs", action="append")
    sparser.add_argument("--unwrap", default=None)
    sparser.add_argument("--wrap", default=None)
    sparser.add_argument("-f", "--format", default=None, choices=formats)
    sparser.add_argument("-i", "--input-format", default=None, choices=formats)
    sparser.add_argument("-o", "--output-format", default=None, choices=formats)
    # select
    fn = select
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("--ref", dest="refs", action="append")
    sparser.add_argument("--unwrap", default=None)
    sparser.add_argument("--wrap", default=None)
    sparser.add_argument("-f", "--format", default=None, choices=formats)
    sparser.add_argument("-i", "--input-format", default=None, choices=formats)
    sparser.add_argument("-o", "--output-format", default=None, choices=formats)

    # bundle
    fn = bundle
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("--ref", default=None)
    sparser.add_argument("-f", "--format", default=None, choices=formats)
    sparser.add_argument("-i", "--input-format", default=None, choices=formats)
    sparser.add_argument("-o", "--output-format", default=None, choices=formats)
    sparser.add_argument("--extra", default=None, nargs="+", dest="extras")

    # examples
    fn = examples
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("src", nargs="?", default=None)
    sparser.add_argument("--dst", default=None)
    sparser.add_argument("--ref", dest="ref", default=None)
    sparser.add_argument("--limit", dest="limit", default=5, type=int)
    sparser.add_argument("--expand", dest="use_expand", action="store_true")
    sparser.add_argument("-f", "--format", default=None, choices=formats)
    sparser.add_argument("-i", "--input-format", default=None, choices=formats)
    sparser.add_argument("-o", "--output-format", default=None, choices=formats)

    args = parser.parse_args()

    with contextlib.ExitStack() as s:
        params = vars(args)
        if params.pop("quiet"):
            args.log_level = logging._levelToName[logging.WARNING]
            s.enter_context(warnings.catch_warnings())
            warnings.simplefilter("ignore")
        logging.basicConfig(level=getattr(logging, params.pop("log_level")))
        with traceback_shortly(params.pop("debug")):
            return params.pop("subcommand")(**params)
