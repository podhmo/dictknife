import re


def normalize(name, ignore_rx=re.compile("[^0-9a-zA-Z_]+")):
    return ignore_rx.sub("", name.replace("-", "_"))


def snakecase(
    name,
    *,
    rx0=re.compile(r"(.)([A-Z][a-z]+)"),
    rx1=re.compile(r"([a-z0-9])([A-Z])"),
    separator="_",
    other="-",
):
    pattern = r"\1{}\2".format(separator)
    replaced = rx1.sub(pattern, rx0.sub(pattern, name)).lower()
    return replaced.replace(other, separator)


def kebabcase(
    name,
    *,
    rx0=re.compile(r"(.)([A-Z][a-z]+)"),
    rx1=re.compile(r"([a-z0-9])([A-Z])"),
    separator="-",
    other="_",
):
    pattern = r"\1{}\2".format(separator)
    replaced = rx1.sub(pattern, rx0.sub(pattern, name)).lower()
    return replaced.replace(other, separator)


def camelcase(name, *, soft: bool=True):
    if soft and name[0].isupper():
        return pascalcase(name)
    else:
        return untitleize(pascalcase(name))


def pascalcase(name, rx=re.compile(r"[\-_ ]")):
    return "".join(titleize(x) for x in rx.split(name))


def titleize(name):
    if not name:
        return name
    name = str(name)
    return "{}{}".format(name[0].upper(), name[1:])


def untitleize(name):
    if not name:
        return name
    return "{}{}".format(name[0].lower(), name[1:])
