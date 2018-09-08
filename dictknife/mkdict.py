import shlex
from .guessing import guess
from .accessing import Accessor
from .langhelpers import make_dict


def mkdict(line, *, separator="/", accessor=Accessor(make_dict), guess=guess):
    d = make_dict()
    tokens = iter(tokenize(line))
    return _mkdict(d, tokens, separator=separator, accessor=accessor, guess=guess)


def _mkdict(d, tokens, *, separator, accessor, guess):
    while True:
        try:
            k = next(tokens)
            v = next(tokens)
            accessor.assign(d, k.split(separator), guess(v))
        except StopIteration:
            break
    return d


def tokenize(line):
    lexer = shlex.shlex(line, punctuation_chars=True)
    lexer.whitespace += "="
    for token in lexer:
        yield token.strip("""'"-""")
