import re
import contextlib
from collections import namedtuple
from ._lazyimport import m
from .raw import setup_extra_parser  # noqa

_loader = None
Guessed = namedtuple("Guessed", "spreadsheet_id, range, sheet_id")


def guess(
    pattern: str, *, sheet_rx=re.compile("/spreadsheets/d/([a-zA-Z0-9-_]+)")
) -> Guessed:
    if not pattern.startswith("http") or "://" not in pattern:
        # like 1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps#/sheet1!A1:B2
        splitted = pattern.split("#/", 1)
        range_value = None
        if len(splitted) > 1:
            range_value = splitted[1]
        return Guessed(spreadsheet_id=splitted[0], range=range_value, sheet_id=None)

    # like  https://docs.google.com/spreadsheets/d/1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps/edit#gid=0
    import urllib.parse as p

    parsed = p.urlparse(pattern)

    m = sheet_rx.search(parsed.path)
    assert m is not None
    spreadsheet_id = m.group(1)

    range_value = None
    if parsed.query:
        qd = p.parse_qs(parsed.query)
        if "ranges" in qd:
            range_value = qd["ranges"][0]
    sheet_id = None
    if parsed.fragment:
        sheet_id = parsed.fragment.replace("gid=", "")
    return Guessed(spreadsheet_id=spreadsheet_id, range=range_value, sheet_id=sheet_id)


def load(pattern: str, *, errors=None, loader=None, **kwargs):
    global _loader
    loader = loader or _loader
    if _loader is None:
        _loader = m.gsuite.Loader()
    guessed = guess(pattern)
    return _loader.load_sheet(guessed)


def dump(rows, fp, *, sort_keys: bool=False):
    raise NotImplementedError("><")


@contextlib.contextmanager
def not_open(path, encoding=None, errors=None):
    yield path.strip()
