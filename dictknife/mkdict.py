import shlex


def mkdict(xs):
    pass


def parse(line):
    lexer = shlex.shlex(line, punctuation_chars=True)
    lexer.whitespace += "="
    for token in lexer:
        yield token.strip("""'"-""")
