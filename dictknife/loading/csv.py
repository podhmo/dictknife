import sys
from ._lazyimport import m
from dictknife.langhelpers import make_dict
from dictknife.guessing import guess
from logging import getLogger as get_logger

logger = get_logger()

_cls_registry = {}


def load(
    fp,
    *,
    loader=None,
    delimiter=",",
    errors=None,
    _registry=_cls_registry,
    create_reader_class=None,
    **kwargs
):
    k = errors
    DictReader = _registry.get(k)
    if DictReader is None:
        DictReader = _registry[k] = (create_reader_class or _create_reader_class)(m.csv, k)
    reader = DictReader(fp, delimiter=delimiter)
    return reader


def dump(rows, fp, *, delimiter=",", sort_keys=False):
    if not rows:
        return
    if hasattr(rows, "keys") or hasattr(rows, "join"):
        rows = [rows]  # string or dict

    itr = iter(rows)
    first_row = next(itr)
    fields = list(first_row.keys())
    if sort_keys:
        fields = sorted(fields)
    writer = m.csv.DictWriter(
        fp, fields, delimiter=delimiter, lineterminator="\r\n", quoting=m.csv.QUOTE_ALL
    )
    writer.writeheader()
    writer.writerow(first_row)
    writer.writerows(itr)


def _create_reader_class(csv, errors=None, retry=10):
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
                logger.info("line=%d errors is occured, skipping err=%r", self.line_num, e)
                if retry <= 0:
                    raise
                return self.__next__(retry=retry - 1)

        make_dictReader.__next__ = __next__
    else:

        def __next__(self):
            d = original_next(self)
            return guess(d, mutable=True)

        make_dictReader.__next__ = __next__
    return make_dictReader
