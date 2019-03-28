import shlex
import sys
from .guessing import guess
from .langhelpers import make_dict
from .accessing import Accessor


class _AccessorSupportList(Accessor):
    def __init__(self, make_dict=make_dict):
        self.make_dict = make_dict

    def assign(self, d, path, value):
        hist = [d]
        seen = []
        for name in path[:-1]:
            if name == "":
                if hasattr(d, "keys"):
                    hist[-2][seen[-1]] = [d]
                else:
                    d.append(self.make_dict())
                    d = d[-1]
            elif name.isdigit():
                if hasattr(d, "keys"):
                    d = hist[-2][seen[-1]] = []
                try:
                    d = d[int(name)]
                except IndexError:
                    p = hist[-2][seen[-1]]
                    for i in range(len(p), int(name) + 1):
                        p.append(self.make_dict())
                    d = p[int(name)]
            elif name.startswith("-") and name[1:].isdigit():
                d = d[int(name)]
            else:
                if name not in d:
                    d[name] = self.make_dict()
                d = d[name]
            hist.append(d)
            seen.append(name)

        name = path[-1]
        if name == "":
            if hasattr(d, "keys"):
                hist[-2][seen[-1]] = [value]
            else:
                d.append(value)
        elif name.isdigit():
            if hasattr(d, "keys"):
                d = hist[-2][seen[-1]] = []
            try:
                d[int(name)] = value
            except IndexError:
                for i in range(len(d), int(name) + 1):
                    d.append(self.make_dict())
                d[int(name)] = value
        else:
            d[name] = value

    def maybe_access(self, d, path):
        for name in path[:-1]:
            if name.isdigit() or (name.startswith("-") and name[1:].isdigit()):
                name = int(name)
            try:
                d = d[name]
            except KeyError:
                return None

        if not d:
            return None

        name = path[-1]
        if name.isdigit() or (name.startswith("-") and name[1:].isdigit()):
            try:
                return d[int(name)]
            except IndexError:
                return None
        return d.get(name)


def mkdict(
    line,
    *,
    separator="/",
    delimiter=";",
    accessor=_AccessorSupportList(make_dict),
    guess=guess
):
    tokens = iter(tokenize(line))
    return _mkdict(
        tokens, separator=separator, delimiter=delimiter, accessor=accessor, guess=guess
    )


def _mkdict(tokens, *, separator, delimiter, accessor, guess):
    L = []
    d = accessor.make_dict()
    variables = {}
    while True:
        try:
            tk = next(tokens)
            if tk == delimiter:
                L.append(d)
                d = accessor.make_dict()
                continue

            k = str(tk)
            v = next(tokens)

            if not hasattr(v, "encode"):
                pass
            elif v.startswith("&&"):  # escaped
                v = v[1:]
            elif v.startswith("&"):
                # reference:
                v = accessor.maybe_access(variables, v[1:].split(separator))

            if k.startswith("@@"):  # escaped
                accessor.assign(d, k[1:].split(separator), guess(v))
            elif k.startswith("@"):
                # assigning variable:
                accessor.assign(variables, k[1:].split(separator), guess(v))
            elif k.startswith(separator):
                if k == separator:
                    d[""] = guess(v)
                else:
                    if "" not in d:
                        d[""] = accessor.make_dict()
                    accessor.assign(d[""], k[1:].split(separator), guess(v))
            else:
                accessor.assign(d, k.split(separator), guess(v))
        except StopIteration:
            break

    if tk != delimiter:
        L.append(d)

    if len(L) == 1 and tk != delimiter:
        return L[0]
    return L


def tokenize(line):
    lexer = shlex.shlex(line, punctuation_chars=True)
    lexer.whitespace += "="
    for token in lexer:
        yield token.strip("""'"-""")


if sys.version_info[:2] < (3, 6):
    # monkey patch
    from io import StringIO
    from collections import deque

    def __init__(
        self, instream=None, infile=None, posix=False, punctuation_chars=False
    ):
        if isinstance(instream, str):
            instream = StringIO(instream)
        if instream is not None:
            self.instream = instream
            self.infile = infile
        else:
            self.instream = sys.stdin
            self.infile = None
        self.posix = posix
        if posix:
            self.eof = None
        else:
            self.eof = ""
        self.commenters = "#"
        self.wordchars = (
            "abcdfeghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        )
        if self.posix:
            self.wordchars += (
                "ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ" "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ"
            )
        self.whitespace = " \t\r\n"
        self.whitespace_split = False
        self.quotes = "'\""
        self.escape = "\\"
        self.escapedquotes = '"'
        self.state = " "
        self.pushback = deque()
        self.lineno = 1
        self.debug = 0
        self.token = ""
        self.filestack = deque()
        self.source = None
        if not punctuation_chars:
            punctuation_chars = ""
        elif punctuation_chars is True:
            punctuation_chars = "();<>|&"
        self.punctuation_chars = punctuation_chars
        if punctuation_chars:
            # _pushback_chars is a push back queue used by lookahead logic
            self._pushback_chars = deque()
            # these chars added because allowed in file names, args, wildcards
            self.wordchars += "~-./*?="
            # remove any punctuation chars from wordchars
            t = self.wordchars.maketrans(dict.fromkeys(punctuation_chars))
            self.wordchars = self.wordchars.translate(t)

    def read_token(self):
        quoted = False
        escapedstate = " "
        while True:
            if self.punctuation_chars and self._pushback_chars:
                nextchar = self._pushback_chars.pop()
            else:
                nextchar = self.instream.read(1)
            if nextchar == "\n":
                self.lineno += 1
            if self.debug >= 3:
                print("shlex: in state %r I see character: %r" % (self.state, nextchar))
            if self.state is None:
                self.token = ""  # past end of file
                break
            elif self.state == " ":
                if not nextchar:
                    self.state = None  # end of file
                    break
                elif nextchar in self.whitespace:
                    if self.debug >= 2:
                        print("shlex: I see whitespace in whitespace state")
                    if self.token or (self.posix and quoted):
                        break  # emit current token
                    else:
                        continue
                elif nextchar in self.commenters:
                    self.instream.readline()
                    self.lineno += 1
                elif self.posix and nextchar in self.escape:
                    escapedstate = "a"
                    self.state = nextchar
                elif nextchar in self.wordchars:
                    self.token = nextchar
                    self.state = "a"
                elif nextchar in self.punctuation_chars:
                    self.token = nextchar
                    self.state = "c"
                elif nextchar in self.quotes:
                    if not self.posix:
                        self.token = nextchar
                    self.state = nextchar
                elif self.whitespace_split:
                    self.token = nextchar
                    self.state = "a"
                else:
                    self.token = nextchar
                    if self.token or (self.posix and quoted):
                        break  # emit current token
                    else:
                        continue
            elif self.state in self.quotes:
                quoted = True
                if not nextchar:  # end of file
                    if self.debug >= 2:
                        print("shlex: I see EOF in quotes state")
                    # XXX what error should be raised here?
                    raise ValueError("No closing quotation")
                if nextchar == self.state:
                    if not self.posix:
                        self.token += nextchar
                        self.state = " "
                        break
                    else:
                        self.state = "a"
                elif (
                    self.posix
                    and nextchar in self.escape
                    and self.state in self.escapedquotes
                ):
                    escapedstate = self.state
                    self.state = nextchar
                else:
                    self.token += nextchar
            elif self.state in self.escape:
                if not nextchar:  # end of file
                    if self.debug >= 2:
                        print("shlex: I see EOF in escape state")
                    # XXX what error should be raised here?
                    raise ValueError("No escaped character")
                # In posix shells, only the quote itself or the escape
                # character may be escaped within quotes.
                if (
                    escapedstate in self.quotes
                    and nextchar != self.state
                    and nextchar != escapedstate
                ):
                    self.token += self.state
                self.token += nextchar
                self.state = escapedstate
            elif self.state in ("a", "c"):
                if not nextchar:
                    self.state = None  # end of file
                    break
                elif nextchar in self.whitespace:
                    if self.debug >= 2:
                        print("shlex: I see whitespace in word state")
                    self.state = " "
                    if self.token or (self.posix and quoted):
                        break  # emit current token
                    else:
                        continue
                elif nextchar in self.commenters:
                    self.instream.readline()
                    self.lineno += 1
                    if self.posix:
                        self.state = " "
                        if self.token or (self.posix and quoted):
                            break  # emit current token
                        else:
                            continue
                elif self.state == "c":
                    if nextchar in self.punctuation_chars:
                        self.token += nextchar
                    else:
                        if nextchar not in self.whitespace:
                            self._pushback_chars.append(nextchar)
                        self.state = " "
                        break
                elif self.posix and nextchar in self.quotes:
                    self.state = nextchar
                elif self.posix and nextchar in self.escape:
                    escapedstate = "a"
                    self.state = nextchar
                elif (
                    nextchar in self.wordchars
                    or nextchar in self.quotes
                    or self.whitespace_split
                ):
                    self.token += nextchar
                else:
                    if self.punctuation_chars:
                        self._pushback_chars.append(nextchar)
                    else:
                        self.pushback.appendleft(nextchar)
                    if self.debug >= 2:
                        print("shlex: I see punctuation in word state")
                    self.state = " "
                    if self.token or (self.posix and quoted):
                        break  # emit current token
                    else:
                        continue
        result = self.token
        self.token = ""
        if self.posix and not quoted and result == "":
            result = None
        if self.debug > 1:
            if result:
                print("shlex: raw token=" + repr(result))
            else:
                print("shlex: raw token=EOF")
        return result

    shlex.shlex.__init__ = __init__
    shlex.shlex.read_token = read_token
