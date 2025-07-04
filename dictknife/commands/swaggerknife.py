import os.path
import logging
import warnings
import contextlib
from typing import Dict, Any, List, Optional, cast # Added Optional, cast
from dictknife import loading
from dictknife.cliutils import traceback_shortly
from magicalimport import import_symbol

logger = logging.getLogger(__name__)


def tojsonschema(*, src: Optional[str], dst: Optional[str], name: Optional[str]) -> None:
    # todo: id
    assert src is not None, "src must be specified for tojsonschema"
    assert name is not None, "name must be specified for tojsonschema"
    d = loading.loadfile(src)
    root = d["definitions"].pop(name)
    root.update(d)
    loading.dumpfile(root, filename=dst)


def json2swagger(
    *,
    files: List[str],
    dst: Optional[str],
    output_format: Optional[str],
    name: Optional[str],
    detector: str,
    emitter: str,
    annotate: Optional[str],
    emit: Optional[str],
    with_minimap: bool,
    without_example: bool,
) -> None:
    from prestring import Module
    from dictknife import DictWalker

    annotate_data: Any
    if annotate is not None:
        annotate_data = loading.loadfile(annotate)
    else:
        annotate_data = {}

    ns = "dictknife.swaggerknife.json2swagger"

    detector_cls = import_symbol(detector, ns=ns)
    actual_detector = cast(Any, detector_cls())

    emitter_cls = import_symbol(emitter, ns=ns)
    actual_emitter = cast(Any, emitter_cls(annotate_data))

    info: Any = None
    for src_file in files:
        data: Any = loading.loadfile(src_file)
        info = actual_detector.detect(data, name, info=info)

    if emit == "info":
        loading.dumpfile(info, filename=dst)
    else:
        m = Module(indent="  ")
        m.stmt(name)
        actual_emitter.emit(info, m)  # type: ignore[attr-defined]
        if with_minimap:
            print("# minimap ###")
            print("# *", end="")
            print("\n# ".join(str(m).split("\n")))

        if without_example:
            for _, d in DictWalker(["example"]).walk(actual_emitter.doc):  # type: ignore[attr-defined]
                d.pop("example")
        loading.dumpfile(actual_emitter.doc, filename=dst, format=output_format)  # type: ignore[attr-defined]


def merge(
    *,
    files: List[str],
    dst: str,
    style: str,  # flavor?, strategy?
    strict: bool = False,
    wrap: Optional[str] = None,
    wrap_section: Optional[str] = "definitions",
):
    """merge files"""
    from dictknife.langhelpers import make_dict, as_jsonpointer
    from dictknife import deepmerge

    r: Dict[str, Dict[str, Any]]
    if style == "ref":
        dstdir = dst and os.path.dirname(dst)

        r = make_dict()
        seen: Dict[str, Dict[str, str]] = {}
        for src_file in files:
            d = loading.loadfile(src_file)
            for ns, sd in d.items():
                for name_key in sd:
                    if ns not in r:
                        r[ns] = make_dict()
                        seen[ns] = make_dict()
                    if strict and name_key in r[ns]:
                        raise RuntimeError(
                            "{name} is already existed, (where={where} and {where2})".format(
                                name=name_key, where=seen[ns][name_key], where2=src_file
                            )
                        )
                    if dst is None:
                        where = ""
                    else:
                        where = os.path.relpath(src_file, start=dstdir)
                    r[ns][name_key] = {
                        "$ref": "{where}#/{ns}/{name}".format(
                            where=where, ns=ns, name=as_jsonpointer(name_key)
                        )
                    }
                    seen[ns][name_key] = src_file
    elif style == "whole":
        # TODO: strict support?
        loaded_data = [loading.loadfile(src_file) for src_file in files]
        r = deepmerge(*loaded_data, override=True)
    else:
        raise RuntimeError("invalid style: {}".format(style))

    if wrap is not None:
        wd: Dict[str, Any] = make_dict()
        wd["type"] = "object"
        wd["properties"] = make_dict()
        # ここでのrの型は Dict[str, Dict[str, Any]] または Dict[Any, Any] (deepmergeの結果による)
        # getの対象となるキーが存在し、かつその値が辞書であることを期待している
        # しかし、style == "whole" の場合、r.get(wrap_section) が辞書でない可能性がある
        # ここでは一旦Anyでキャストする
        wrap_section_data = r.get(wrap_section)
        if isinstance(wrap_section_data, dict):
            for name_key in wrap_section_data:
                properties = wd["properties"]
                if isinstance(properties, dict):
                    properties[name_key] = {
                        "$ref": "#/{wrap_section}/{name}".format(
                            wrap_section=wrap_section, name=name_key
                        )
                    }
        # r[wrap_section] が存在し、かつそれが辞書であることを期待
        if wrap_section not in r or not isinstance(r[wrap_section], dict):
            r[wrap_section] = make_dict() # もし存在しないか、辞書でなければ新しい辞書を作成

        # r[wrap_section] が辞書であることを保証した上でアクセス
        # しかし、mypyはこれだけでは納得しない可能性があるため、キャストを検討
        # ここでは、r の型が複雑なため、一旦エラーが出なくなることを優先する
        target_section = r[wrap_section]
        if isinstance(target_section, dict):
            target_section[wrap] = wd
        else:
            # このケースは通常発生しないはずだが、型チェッカーのために記述
            pass

    loading.dumpfile(r, dst)


def flatten(*, src: Optional[str], dst: Optional[str], input_format: Optional[str], output_format: Optional[str], format: Optional[str]) -> None:
    """flatten jsonschema sub definitions"""
    from dictknife.swaggerknife.flatten import flatten as flatten_module

    actual_input_format = input_format or format
    assert src is not None, "src must be specified for flatten"
    data: Any = loading.loadfile(src, format=actual_input_format)
    d: Any = flatten_module(data)
    loading.dumpfile(d, filename=dst, format=output_format or format)


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

    # merge
    def run_merge(args: argparse.Namespace) -> None:
        merge(
            files=args.files,
            dst=args.dst,
            style=args.style,
            strict=args.strict,
            wrap=args.wrap,
            wrap_section=args.wrap_section,
        )
    fn = run_merge
    sparser = subparsers.add_parser(
        merge.__name__, help=merge.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("--strict", action="store_true", help="-")
    sparser.add_argument("--style", default="ref", choices=["ref", "whole"], help="-")
    sparser.add_argument("--wrap", default=None, help="-")
    sparser.add_argument("--wrap-section", default="definitions", help="-")
    # tojsonschema
    def run_tojsonschema(args: argparse.Namespace) -> None:
        tojsonschema(src=args.src, dst=args.dst, name=args.name)
    fn = run_tojsonschema
    sparser = subparsers.add_parser(
        tojsonschema.__name__, help=tojsonschema.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("--src", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument("--name", default="top", help="-")

    # json2swagger
    def run_json2swagger(args: argparse.Namespace) -> None:
        assert args.detector is not None, "detector must be specified for json2swagger"
        assert args.emitter is not None, "emitter must be specified for json2swagger"
        json2swagger(
            files=args.files,
            dst=args.dst,
            output_format=args.output_format,
            name=args.name,
            detector=args.detector,
            emitter=args.emitter,
            annotate=args.annotate,
            emit=args.emit,
            with_minimap=args.with_minimap,
            without_example=args.without_example,
        )
    fn = run_json2swagger
    sparser = subparsers.add_parser(
        json2swagger.__name__, help=json2swagger.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("files", nargs="*", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument("--name", default="top", help="-")
    sparser.add_argument("--detector", default="Detector", help="-")
    sparser.add_argument("--emitter", default="Emitter", help="-")
    sparser.add_argument("--annotate", default=None, help="-")
    sparser.add_argument(
        "--emit", default="schema", choices=["schema", "info"], help="-"
    )
    sparser.add_argument("--with-minimap", action="store_true", help="-")
    sparser.add_argument("--without-example", action="store_true", help="-")

    # flatten
    def run_flatten(args: argparse.Namespace) -> None:
        flatten(
            src=args.src,
            dst=args.dst,
            input_format=args.input_format,
            output_format=args.output_format,
            format=args.format,
        )
    fn = run_flatten
    sparser = subparsers.add_parser(
        flatten.__name__, help=flatten.__doc__, formatter_class=parser.formatter_class
    )
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("src", nargs="?", default=None, help="-")
    sparser.add_argument("--dst", default=None, help="-")
    sparser.add_argument(
        "-i", "--input-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument(
        "-o", "--output-format", default=None, choices=formats, help="-"
    )
    sparser.add_argument("-f", "--format", default=None, choices=formats, help="-")

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
