import sys
from ._lazyimport import m
from dictknife.langhelpers import make_dict
from dictknife.guessing import guess
from logging import getLogger as get_logger
from typing import Any, Type

logger = get_logger(__name__)

_cls_registry: dict[str, type] = {}


def setup_extra_parser(parser):
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
    k = errors
    DictReader = _registry.get(k)
    if DictReader is None:
        DictReader = _registry[k] = (create_reader_class or _create_reader_class)(
            m.csv, k
        )
    reader = DictReader(fp, delimiter=delimiter)
    return reader


def dump(
    rows, fp, *, delimiter: str = ",", sort_keys: bool = False, fullscan: bool = False
) -> None:
    if not rows:
        return
    if hasattr(rows, "keys") or hasattr(rows, "join"):
        rows = [rows]  # string or dict

    itr = iter(rows)
    scanned = [next(itr)]
    fields = list(scanned[0].keys())
    seen = set(fields)

    if fullscan:
        for row in itr:
            for k in row.keys():
                if k not in seen:
                    seen.add(k)
                    fields.append(k)
            scanned.append(row)
    if sort_keys:
        fields = sorted(fields)
    fields = list(fields)
    writer = m.csv.DictWriter(
        fp, fields, delimiter=delimiter, lineterminator="\r\n", quoting=m.csv.QUOTE_ALL
    )
    writer.writeheader()
    writer.writerows(scanned)
    writer.writerows(itr)


def _create_reader_class(csv, errors=None, retry: int = 10):
    if sys.version_info[:2] >= (3, 6):
        make_dictReader = csv.DictReader
    else:

        class make_dictReader(csv.DictReader):
            def __next__(self):
                if self.line_num == 0:
                    # Used only for its side effect.
                    self.fieldnames
                row = next(self.reader)
                self.line_num = self.reader.line_num

                # unlike the basic reader, we prefer not to return blanks,
                # because we will typically wind up with a dict full of None
                # values
                while row == []:
                    row = next(self.reader)
                d = make_dict(zip(self.fieldnames, row))
                lf = len(self.fieldnames)
                lr = len(row)
                if lf < lr:
                    d[self.restkey] = row[lf:]
                elif lf > lr:
                    for key in self.fieldnames[lr:]:
                        d[key] = self.restval
                return d

    original_next = make_dictReader.__next__
    if errors == "ignore":

        def __next__(self, retry=retry):
            try:
                d = original_next(self)
                return guess(d, mutable=True)
            except csv.Error as e:
                logger.info(
                    "line=%d errors is occured, skipping err=%r", self.line_num, e
                )
                if retry <= 0:
                    raise
                return self.__next__(retry=retry - 1)

        make_dictReader.__next__ = __next__
    else:

        def __next__(self, retry=None):
            d = original_next(self)
            return guess(d, mutable=True)

        make_dictReader.__next__ = __next__
    return make_dictReader
