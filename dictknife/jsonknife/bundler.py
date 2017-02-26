import sys
from collections import OrderedDict
from namedlist import namedlist
from dictknife import LooseDictWalkingIterator
from dictknife.langhelpers import reify
from dictknife import Accessor
from dictknife import deepmerge
from .accessor import StackedAccessor


CacheItem = namedlist("CacheItem", "file, localref, globalref, resolver, data")


class Bundler(object):
    def __init__(self, resolver, strict=False):
        self.raw_accessor = Accessor()
        self.accessor = CachedItemAccessor(resolver)
        self.resolver = resolver
        self.item_map = {}  # localref -> item
        self.strict = strict

    def get_item_by_globalref(self, globalref):
        return self.accessor.cache[globalref]

    def get_item_by_localref(self, localref):
        return self.item_map[localref]

    @reify
    def ref_walking(self):
        return LooseDictWalkingIterator(["$ref"])

    def fix_localref_item(self, path, item):
        # xxx: side effect
        if not item.localref:
            localref = "/{}".format("/".join(path))
            item.localref = localref.replace("/properties/", "_").replace("/items/", "_item").replace("/$ref", "")  # xxx:
        if item.localref.startswith("/"):
            item.localref = item.localref[1:]
        return item

    def fix_conflict_item(self, olditem, newitem):
        msg = "conficted. {!r} <-> {!r}".format(olditem.globalref, newitem.globalref)
        if self.strict:
            raise RuntimeError(msg)
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        i = 1
        while True:
            new_localref = "{}{}".format(newitem.localref, i)
            if new_localref not in self.item_map:
                newitem.localref = new_localref
                break
            i += 1
        self.item_map[newitem.localref] = newitem
        self.scan(doc=newitem.data)

    def scan(self, doc):
        for path, sd in self.ref_walking.iterate(doc):
            try:
                item = self.accessor.access_and_stacked(sd["$ref"])
                item = self.fix_localref_item(path, item)
                if item.localref not in self.item_map:
                    self.item_map[item.localref] = item
                    self.scan(doc=item.data)
                if item.globalref != self.item_map[item.localref].globalref:
                    self.fix_conflict_item(self.item_map[item.localref], item)
            finally:
                self.accessor.pop_stack()

    def bundle(self, doc=None):
        doc = doc or self.resolver.doc
        self.scan(doc)
        # side effect
        d = OrderedDict()
        for path, sd in self.ref_walking.iterate(doc):
            filename, _, pointer = self.resolver.resolve_pathset(sd["$ref"])
            related = self.get_item_by_globalref((filename, pointer))
            sd["$ref"] = "#/{}".format(related.localref)

        d = deepmerge(d, doc)
        for name, item in self.item_map.items():
            if name == "":
                continue
            data = item.data
            for path, sd in self.ref_walking.iterate(data):
                filename, _, pointer = item.resolver.resolve_pathset(sd["$ref"])
                related = self.get_item_by_globalref((filename, pointer))
                sd["$ref"] = "#/{}".format(related.localref)
            self.raw_accessor.assign(d, name.split("/"), data)
        return d


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
        item = CacheItem(
            file=subresolver.filename,
            resolver=subresolver,
            localref=pointer,
            globalref=globalref,
            data=data,
        )
        self.cache[globalref] = item
        return item
