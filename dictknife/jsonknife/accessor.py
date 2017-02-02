from dictknife import Accessor
from dictknife import LooseDictWalkingIterator


class JSONRefAccessor(object):
    def __init__(self):
        self.accessor = Accessor()
        self.ref_walking = LooseDictWalkingIterator(["$ref"])

    def access(self, fulldata, ref):
        # not support external file
        if not ref.startswith("#/"):
            raise ValueError("invalid ref {!r}".format(ref))
        path = ref[2:].split("/")
        return self.accessor.access(fulldata, path)

    def expand(self, fulldata, d):
        if "$ref" in d:
            original = self.access(fulldata, d["$ref"])
            d.pop("$ref")
            d.update(self.expand(fulldata, original))
            return d
        else:
            for path, sd in self.ref_walking.iterate(d):
                self.expand(fulldata, sd)
            return d

    def extract(self, fulldata, ref):
        return self.expand(fulldata, self.access(fulldata, ref))
