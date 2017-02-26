from dictknife import Accessor
from dictknife import LooseDictWalkingIterator


class JSONRefAccessor(object):
    def __init__(self):
        self.accessor = Accessor()
        self.ref_walking = LooseDictWalkingIterator(["$ref"])

    def access(self, doc, query):
        # not support external file
        if not query.startswith("#/"):
            raise ValueError("invalid query {!r}".format(query))
        return self._access(doc, query[2:])

    def _access(self, doc, query):
        if query == "":
            return doc
        path = [p.replace("~1", "/").replace("~0", "~") for p in query[1:].split("/")]
        return self.accessor.access(doc, path)

    def expand(self, doc, d):
        if "$ref" in d:
            original = self.access(doc, d["$ref"])
            d.pop("$ref")
            d.update(self.expand(doc, original))
            return d
        else:
            for path, sd in self.ref_walking.iterate(d):
                self.expand(doc, sd)
            return d

    def extract(self, doc, ref):
        return self.expand(doc, self.access(doc, ref))
