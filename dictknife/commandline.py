import contextlib
import argparse


class SubCommandParser:
    def __init__(self, *args, **kwargs):
        parser = argparse.ArgumentParser(*args, **kwargs)
        parser.print_usage = parser.print_help  # hack
        self.parser = parser
        self.subparsers = parser.add_subparsers(dest="subcommand")
        self.subparsers.required = True

    def __getattr__(self, name):
        return getattr(self.parser, name)

    def subcommand(self, fn, *args, **kwargs):
        return subparser(self.subparsers, fn, *args, **kwargs)


@contextlib.contextmanager
def subparser(subparsers, fn, *args, **kwargs):
    parser = subparsers.add_parser(fn.__name__, *args, **kwargs)
    dests = []
    arrived = set()

    def add_argument(*args, **kwargs):
        ac = parser.add_argument(*args, **kwargs)
        if ac.dest not in arrived:
            arrived.add(ac.dest)
            dests.append(ac.dest)
        return ac

    yield add_argument

    def run(args):
        return fn(**{name: getattr(args, name) for name in dests})

    parser.set_defaults(fn=run)
