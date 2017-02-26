from dictknife import Accessor
from dictknife import LooseDictWalkingIterator
from dictknife.langhelpers import reify
from .resolver import OneDocResolver
from .accessor import access_by_json_pointer


class Expander(object):
    def __init__(self, resolver, accessor=Accessor()):
        self.accessor = accessor
        self.resolver = resolver

    @classmethod
    def from_doc(cls, doc):
        return cls(resolver=OneDocResolver(doc))

    @property
    def doc(self):
        return self.resolver.doc

    @reify
    def ref_walking(self):
        return LooseDictWalkingIterator(["$ref"])

    def expand(self, resolver=None):
        return self.expand_subpart(self.doc, resolver=resolver)

    def access(self, ref, resolver=None):
        resolver = resolver or self.resolver
        subresolver, pointer = resolver.resolve(ref)
        return access_by_json_pointer(subresolver.doc, pointer, accessor=self.accessor)

    def expand_subpart(self, subpart, resolver=None):
        resolver = resolver or self.resolver
        if "$ref" in subpart:
            subresolver, pointer = resolver.resolve(subpart["$ref"])
            original = access_by_json_pointer(subresolver.doc, pointer, accessor=self.accessor)
            subpart.pop("$ref")
            subpart.update(self.expand_subpart(original, resolver=subresolver))
            return subpart
        else:
            for path, sd in self.ref_walking.iterate(subpart):
                self.expand_subpart(sd, resolver=resolver)
            return subpart
