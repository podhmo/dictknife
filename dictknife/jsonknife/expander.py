from dictknife import DictWalker
from dictknife.langhelpers import reify
from .accessor import StackedAccessor


def detect_circur_reference(doc, d) -> bool:
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
    def __init__(self, resolver) -> None:
        self.accessor = StackedAccessor(resolver)
        self.resolver = resolver

    @reify
    def ref_walking(self):
        return DictWalker(["$ref"])

    def access(self, ref):
        if not ref:
            return self.resolver.doc
        return self.accessor.access(ref)

    def expand(self, *, _expect_stack_size=1):
        doc = self.expand_subpart(self.resolver.doc)
        assert len(self.accessor.stack) == _expect_stack_size
        return doc

    def expand_subpart(self, subpart, resolver=None, ctx=None):
        resolver = resolver or self.resolver

        if "$ref" in subpart:
            original = self.accessor.access(subpart["$ref"])
            ref = subpart.pop("$ref")
            new_subpart = self.expand_subpart(
                original, resolver=self.accessor.resolver, ctx=ctx
            )
            if detect_circur_reference(subpart, new_subpart):
                subpart["$ref"] = ref
            else:
                subpart.update(new_subpart)
            self.accessor.pop_stack()
            return subpart
        else:
            for path, sd in self.ref_walking.iterate(subpart):
                self.expand_subpart(sd, resolver=resolver, ctx=ctx)
            return subpart
