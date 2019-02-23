import logging
from dictknife import Accessor
from dictknife.langhelpers import as_jsonpointer, as_path_node

logger = logging.getLogger(__name__)


class AccessorMixin:
    # need self.doc
    def assign(self, path, value, *, doc=None, a=Accessor()):
        if doc is None:
            doc = self.doc
        return a.assign(doc, path, value)

    def access(self, path, *, doc=None, a=Accessor()):
        if doc is None:
            doc = self.doc
        return a.access(doc, path)

    def maybe_access(self, path, *, doc=None, a=Accessor()):
        if doc is None:
            doc = self.doc
        return a.maybe_access(doc, path)

    def access_by_json_pointer(self, jsonref, *, doc=None, guess=True):
        if doc is None:
            doc = self.doc
        return access_by_json_pointer(doc, jsonref, guess=guess)

    def assign_by_json_pointer(self, jsonref, value, *, doc=None, guess=True):
        if doc is None:
            doc = self.doc
        return assign_by_json_pointer(doc, jsonref, value, guess=guess)


class CachedItem:
    def __init__(self, file, localref, globalref, resolver, data):
        self.file = file
        self.localref = localref
        self.globalref = globalref
        self.resolver = resolver
        self.data = data


def path_to_json_pointer(path):
    return "/".join((as_jsonpointer(x) for x in path))


def json_pointer_to_path(ref):
    return [as_path_node(p) for p in ref.lstrip("#/").split("/")]


def access_by_json_pointer(doc, query, *, accessor=Accessor(), guess=False):
    if query == "":
        return doc
    try:
        path = json_pointer_to_path(query)
        return accessor.access(doc, path)
    except KeyError:
        if guess:
            new_path = []
            has_integer = False
            for p in path:
                if p.isdigit():
                    new_path.append(int(p))
                    has_integer = True
                else:
                    new_path.append(p)
            if has_integer:
                logger.debug("jsonpointer: %r is notfound. including integer?", query)
                try:
                    return accessor.access(doc, new_path)
                except KeyError:
                    pass
        raise KeyError(query)


def assign_by_json_pointer(doc, query, v, *, accessor=Accessor(), guess=False):
    if query == "":
        return doc
    try:
        path = json_pointer_to_path(query)
        return accessor.assign(doc, path, v)
    except KeyError:
        if guess:
            new_path = []
            has_integer = False
            for p in path:
                if p.isdigit():
                    new_path.append(int(p))
                    has_integer = True
                else:
                    new_path.append(p)

            if has_integer:
                logger.debug("jsonpointer: %r is notfound. including integer?", query)
                try:
                    return accessor.assign(doc, new_path, v)
                except KeyError:
                    pass
        raise KeyError(query)


class StackedAccessor(object):
    def __init__(self, resolver, accessor=Accessor()):
        self.stack = [resolver]
        self.accessor = accessor

    @property
    def resolver(self):
        return self.stack[-1]

    def access(self, ref, format=None):
        try:
            subresolver, pointer = self.resolver.resolve(ref, format=format)
            self.push_stack(subresolver)
            return self._access(subresolver, pointer)
        except Exception as e:
            where = None
            if len(self.stack) > 1:
                where = self.stack[-2].name
            raise e.__class__("{} (where={})".format(e, where)).with_traceback(
                e.__traceback__
            ) from None

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
