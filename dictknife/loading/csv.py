from ._lazyimport import m
from collections import OrderedDict
from dictknife.guessing import guess


def load(fp, *, loader=None, delimiter=",", **kwargs):
    class OrderedDictReader(m.csv.DictReader):
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
            d = OrderedDict(zip(self.fieldnames, row))
            lf = len(self.fieldnames)
            lr = len(row)
            if lf < lr:
                d[self.restkey] = row[lf:]
            elif lf > lr:
                for key in self.fieldnames[lr:]:
                    d[key] = self.restval
            return guess(d, mutable=True)

    reader = OrderedDictReader(fp, delimiter=delimiter)
    return reader


def dump(rows, fp, *, delimiter=","):
    if not rows:
        return
    if hasattr(rows, "keys") or hasattr(rows, "join"):
        rows = [rows]  # string or dict

    itr = iter(rows)
    first_row = next(itr)
    fields = list(first_row.keys())
    writer = m.csv.DictWriter(
        fp, fields, delimiter=delimiter, lineterminator="\r\n", quoting=m.csv.QUOTE_ALL
    )
    writer.writeheader()
    writer.writerow(first_row)
    writer.writerows(itr)
