from dictknife import LooseDictWalkingIterator
from dictknife.langhelpers import reify
from .accessor import StackedAccessor


class Expander(object):
    def __init__(self, resolver):
        self.accessor = StackedAccessor(resolver)
        self.resolver = resolver

    @reify
    def ref_walking(self):
        return LooseDictWalkingIterator(["$ref"])

    def access(self, ref):
        return self.accessor.access_and_stacked(ref)

    def expand(self):
        return self.expand_subpart(self.resolver.doc)

    def expand_subpart(self, subpart, resolver=None):
        resolver = resolver or self.resolver
        if "$ref" in subpart:
            try:
                original = self.accessor.access_and_stacked(subpart["$ref"])
                subpart.pop("$ref")
                subpart.update(self.expand_subpart(original, resolver=self.accessor.resolver))
            finally:
                self.accessor.pop_stack()
            return subpart
        else:
            for path, sd in self.ref_walking.iterate(subpart):
                self.expand_subpart(sd, resolver=resolver)
            return subpart
