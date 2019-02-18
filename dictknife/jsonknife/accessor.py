from dictknife import Accessor
from dictknife.langhelpers import as_jsonpointer


class CachedItem:
    def __init__(self, file, localref, globalref, resolver, data):
        self.file = file
        self.localref = localref
        self.globalref = globalref
        self.resolver = resolver
        self.data = data


def path_to_json_pointer(path):
    return "/".join((as_jsonpointer(x) for x in path))


def normalize_json_pointer(ref):
    if "~" not in ref:
        return ref
    return ref.replace("~1", "/").replace("~0", "~")


def access_by_json_pointer(doc, query, *, accessor=Accessor(), guess=False):
    if query == "":
        return doc
    try:
        path = [normalize_json_pointer(p) for p in query.lstrip("#/").split("/")]
        if guess:
            path = [(int(p) if p.isdigit() else p) for p in path]
        return accessor.access(doc, path)
    except KeyError:
        raise KeyError(query)


def assign_by_json_pointer(doc, query, v, *, accessor=Accessor(), guess=False):
    if query == "":
        return doc
    try:
        path = [normalize_json_pointer(p) for p in query.lstrip("#/").split("/")]
        if guess:
            path = [(int(p) if p.isdigit() else p) for p in path]
        return accessor.assign(doc, path, v)
    except KeyError:
        raise KeyError(query)


class StackedAccessor(object):
    def __init__(self, resolver, accessor=Accessor()):
        self.stack = [resolver]
        self.accessor = accessor

    @property
    def resolver(self):
        return self.stack[-1]

    def access(self, ref, format=None):
        subresolver, pointer = self.resolver.resolve(ref, format=format)
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
