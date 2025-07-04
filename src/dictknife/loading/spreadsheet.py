import re
import contextlib
from collections import namedtuple
from ._lazyimport import m
from .raw import setup_extra_parser  # noqa

_loader = None
Guessed = namedtuple("Guessed", "spreadsheet_id, range, sheet_id")
"""Represents the parsed components of a Google Sheet URL or pattern.

Attributes:
    spreadsheet_id (str): The ID of the Google Spreadsheet.
    range (str | None): The specific range within the sheet (e.g., "Sheet1!A1:B2").
    sheet_id (str | None): The GID of the sheet.
"""


def guess(
    pattern: str, *, sheet_rx=re.compile("/spreadsheets/d/([a-zA-Z0-9-_]+)")
) -> Guessed:
    """Parses a Google Spreadsheet URL or a shorthand pattern to extract spreadsheet ID, range, and sheet GID.

    Supports two main patterns:
    1. Full HTTPS URL: e.g., "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=SHEET_GID"
       or with a range query parameter: "...?ranges=Sheet1!A1:C3"
    2. Shorthand ID and optional range: e.g., "SPREADSHEET_ID" or "SPREADSHEET_ID#/Sheet1!A1:C3"

    Args:
        pattern: The URL or shorthand pattern string for the Google Sheet.
        sheet_rx: A compiled regular expression to find the spreadsheet ID in a URL path.

    Returns:
        A Guessed namedtuple containing `spreadsheet_id`, `range`, and `sheet_id`.
        `range` and `sheet_id` can be None if not present in the pattern.

    Raises:
        ValueError: If the pattern is a URL but the spreadsheet ID cannot be extracted.
    """
    if not pattern.startswith("http") or "://" not in pattern:
        # Shorthand pattern: "SPREADSHEET_ID" or "SPREADSHEET_ID#/sheet_name!A1:B2"
        parts = pattern.split("#/", 1)
        spreadsheet_id = parts[0]
        range_value = parts[1] if len(parts) > 1 else None
        return Guessed(spreadsheet_id=spreadsheet_id, range=range_value, sheet_id=None)

    # Full URL pattern
    import urllib.parse as p # Lazy import for a standard library module

    parsed_url = p.urlparse(pattern)

    match = sheet_rx.search(parsed_url.path)
    if match is None:
        raise ValueError(f"Could not extract spreadsheet ID from URL path: {parsed_url.path}")
    spreadsheet_id = match.group(1)

    query_params = p.parse_qs(parsed_url.query)
    range_value = query_params.get("ranges", [None])[0] # Get first range if multiple, or None

    sheet_id_from_fragment = None
    if parsed_url.fragment and parsed_url.fragment.startswith("gid="):
        sheet_id_from_fragment = parsed_url.fragment[4:] # Strip "gid="

    return Guessed(spreadsheet_id=spreadsheet_id, range=range_value, sheet_id=sheet_id_from_fragment)


def load(pattern: str, *, errors=None, loader=None, **kwargs):
    """Loads data from a Google Spreadsheet specified by a URL or pattern.

    This function requires the `google-api-python-client` and `google-auth-oauthlib`
    packages, and proper authentication for Google Sheets API.
    For installation details, see the `Loader` class documentation or the project's README.

    The `pattern` is first parsed by the `guess` function to extract spreadsheet ID,
    range, and sheet GID. Then, it uses a lazily initialized `gsuite.Loader`
    to fetch the data.

    Args:
        pattern: The URL or shorthand pattern for the Google Sheet.
                 (e.g., "https://docs.google.com/spreadsheets/d/ID/edit#gid=0" or "ID#/Sheet1!A1:B2")
        errors: (Unused) Error handling scheme, kept for API consistency.
        loader: (Optional) An instance of `gsuite.Loader`. If None, a global instance
                is used/created.
        **kwargs: Additional keyword arguments (currently unused by this loader but
                  kept for API consistency).

    Returns:
        The data loaded from the Google Spreadsheet, typically a list of lists or list of dicts
        depending on the underlying `gsuite.Loader` implementation.
    """
    global _loader
    # Use the provided loader if available, otherwise fall back to the global _loader.
    current_loader = loader or _loader
    if current_loader is None:
        _loader = m.gsuite.Loader()
        current_loader = _loader

    guessed_params = guess(pattern)
    return current_loader.load_sheet(guessed_params)


def dump(rows, fp, *, sort_keys: bool = False):
    """Dumping data to a Google Spreadsheet is not implemented.

    Args:
        rows: Data to dump.
        fp: File-like object (irrelevant for this loader).
        sort_keys: Whether to sort keys (irrelevant).

    Raises:
        NotImplementedError: Always, as this functionality is not available.
    """
    raise NotImplementedError("Dumping to Google Spreadsheet is not supported.")


@contextlib.contextmanager
def not_open(path: str, encoding=None, errors=None):
    """A context manager that doesn't actually open a file, but yields the path itself.

    This is used by the `dictknife` loading mechanism when a custom opener is
    provided for a format. For spreadsheets, the 'path' is the URL or pattern,
    which is directly consumed by the `load` function, not opened as a local file.

    Args:
        path: The path (URL or pattern string) to the spreadsheet.
        encoding: (Unused) Encoding, kept for API consistency.
        errors: (Unused) Error handling, kept for API consistency.

    Yields:
        The path string, stripped of leading/trailing whitespace.
    """
    yield path.strip()
