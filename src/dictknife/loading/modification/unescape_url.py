from io import StringIO
import urllib.parse as parselib
from dictknife.loading.modification import use, is_used


def setup(dispatcher) -> None:
    if is_used(dispatcher, __name__):
        return
    use(dispatcher, __name__)

    def wrap(load_fn):
        def call(stream, *args, **kwargs):
            s = stream.read()
            s = parselib.unquote_plus(s).strip()
            if s.startswith("'") and s.endswith("'"):
                s = s[1:-1]
            elif s.startswith('"') and s.endswith('"'):
                s = s[1:-1]
            s = s.strip()
            rf = StringIO(s)
            rf.name = getattr(stream, "name", "(unknown)")
            return load_fn(rf, *args, **kwargs)

        return call

    for k in list(dispatcher.loader.fn_map.keys()):
        dispatcher.loader.fn_map[k] = wrap(dispatcher.loader.fn_map[k])
