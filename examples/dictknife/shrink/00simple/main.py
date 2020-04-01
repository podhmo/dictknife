from dictknife import loading
from dictknife.transform import shrink
from handofcats import as_command


@as_command
def run(filename: str) -> None:
    d = loading.loadfile(filename)
    format = loading.guess_format(filename)

    r = shrink(d)
    loading.dumpfile(r, format=format)
