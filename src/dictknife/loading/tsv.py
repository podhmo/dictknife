from functools import partial
from . import csv

setup_extra_parser = csv.setup_extra_parser
"""Setup extra parser arguments for TSV format (delegated to CSV)."""

load = partial(csv.load, delimiter="\t")
"""Loads TSV data from a file-like object.

This is a partial function of `dictknife.loading.csv.load` with the
delimiter set to '\\t'.

Args:
    fp: A file-like object supporting .read().
    loader: (Optional) The loader instance.
    errors: (Optional) Error handling scheme.
    **kwargs: Additional keyword arguments passed to `csv.reader`.

Returns:
    A list of lists representing the rows and cells of the TSV data.
"""

dump = partial(csv.dump, delimiter="\t")
"""Dumps a list of lists to a file-like object in TSV format.

This is a partial function of `dictknife.loading.csv.dump` with the
delimiter set to '\\t'.

Args:
    d: A list of lists to dump.
    fp: A file-like object supporting .write().
    sort_keys: (Unused for TSV/CSV) Whether to sort keys.
    **kwargs: Additional keyword arguments passed to `csv.writer`.
"""
