from dictknife import LooseDictWalkingIterator
from dictknife.langhelpers import reify
from .accessor import StackedAccessor


def detect_circur_reference(doc, d):
    if id(doc) == id(d):
        return True
    elif isinstance(d, dict):
        for v in d.values():
            if detect_circur_reference(doc, v):
                return True
    elif isinstance(d, list):
        for x in d:
            if detect_circur_reference(doc, x):
                return True
    else:
        return False


class Expander(object):
    def __init__(self, resolver):
        self.accessor = StackedAccessor(resolver)
        self.resolver = resolver

    @reify
    def ref_walking(self):
        return LooseDictWalkingIterator(["$ref"])

    def access(self, ref):
        return self.accessor.access(ref)

    def expand(self):
        return self.expand_subpart(self.resolver.doc)

    def expand_subpart(self, subpart, resolver=None, ctx=None):
        resolver = resolver or self.resolver

        if "$ref" in subpart:
            try:
                original = self.accessor.access(subpart["$ref"])
                ref = subpart.pop("$ref")
                new_subpart = self.expand_subpart(original, resolver=self.accessor.resolver, ctx=ctx)
                if detect_circur_reference(subpart, new_subpart):
                    subpart["$ref"] = ref
                else:
                    subpart.update(new_subpart)
            finally:
                self.accessor.pop_stack()
            return subpart
        else:
            for path, sd in self.ref_walking.iterate(subpart):
                self.expand_subpart(sd, resolver=resolver, ctx=ctx)
            return subpart
