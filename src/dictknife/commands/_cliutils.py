import sys
import contextlib
import argparse


@contextlib.contextmanager
def traceback_shortly(debug: bool):
    try:
        yield
    except Exception as e:
        if debug:
            raise
        else:
            print(
                "\x1b[33m\x1b[1m{e.__class__.__name__}: {e}\x1b[0m".format(e=e),
                file=sys.stderr,
            )
            sys.exit(1)


class ExtraArgumentsParsers:
    def __init__(
        self,
        parser,
        dest,
        *,
        prefix: str = "extra",
        parser_factory=argparse.ArgumentParser,
    ) -> None:
        self.parser = parser
        self.dest = dest

        self.prefix = prefix
        self.mapping: dict = {}
        self.parser_factory = parser_factory

        self.bind(parser)  # xxx: side effect

    def add_parser(self, name: str):
        self.mapping[name] = p = self.parser_factory(
            "{self.prefix} arguments {name}".format(self=self, name=name),
            description="for {self.dest}={name}".format(self=self, name=name),
            add_help=False,
        )
        return p

    def as_epilog(self):
        r = [
            "{self.prefix} arguments: (with --{self.prefix}<option>)".format(self=self)
        ]

        formatter = argparse.HelpFormatter("")
        for name, parser in self.mapping.items():
            is_empty = True
            for action_group in parser._action_groups:
                if len(action_group._group_actions) > 0:
                    is_empty = False
                    break
            if is_empty:
                continue

            formatter.start_section(parser.description)
            for action_group in parser._action_groups:
                formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        r.extend(formatter.format_help().split("\n"))
        return "\n  ".join(r).rstrip(" ")

    def bind(self, parser):
        if hasattr(parser, "_original_format_help"):
            raise RuntimeError("extra arguments parser is already bounded")
        original_format_help = parser.format_help
        parser._original_format_help = original_format_help

        def format_help():
            return "\n".join([original_format_help(), self.as_epilog()])

        parser.format_help = format_help
        return parser

    def parse_args(self, name: str, args):
        rest = self._transform_args(args)
        return self._parse_args(name, rest)

    def _transform_args(self, args):
        prefix = "--{prefix}".format(prefix=self.prefix)
        return [(x[7:] if x.startswith(prefix) else x) for x in args]

    def _parse_args(self, name: str, rest):
        parser = self.mapping[name]
        args, rest = parser.parse_known_args(rest, namespace=argparse.Namespace())
        self._show_warnigs(rest)
        return args

    def _show_warnigs(self, rest) -> None:
        if not rest:
            return
        print(
            "extra arguments: {rest!r} are ignored (option: {self.dest})".format(
                rest=rest, self=self
            ),
            file=sys.stderr,
        )
