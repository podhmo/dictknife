def apply_loading_format_extra_arguments_parser(parser):
    from importlib import import_module
    from dictknife.cliutils.extraaguments import ExtraArgumentsParsers
    from dictknife import loading

    formats = loading.get_formats()
    ex_parsers = ExtraArgumentsParsers(parser, "--format")  # xxx:
    for f in formats:
        if f == "markdown":  # xxx:
            continue

        m = import_module(f"dictknife.loading.{f}")
        ex_parser = ex_parsers.add_parser(f)
        setup = getattr(m, "setup_parser", None)
        if setup is None:
            print(f"{m.__name__} doesn't have setup_parser() function", file=sys.stderr)
            continue
        setup(ex_parser)

    original = parser.parse_known_args

    def parse_known_args(*args, **kwargs):
        args, rest = original(*args, **kwargs)
        if args.format is None:
            args.format = loading.get_unknown().__name__.split(".")[-1]
        ex_args = ex_parsers.parse_args(args.format, rest)
        args.extra = dict(vars(ex_args))
        return args, []  # xxx:

    parser.parse_known_args = parse_known_args
