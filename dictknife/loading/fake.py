class FakeModule:
    def __init__(self, name, msg):
        self.name = name
        self.msg = msg

    def load(self, *args, **kwargs):
        raise RuntimeError(self.msg)

    def dump(self, *args, **kwargs):
        raise RuntimeError(self.msg)

    def setup(self, *args, **kwargs):
        pass
