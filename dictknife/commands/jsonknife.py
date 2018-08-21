# -*- coding:utf-8 -*-
import logging
from dictknife.langhelpers import make_dict
from dictknife.commandline import SubCommandParser
from dictknife import loading
from dictknife import deepmerge
from dictknife.accessing import Accessor
from dictknife.jsonknife import Expander
from dictknife.jsonknife import Bundler
from dictknife.jsonknife import extract_example
from dictknife.jsonknife.resolver import get_resolver_from_filename
from dictknife.jsonknife.accessor import assign_by_json_pointer, access_by_json_pointer

logger = logging.getLogger(__name__)


def cut(*, src, dst, refs):
    d = loading.loadfile(src)
    accessor = Accessor(make_dict)
    for ref in refs:
        if ref.startswith("#/"):
            ref = ref[2:]
        accessor.maybe_remove(d, ref.split("/"))
    loading.dumpfile(d, dst)


def deref(*, src, dst, refs, unwrap, wrap):
    resolver = get_resolver_from_filename(src)
    expander = Expander(resolver)
    if unwrap and not refs:
        refs = list(refs)
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
    loading.dumpfile(d, dst)


def bundle(*, src, dst):
    resolver = get_resolver_from_filename(src)
    bundler = Bundler(resolver)
    d = bundler.bundle()
    loading.dumpfile(d, dst)


def examples(*, src, ref, format):
    data = loading.loadfile(src)
    if ref is not None:
        data = access_by_json_pointer(data, ref)
    d = extract_example(data)
    loading.dumpfile(d, format=format)


def main():
    parser = SubCommandParser()

    parser.add_argument("--log", choices=list(logging._nameToLevel.keys()), default="INFO")
    formats = loading.get_formats()

    with parser.subcommand(cut) as add_argument:
        add_argument("--src", default=None)
        add_argument("--dst", default=None)
        add_argument("--ref", dest="refs", action="append")

    with parser.subcommand(deref) as add_argument:
        add_argument("--src", default=None)
        add_argument("--dst", default=None)
        add_argument("--ref", dest="refs", action="append")
        add_argument("--unwrap", default=None)
        add_argument("--wrap", default=None)

    with parser.subcommand(bundle) as add_argument:
        add_argument("--src", default=None)
        add_argument("--dst", default=None)

    with parser.subcommand(
        examples, description="output sample value from swagger's spec"
    ) as add_argument:
        add_argument("src", nargs="?", default=None)
        add_argument("--ref", dest="ref", default=None)
        add_argument("-f", "--format", default="json", choices=formats)

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log))
    return args.fn(args)
