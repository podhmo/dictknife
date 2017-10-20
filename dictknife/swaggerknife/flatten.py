from collections import OrderedDict
from dictknife.langhelpers import reify
from dictknife.jsonknife.lifting import Extractor, LiftingState


class Flattener:
    def __init__(self, doc=None, *, position="#/definitions", state_factory=LiftingState):
        self.doc = doc or OrderedDict()
        self.path = position.lstrip("#/").rstrip("/").split("/")
        self.ref_format = "#/{path}/{{}}".format(path="/".join(self.path))
        self.state_factory = state_factory

    @reify
    def extractor(self):
        return Extractor(self.return_definition)

    @reify
    def definitions(self):
        defs = self.doc
        for name in self.path:
            if name not in defs:
                defs[name] = OrderedDict()
            defs = defs[name]
        return defs

    def return_definition(self, definition, fullname, typ="object"):
        return {"$ref": self.ref_format.format(fullname)}

    def emit_definition(self, name, definition):
        self.definitions[name] = definition

    def replace(self, data, name):
        state = self.state_factory([name])
        r = self.extractor.extract(data, state)
        for name, definition in reversed(r.items()):
            self.emit_definition(name, definition)
        return self.doc


def flatten(data):
    if "definitions" not in data:
        return data
    flattener = Flattener(data, position="definitions")
    defs = data["definitions"]
    for name in list(defs.keys()):
        flattener.replace(defs[name], name)
    return data
