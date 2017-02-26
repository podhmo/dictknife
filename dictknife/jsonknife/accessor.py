from dictknife.langhelpers import reify
from dictknife import Accessor
from dictknife import LooseDictWalkingIterator


class OnefileOnlyQueryResolver(object):
    def resolve(self, query):
        # not support external file
        if not query.startswith("#/"):
            raise ValueError("invalid query {!r}".format(query))
        return query[1:]


class JSONRefAccessor(object):
    def __init__(self, accessor=Accessor(), resolver=OnefileOnlyQueryResolver()):
        self.accessor = accessor
        self.resolver = resolver

    @reify
    def ref_walking(self):
        return LooseDictWalkingIterator(["$ref"])

    def access(self, doc, query):
        pointer = self.resolver.resolve(query)
        return self.access_json_pointer(doc, pointer)

    def access_json_pointer(self, doc, query):
        if query == "":
            return doc
        path = [p.replace("~1", "/").replace("~0", "~") for p in query[1:].split("/")]
        return self.accessor.access(doc, path)

    def expand(self, doc, subpart):
        if "$ref" in subpart:
            original = self.access(doc, subpart["$ref"])
            subpart.pop("$ref")
            subpart.update(self.expand(doc, original))
            return subpart
        else:
            for path, sd in self.ref_walking.iterate(subpart):
                self.expand(doc, sd)
            return subpart
