def apply_rest_arguments_as_extra_arguments_parser(parser, *, dest: str="extra") -> None:
    original = parser.parse_known_args

    def parse_known_args(*args, **kwargs):
        parsed, extra = original(*args, **kwargs)
        setattr(parsed, dest, extra)
        return parsed, []

    parser.parse_known_args = parse_known_args


def apply_loading_format_extra_arguments_parser(parser) -> None:
    import sys
    import argparse
    from importlib import import_module
    from dictknife.cliutils.extraarguments import ExtraArgumentsParsers
    from dictknife import loading

    formats = loading.get_formats()
    ex_parsers = ExtraArgumentsParsers(parser, "--output-format")  # xxx:
    mixed_parser = argparse.ArgumentParser(conflict_handler="resolve")

    for f in formats:
        if f == "markdown":  # xxx:
            continue

        m = import_module("dictknife.loading.{f}".format(f=f))
        ex_parser = ex_parsers.add_parser(f)
        setup = getattr(m, "setup_extra_parser", None)
        if setup is None:
            print(
                "{m.__name__} doesn't have setup_extra_parser() function".format(m=m),
                file=sys.stderr,
            )
            continue

        setup(ex_parser)
        # xxx: Action has state (not copyable) , so, re-setup by setup function
        # for ac in ex_parser._actions:
        #     mixed_parser._add_action(new_ac)
        setup(mixed_parser)

    original = parser.parse_known_args

    def parse_known_args(*args, **kwargs):
        parsed, rest = original(*args, **kwargs)
        transformed_rest = ex_parsers._transform_args(rest)
        _, unexpected = mixed_parser.parse_known_args(
            transformed_rest, namespace=argparse.Namespace()
        )
        if unexpected:
            return parsed, unexpected  # xxx:

        if parsed.output_format is None:
            parsed.output_format = (
                parsed.format or loading.get_unknown().__name__.split(".")[-1]
            )
        if parsed.dst is not None:
            parsed.output_format = loading.guess_format(parsed.dst)
        ex_parsed = ex_parsers._parse_args(parsed.output_format, transformed_rest)
        parsed.extra = dict(vars(ex_parsed))
        return parsed, []

    parser.parse_known_args = parse_known_args
