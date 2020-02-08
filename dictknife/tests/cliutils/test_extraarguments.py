import textwrap
import unittest


class Tests(unittest.TestCase):
    maxDiff = None

    def _getTarget(self):
        from dictknife.cliutils.extraarguments import ExtraArgumentsParsers

        return ExtraArgumentsParsers

    def _makeOne(self):
        from argparse import ArgumentParser

        parser = ArgumentParser("cmd")
        target = self._getTarget()(parser, "--format", prefix="extra")
        sparser0 = target.add_parser("json")
        sparser0.add_argument("--sort-keys", action="store_true", help="sort keys")

        sparser1 = target.add_parser("toml")  # noqa
        return target

    def test_help_message(self):
        target = self._makeOne()
        expected = textwrap.dedent(
            """
        usage: cmd [-h]

        optional arguments:
          -h, --help  show this help message and exit

        extra arguments: (with --extra<option>)
          for --format=json:
            --sort-keys  sort keys
        """
        ).strip()

        actual = target.parser.format_help().strip()
        self.assertEqual(actual, expected)

    def test_parse_extra_arguments(self):
        target = self._makeOne()
        args = target.parse_args("json", ["--extra--sort-keys"])
        actual = vars(args)
        expected = {"sort_keys": True}
        self.assertEqual(actual, expected)

    def test_parse_extra_arguments_are_ignored(self):
        import contextlib
        from io import StringIO

        target = self._makeOne()

        with contextlib.redirect_stderr(StringIO()) as o:
            args = target.parse_args("toml", ["--extra--sort-keys"])
            actual = vars(args)
            expected = {}
            self.assertEqual(actual, expected)

        self.assertIn("--sort-keys", o.getvalue())
        self.assertIn("ignored", o.getvalue())
