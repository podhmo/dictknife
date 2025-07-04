# -*- coding:utf-8 -*-
import sys
import os.path
import logging
from io import StringIO
from typing import Callable
from . import json
from . import raw
from . import env
from . import yaml
from . import toml
from . import tsv
from . import csv
from . import md
from . import spreadsheet  # optional

logger = logging.getLogger(__name__)
unknown = "(unknown)"


class Loader:
    """A class for loading data from various formats.

    The Loader class provides methods to load data from file-like objects or strings.
    It uses a dispatcher to determine the correct loading function based on the format
    or file extension.

    Note: Loading certain formats might require optional dependencies. For example,
    loading from Google Spreadsheets (via the `loadfile` method with a spreadsheet URL)
    requires `google-api-python-client` and `google-auth-oauthlib`. These can often
    be installed using extras, e.g., `pip install dictknife[spreadsheet]`.
    Refer to the documentation of individual format handlers for specific requirements.
    """
    def __init__(self, dispatcher) -> None:
        """Initializes the Loader with a dispatcher.

        Args:
            dispatcher: The dispatcher instance to use for format detection.
        """
        self.dispatcher = dispatcher
        self.fn_map: dict[str, Callable] = {}
        self.opener_map: dict[str, Callable] = {}

    def add_format(self, fmt: str, fn: Callable, *, opener: Callable = None) -> None:
        """Adds a new format and its corresponding loading function.

        Args:
            fmt: The format identifier (e.g., "json", "yaml").
            fn: The function to call for loading this format.
            opener: An optional function to open files for this format.
        """
        self.fn_map[fmt] = fn
        if opener is not None:
            self.opener_map[fmt] = opener

    def loads(self, s: str, *args, **kwargs):
        """Loads data from a string.

        Args:
            s: The string containing the data to load.
            *args: Additional arguments to pass to the loading function.
            **kwargs: Additional keyword arguments to pass to the loading function.

        Returns:
            The loaded data.
        """
        return load(StringIO(s), *args, **kwargs)

    def load(self, fp, format: str = None, errors=None):
        """Loads data from a file-like object.

        If format is not specified, it attempts to guess the format from the
        environment variable DICTKNIFE_LOAD_FORMAT or the file extension.

        Args:
            fp: The file-like object to read from.
            format: The format of the data. If None, it will be guessed.
            errors: Error handling scheme for codecs.

        Returns:
            The loaded data.
        """
        load_func: Callable
        if format is not None:
            load_func = self.fn_map[format]
        else:
            format = os.environ.get("DICTKNIFE_LOAD_FORMAT")
            if format is not None:
                load_func = self.fn_map[format]
            else:
                fname = getattr(fp, "name", "(unknown)")
                load_func = self.dispatcher.dispatch(fname, self.fn_map)

        return load_func(fp, loader=self, errors=errors)

    def loadfile(
        self,
        filename: str = None,
        format: str = None,
        opener: Callable = None,
        encoding: str = None,
        errors=None,
    ):
        """Loads data from a file or stdin.

        If filename is None, reads from stdin.
        If format is not specified, it's guessed from the filename extension.
        Optional dependencies might be required for certain formats (e.g., 'spreadsheet').

        Args:
            filename: The path to the file to load. If None, reads from stdin.
            format: The format of the data. If None, it will be guessed.
            opener: An optional function to open the file.
            encoding: The encoding to use when opening the file.
            errors: Error handling scheme for codecs.

        Returns:
            The loaded data.
        """
        if filename is None:
            return self.load(sys.stdin, format=format)
        else:
            actual_opener: Callable = opener or self.opener_map.get(format) or open
            with actual_opener(filename, encoding=encoding, errors=errors) as rf:
                r = self.load(rf, format=format, errors=errors)
                if (
                    not hasattr(r, "keys")
                    and hasattr(r, "__iter__")
                    and not isinstance(r, (str, bytes))
                ):
                    r = list(r)
                return r


class Dumper:
    """A class for dumping data to various formats.

    The Dumper class provides methods to dump data to file-like objects or strings.
    It uses a dispatcher to determine the correct dumping function based on the format
    or file extension.

    Note: Dumping to certain formats might require optional dependencies. For example,
    YAML format requires `ruamel.yaml`, and TOML format requires `tomlkit`.
    These can often be installed using extras, e.g., `pip install dictknife[load]`
    (as 'load' extra includes common serialization libraries). Refer to the
    documentation of individual format handlers for specific requirements.
    """
    def __init__(self, dispatcher) -> None:
        """Initializes the Dumper with a dispatcher.

        Args:
            dispatcher: The dispatcher instance to use for format detection.
        """
        self.dispatcher = dispatcher
        self.fn_map: dict[str, Callable] = {}

    def add_format(self, fmt: str, fn: Callable) -> None:
        """Adds a new format and its corresponding dumping function.

        Args:
            fmt: The format identifier (e.g., "json", "yaml").
            fn: The function to call for dumping this format.
        """
        self.fn_map[fmt] = fn

    def dumps(self, d, *, format: str = None, sort_keys: bool = False, extra=None, **kwargs) -> str:
        """Dumps data to a string.

        Args:
            d: The data to dump.
            format: The format to dump to. If None, it will be guessed.
            sort_keys: Whether to sort keys in the output.
            extra: Additional arguments for the dumping function.
            **kwargs: Additional keyword arguments for the dumping function.

        Returns:
            A string representation of the data in the specified format.
        """
        fp = StringIO()
        self.dump(d, fp, format=format, sort_keys=sort_keys, extra=extra, **kwargs)
        return fp.getvalue()

    def dump(self, d, fp, *, format: str = None, sort_keys: bool = False, extra=None):
        """Dumps data to a file-like object.

        If format is not specified, it attempts to guess the format from the
        environment variable DICTKNIFE_DUMP_FORMAT or the file extension.

        Args:
            d: The data to dump.
            fp: The file-like object to write to.
            format: The format to dump to. If None, it will be guessed.
            sort_keys: Whether to sort keys in the output.
            extra: Additional arguments for the dumping function.
        """
        dump_func: Callable
        if format is not None:
            dump_func = self.fn_map[format]
        else:
            format = os.environ.get("DICTKNIFE_DUMP_FORMAT")
            if format is not None:
                dump_func = self.fn_map[format]
            else:
                fname = getattr(fp, "name", "(unknown)")
                dump_func = self.dispatcher.dispatch(fname, self.fn_map)
        extra = extra or {}
        return dump_func(d, fp, sort_keys=sort_keys, **extra)

    def dumpfile(
        self,
        d,
        filename: str = None,
        *,
        format: str = None,
        sort_keys: bool = False,
        extra=None,
        _retry: bool = False,
    ):
        """Dumps data to a file or stdout.

        If filename is None, writes to stdout.
        If the directory for the output file does not exist, it will be created.
        Optional dependencies might be required for certain formats (e.g., 'yaml', 'toml').

        Args:
            d: The data to dump.
            filename: The path to the file to write. If None, writes to stdout.
            format: The format to dump to. If None, it will be guessed.
            sort_keys: Whether to sort keys in the output.
            extra: Additional arguments for the dumping function.
            _retry: Internal flag for retrying after directory creation.
        """
        if hasattr(d, "__next__"):  # iterator
            d = list(d)

        if filename is None:
            return self.dump(
                d, sys.stdout, format=format, sort_keys=sort_keys, extra=extra
            )
        else:
            try:
                with open(filename, "w") as wf:
                    return self.dump(
                        d, wf, format=format, sort_keys=sort_keys, extra=extra
                    )
            except FileNotFoundError:
                if _retry:
                    raise
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                return self.dumpfile(
                    d,
                    filename,
                    format=format,
                    sort_keys=sort_keys,
                    extra=extra,
                    _retry=True,
                )


class Dispatcher:
    """A class for managing and dispatching loading and dumping functions.

    The Dispatcher holds instances of Loader and Dumper and maps file extensions
    to specific formats.
    """
    loader_factory = Loader
    dumper_factory = Dumper

    def __init__(self) -> None:
        """Initializes the Dispatcher, creating Loader and Dumper instances."""
        self.loader = self.loader_factory(self)
        self.dumper = self.dumper_factory(self)
        self.exts_matching: dict[str, str] = {}

    def guess_format(self, filename: str, *, default=unknown) -> str:
        """Guesses the data format based on the filename extension.

        Args:
            filename: The name of the file.
            default: The default format to return if no match is found.

        Returns:
            The guessed format string (e.g., "json", "yaml") or the default.
        """
        if filename is None:
            return default
        _, ext = os.path.splitext(filename)
        return self.exts_matching.get(ext) or default

    def dispatch(
        self, filename: str, fn_map: dict[str, Callable], default=unknown
    ) -> Callable:
        """Dispatches to the appropriate function based on the guessed format.

        Args:
            filename: The name of the file.
            fn_map: A dictionary mapping format strings to functions.
            default: The default format to use if guessing fails.

        Returns:
            The function corresponding to the guessed format.
        """
        fmt = self.guess_format(filename, default=default)
        return fn_map[fmt]

    def add_format(
        self, fmt: str, load: Callable, dump: Callable, *, exts: list[str] = [], opener: Callable = None
    ) -> None:
        """Adds a new format with its load, dump functions, and associated extensions.

        Args:
            fmt: The format identifier (e.g., "json", "yaml").
            load: The function to call for loading this format.
            dump: The function to call for dumping this format.
            exts: A list of file extensions associated with this format (e.g., [".json", ".js"]).
            opener: An optional function to open files for this format (for loader).
        """
        self.loader.add_format(fmt, load, opener=opener)
        self.dumper.add_format(fmt, dump)
        for ext in exts:
            self.exts_matching[ext] = fmt


dispatcher = Dispatcher()
dispatcher.add_format("yaml", yaml.load, yaml.dump, exts=(".yaml", ".yml"))
dispatcher.add_format("json", json.load, json.dump, exts=(".json", ".js"))
dispatcher.add_format("toml", toml.load, toml.dump, exts=(".toml",))
dispatcher.add_format("csv", csv.load, csv.dump, exts=(".csv",))
dispatcher.add_format("tsv", tsv.load, tsv.dump, exts=(".tsv",))
dispatcher.add_format("raw", raw.load, raw.dump, exts=[])
dispatcher.add_format("env", env.load, None, exts=(".env", ".environ"))
dispatcher.add_format("md", md.load, md.dump, exts=(".md", ".mdtable"))
dispatcher.add_format("markdown", md.load, md.dump, exts=[])
dispatcher.add_format(
    "spreadsheet", spreadsheet.load, None, exts=[], opener=spreadsheet.not_open
)
dispatcher.add_format(unknown, yaml.load, yaml.dump, exts=[])

# short cuts
load = dispatcher.loader.load
"""Alias for `dispatcher.loader.load`."""
loads = dispatcher.loader.loads
"""Alias for `dispatcher.loader.loads`."""
loadfile = dispatcher.loader.loadfile
"""Alias for `dispatcher.loader.loadfile`.

This function may require optional dependencies for certain file formats.
See the `Loader` class docstring or individual format loader documentation for details
on required packages and installation (e.g., using `dictknife[spreadsheet]`).
"""
dump = dispatcher.dumper.dump
"""Alias for `dispatcher.dumper.dump`."""
dumps = dispatcher.dumper.dumps
"""Alias for `dispatcher.dumper.dumps`."""
dumpfile = dispatcher.dumper.dumpfile
"""Alias for `dispatcher.dumper.dumpfile`.

This function may require optional dependencies for certain file formats.
See the `Dumper` class docstring or individual format dumper documentation for details
on required packages and installation (e.g., using `dictknife[load]`).
"""
guess_format = dispatcher.guess_format
"""Alias for `dispatcher.guess_format`."""


def get_opener(*, format: str = None, filename: str = None, default=open, dispatcher=dispatcher) -> Callable:
    """Gets the appropriate file opener for a given format or filename.

    If format is not provided, it's guessed from the filename.
    This is particularly useful for formats that require special file handling,
    like spreadsheets.

    Args:
        format: The data format (e.g., "spreadsheet").
        filename: The name of the file (used to guess format if `format` is None).
        default: The default opener function to return if no specific opener is found.
        dispatcher: The dispatcher instance to use.

    Returns:
        A callable that can be used to open a file.
    """
    if format is None and filename is not None:
        if hasattr(filename, "name"):
            filename = filename.name  # IO
        format = dispatcher.guess_format(filename)

    opener = dispatcher.loader.opener_map.get(format)
    if opener is None:
        return default
    return opener


def get_formats(dispatcher=dispatcher) -> list[str]:
    """Returns a list of supported format identifiers.

    Args:
        dispatcher: The dispatcher instance to use.

    Returns:
        A list of format strings (e.g., ["json", "yaml", "toml"]).
    """
    return [fmt for fmt in dispatcher.loader.fn_map.keys() if fmt != unknown]


def get_unknown(dispatcher=dispatcher):
    """Gets the module associated with the 'unknown' format loader.

    This is typically the default loader used when a format cannot be determined.

    Args:
        dispatcher: The dispatcher instance to use.

    Returns:
        The module object for the unknown format loader.
    """
    loader = dispatcher.loader.fn_map[unknown]
    return sys.modules[loader.__module__]


def setup(input: Callable = None, output: Callable = None, dispatcher=dispatcher, unknown=unknown) -> None:
    """Configures the default loader and dumper for 'unknown' formats.

    This allows overriding the default behavior for files where the format
    cannot be automatically determined.

    Args:
        input: The function to use for loading unknown formats.
        output: The function to use for dumping unknown formats.
        dispatcher: The dispatcher instance to configure.
        unknown: The identifier for the unknown format.
    """
    if input is not None:
        logger.debug("setup input format: %s", input)
        dispatcher.loader.add_format(unknown, input)
    if output is not None:
        logger.debug("setup output format: %s", output)
        dispatcher.dumper.add_format(unknown, output)
