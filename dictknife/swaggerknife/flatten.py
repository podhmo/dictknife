from collections import OrderedDict
from dictknife.langhelpers import reify
from dictknife import DictWalker
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

    def flatten(self, d):
        for name, sd in d.items():
            self.replace(sd, name)
        return self.doc


def flatten(doc, *, position="#/definitions"):
    flattener = Flattener(doc, position=position)
    w = DictWalker(flattener.path)
    for path, d in w.walk(doc):
        for name, sd in d[path[-1]].items():
            flattener.replace(sd, name)
    return doc
