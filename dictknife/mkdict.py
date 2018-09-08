import shlex
from .guessing import guess
from .accessing import Accessor
from .langhelpers import make_dict


def mkdict(line, *, separator="/", delimiter=";", accessor=Accessor(make_dict), guess=guess):
    tokens = iter(tokenize(line))
    return _mkdict(
        tokens,
        separator=separator,
        delimiter=delimiter,
        accessor=accessor,
        guess=guess,
    )


def _mkdict(tokens, *, separator, delimiter, accessor, guess):
    L = []
    d = accessor.make_dict()
    while True:
        try:
            tk = next(tokens)
            if tk == delimiter:
                L.append(d)
                d = accessor.make_dict()
                continue
            k = tk
            v = next(tokens)
            accessor.assign(d, k.split(separator), guess(v))
        except StopIteration:
            break

    if tk != delimiter:
        L.append(d)

    if len(L) == 1:
        return L[0]
    return L


def tokenize(line):
    lexer = shlex.shlex(line, punctuation_chars=True)
    lexer.whitespace += "="
    for token in lexer:
        yield token.strip("""'"-""")
