from dictknife import LooseDictWalkingIterator
from dictknife.langhelpers import reify
from .accessor import StackedAccessor
from dictknife.contexts import PathContext


class SelfContext(PathContext):
    def __call__(self, walker, fn, value):
        return fn(self, value)


class Expander(object):
    def __init__(self, resolver):
        self.accessor = StackedAccessor(resolver)
        self.resolver = resolver

    @reify
    def ref_walking(self):
        return LooseDictWalkingIterator(["$ref"], context_factory=SelfContext)

    def access(self, ref):
        return self.accessor.access_and_stacked(ref)

    def expand(self):
        return self.expand_subpart(self.resolver.doc)

    def expand_subpart(self, subpart, resolver=None, ctx=None):
        resolver = resolver or self.resolver

        if "$ref" in subpart:
            try:
                original = self.accessor.access_and_stacked(subpart["$ref"])
                ref = subpart.pop("$ref")
                new_subpart = self.expand_subpart(original, resolver=self.accessor.resolver, ctx=ctx)
                # for circular reference
                if id(new_subpart) in ctx._arrived:
                    subpart["$ref"] = ref
                else:
                    subpart.update(new_subpart)
            finally:
                self.accessor.pop_stack()
            return subpart
        else:
            for ctx, sd in self.ref_walking.iterate(subpart):
                self.expand_subpart(sd, resolver=resolver, ctx=ctx)
            return subpart
