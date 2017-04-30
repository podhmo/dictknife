from dictknife import Accessor
from namedlist import namedlist
CachedItem = namedlist("CachedItem", "file, localref, globalref, resolver, data")


def normalize_json_pointer(ref):
    if "~" not in ref:
        return ref
    return ref.replace("~1", "/").replace("~0", "~")


def access_by_json_pointer(doc, query, accessor=Accessor()):
    if query == "":
        return doc
    try:
        path = [normalize_json_pointer(p) for p in query[1:].split("/")]
        return accessor.access(doc, path)
    except KeyError:
        raise KeyError(query)


class StackedAccessor(object):
    def __init__(self, resolver, accessor=Accessor()):
        self.stack = [resolver]
        self.accessor = accessor

    @property
    def resolver(self):
        return self.stack[-1]

    def access(self, ref):
        subresolver, pointer = self.resolver.resolve(ref)
        self.push_stack(subresolver)
        return self._access(subresolver, pointer)

    def _access(self, subresolver, pointer):
        return access_by_json_pointer(subresolver.doc, pointer, accessor=self.accessor)

    def pop_stack(self):
        return self.stack.pop()

    def push_stack(self, resolver):
        return self.stack.append(resolver)


class CachedItemAccessor(StackedAccessor):
    def __init__(self, resolver):
        super().__init__(resolver)
        self.cache = {}  # globalref -> item

    def _access(self, subresolver, pointer):
        globalref = (subresolver.filename, pointer)
        item = self.cache.get(globalref)
        if item is not None:
            return item
        data = super()._access(subresolver, pointer)
        item = CachedItem(
            file=subresolver.filename,
            resolver=subresolver,
            localref=pointer,
            globalref=globalref,
            data=data,
        )
        self.cache[globalref] = item
        return item
