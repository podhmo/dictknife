from dictknife import loading
from dictknife.accessing import ImmutableModifier
from handofcats import as_command

# todo: random select
# todo: cont suffix for list


def shrink(d, *, max_of_string_length=100, cont_suffix="...", max_of_list_length=3):
    modifier = ImmutableModifier()

    def _map(d):
        if isinstance(d, (list, tuple)):
            xs = d
            if len(xs) > max_of_list_length:
                xs = xs[:max_of_list_length]
            return modifier.modify_list(_map, xs)
        elif hasattr(d, "keys"):
            return modifier.modify_dict(_map, d)
        elif isinstance(d, str):
            s = d
            if len(s) > max_of_string_length:
                s = s[:max_of_string_length] + cont_suffix
            return s
        else:
            return d

    return _map(d)


@as_command
def run(filename: str) -> None:
    d = loading.loadfile(filename)
    format = loading.guess_format(filename)

    r = shrink(d)
    loading.dumpfile(r, format=format)
