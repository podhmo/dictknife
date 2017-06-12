from functools import wraps
from dictknife.langhelpers import reify


class LazyImporter:
    def __init__(self):
        self.module = None

    @reify
    def import_(self):
        raise RuntimeError("import function is not set")

    def setup(self, fn):
        self.import_ = fn
        return fn

    def use(self, fn):
        @wraps(fn)
        def _use(*args, **kwargs):
            if self.module is None:
                self.module = self.import_()
            return fn(self.module, *args, **kwargs)

        return _use
