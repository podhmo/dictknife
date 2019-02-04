def apply_rest_arguments_as_extra_arguments_parser(parser, *, dest="extra"):
    original = parser.parse_known_args

    def parse_known_args(*args, **kwargs):
        args, extra = original(*args, **kwargs)
        setattr(args, dest, extra)
        return args, []

    parser.parse_known_args = parse_known_args


def apply_loading_format_extra_arguments_parser(parser):
    from importlib import import_module
    from dictknife.cliutils.extraaguments import ExtraArgumentsParsers
    from dictknife import loading

    formats = loading.get_formats()
    ex_parsers = ExtraArgumentsParsers(parser, "--output-format")  # xxx:
    for f in formats:
        if f == "markdown":  # xxx:
            continue

        m = import_module(f"dictknife.loading.{f}")
        ex_parser = ex_parsers.add_parser(f)
        setup = getattr(m, "setup_extra_parser", None)
        if setup is None:
            print(f"{m.__name__} doesn't have setup_extra_parser() function", file=sys.stderr)
            continue
        setup(ex_parser)

    original = parser.parse_known_args

    def parse_known_args(*args, **kwargs):
        args, rest = original(*args, **kwargs)
        if args.output_format is None:
            args.output_format = args.format or loading.get_unknown().__name__.split(".")[-1]
        if args.dst is not None:
            args.output_format = loading.guess_format(args.dst)
        ex_args = ex_parsers.parse_args(args.output_format, rest)
        args.extra = dict(vars(ex_args))
        return args, []  # xxx:

    parser.parse_known_args = parse_known_args
