from ._lazyimport import m


def load(fp, *, loader=None, delimiter=",", **kwargs):
    reader = m.csv.DictReader(fp, delimiter=delimiter)
    return reader


def dump(rows, fp, *, delimiter=","):
    if not rows:
        return
    if hasattr(rows, "keys") or hasattr(rows, "join"):
        rows = [rows]  # string or dict

    itr = iter(rows)
    first_row = next(itr)
    fields = list(first_row.keys())
    writer = m.csv.DictWriter(fp, fields, delimiter=delimiter, lineterminator="\r\n")
    writer.writeheader()
    writer.writerow(first_row)
    writer.writerows(itr)
