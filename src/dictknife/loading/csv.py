import sys
from ._lazyimport import m
from dictknife.langhelpers import make_dict
from dictknife.guessing import guess
from logging import getLogger as get_logger

logger = get_logger(__name__)

_cls_registry: dict[str, type] = {}


def setup_extra_parser(parser):
    """Sets up extra parser arguments for CSV loading.

    Adds a `--fullscan` option to the parser, which is used by the `dump`
    function to determine if it should scan all rows to find all possible headers.

    Args:
        parser: The argparse parser instance.

    Returns:
        The parser instance with added arguments.
    """
    parser.add_argument(
        "--fullscan", action="store_true", help="full scan for guessing headers"
    )
    return parser


def load(
    fp,
    *,
    loader=None,
    delimiter: str = ",",
    errors=None,
    _registry=_cls_registry,
    create_reader_class=None,
    **kwargs,
):
    """Loads data from a CSV file-like object.

    It uses a custom DictReader that can handle errors by ignoring lines
    if `errors` is set to "ignore". It also performs type guessing on values.

    Args:
        fp: A file-like object supporting .read().
        loader: (Unused) The loader instance.
        delimiter: The delimiter character for the CSV file. Defaults to ",".
        errors: Error handling scheme. If "ignore", CSV parsing errors will be
                logged and the problematic line will be skipped.
        _registry: (Internal) A registry for caching DictReader classes.
        create_reader_class: (Internal) A function to create the DictReader class.
        **kwargs: Additional keyword arguments passed to the DictReader.

    Returns:
        An iterator of dictionaries, where each dictionary represents a row.
    """
    k = errors
    DictReader = _registry.get(k)
    if DictReader is None:
        DictReader = _registry[k] = (create_reader_class or _create_reader_class)(
            m.csv, k
        )
    reader = DictReader(fp, delimiter=delimiter, **kwargs) # Pass kwargs here
    return reader


def dump(
    rows, fp, *, delimiter: str = ",", sort_keys: bool = False, fullscan: bool = False
) -> None:
    """Dumps a list of dictionaries to a file-like object in CSV format.

    Args:
        rows: An iterable of dictionaries to dump. If a single dictionary or string
              is passed, it's wrapped in a list.
        fp: A file-like object supporting .write().
        delimiter: The delimiter character for the CSV file. Defaults to ",".
        sort_keys: If True, the CSV headers (dictionary keys) will be sorted.
                   Defaults to False.
        fullscan: If True, scans all rows to determine the complete set of headers.
                  If False (default), only the keys from the first row are used,
                  which is faster but may miss headers present only in later rows.
    """
    if not rows:
        return
    if hasattr(rows, "keys") or hasattr(rows, "join"): # handles single dict or string
        rows = [rows]

    itr = iter(rows)
    try:
        first_row = next(itr)
    except StopIteration: # empty iterator after handling single item case
        return
    scanned = [first_row]
    fields = list(first_row.keys())
    seen = set(fields)

    if fullscan:
        for row in itr: # itr continues from where next(itr) left off
            for k in row.keys():
                if k not in seen:
                    seen.add(k)
                    fields.append(k)
            scanned.append(row)
        # After fullscan, itr is exhausted, so we use 'scanned' for writerows
        itr_for_writing = iter(scanned)
    else:
        # If not fullscan, itr still has remaining items (if any)
        # We need to write the first_row (already in scanned) and then the rest of itr
        itr_for_writing = iter(scanned + list(itr))


    if sort_keys:
        fields = sorted(list(seen)) # Use 'seen' for sorted fields if fullscan, else 'fields'
    else:
        fields = list(fields) # Ensure it's the order from first row or appended order

    writer = m.csv.DictWriter(
        fp, fields, delimiter=delimiter, lineterminator="\r\n", quoting=m.csv.QUOTE_ALL
    )
    writer.writeheader()
    writer.writerows(itr_for_writing)


def _create_reader_class(csv_module, errors=None, retry: int = 10):
    """Creates a custom csv.DictReader class.

    This custom reader handles type guessing for cell values and provides
    an option to ignore lines with parsing errors.
    It also includes a workaround for Python versions older than 3.6.

    Args:
        csv_module: The csv module (passed as `m.csv`).
        errors: Error handling mode. If "ignore", parsing errors are logged
                and skipped up to `retry` times per problematic read attempt.
        retry: Number of retries for skipping lines when `errors="ignore"`.

    Returns:
        A specialized DictReader class.
    """
    if sys.version_info[:2] >= (3, 6):
        base_dict_reader = csv_module.DictReader
    else:
        # Custom DictReader for older Python versions to ensure make_dict is used
        # and to align behavior more closely with newer versions if possible.
        class OldPythonDictReader(csv_module.DictReader):
            def __next__(self):
                if self.line_num == 0:
                    # Used only for its side effect of initializing fieldnames.
                    _ = self.fieldnames # Ensure fieldnames are read
                row = next(self.reader)
                self.line_num = self.reader.line_num

                # Skip blank rows
                while row == []:
                    row = next(self.reader)

                # Use make_dict for consistency if available and appropriate
                d = make_dict(zip(self.fieldnames, row))

                len_fieldnames = len(self.fieldnames)
                len_row = len(row)

                if len_fieldnames < len_row:
                    d[self.restkey] = row[len_fieldnames:]
                elif len_fieldnames > len_row:
                    for key in self.fieldnames[len_row:]:
                        d[key] = self.restval
                return d
        base_dict_reader = OldPythonDictReader

    original_next = base_dict_reader.__next__

    if errors == "ignore":
        def __next__(self, current_retry=retry): # Renamed arg to avoid conflict
            try:
                d = original_next(self)
                return guess(d, mutable=True) # Type guess values
            except csv_module.Error as e:
                logger.info(
                    "line=%d CSV parsing error occurred, skipping. Error: %r", self.line_num +1, e
                ) # line_num might be 0-indexed from reader
                if current_retry <= 0:
                    raise
                # This recursive call might lead to deep stacks on many consecutive errors.
                # A loop-based approach or careful management of fp might be more robust.
                return self.__next__(current_retry=current_retry - 1)

        # To handle StopIteration correctly when retrying, especially if the error occurs on the last line
        # or if __next__ itself needs to advance the underlying reader upon error.
        # This simplified version assumes original_next advances the reader or error is fatal for the line.

    else: # errors is None or any other value, treat as strict
        def __next__(self, current_retry=None): # Added current_retry for signature consistency
            d = original_next(self)
            return guess(d, mutable=True) # Type guess values

    # Create a new class with the modified __next__
    # The name of the class is dynamic to reflect its configuration if needed,
    # or simply "CustomDictReader"
    custom_reader_name = f"CustomDictReader_{errors}" if errors else "CustomDictReader_strict"
    CustomDictReader = type(custom_reader_name, (base_dict_reader,), {"__next__": __next__})

    return CustomDictReader
