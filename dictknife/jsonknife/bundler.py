import sys
import logging
import os.path
from collections import OrderedDict
from namedlist import namedlist
from dictknife import LooseDictWalkingIterator
from dictknife.langhelpers import reify, pairrsplit
from dictknife import Accessor
from dictknife import deepmerge
from .accessor import StackedAccessor


logger = logging.getLogger("jsonknife.bundler")
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

    def fix_localref_item(self, path, item, prefixes=set(["definitions", "paths", "responses", "parameters"])):
        localref = item.localref
        if localref.startswith("/"):
            localref = localref[1:]
        prefix, name = pairrsplit(localref, "/")

        if prefix not in prefixes:
            found = None
            for node in reversed(path):
                if node in prefixes:
                    found = node
                    break
                if node == "schema":
                    found = "definitions"
                    break
            if found is None:
                logger.info("fix localref: prefix is not found from %s", path)
                found = "definitions"

            prefix = found

        if not name:
            name = pairrsplit(item.globalref[1], "/")[1]
            if not name:
                name = os.path.splitext(pairrsplit(item.globalref[0], "/")[1])[0]

        # xxx: side effect
        item.localref = "{}/{}".format(prefix, name)
        # print("changes: {} -> {}".format(localref, item.localref), file=sys.stderr)
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

    def fix_ref(self, resolver, sd):
        filename, _, pointer = resolver.resolve_pathset(sd["$ref"])
        related = self.get_item_by_globalref((filename, pointer))
        new_ref = "#/{}".format(related.localref)
        logger.debug("fix ref: %r -> %r (where=%r)", sd["$ref"], new_ref, resolver.filename)
        sd["$ref"] = new_ref

    def bundle(self, doc=None):
        doc = doc or self.resolver.doc
        self.scan(doc)
        # side effect
        d = OrderedDict()
        for path, sd in self.ref_walking.iterate(doc):
            self.fix_ref(self.resolver, sd)

        d = deepmerge(d, doc)
        for name, item in self.item_map.items():
            if name == "":
                continue
            data = item.data
            for path, sd in self.ref_walking.iterate(data):
                self.fix_ref(item.resolver, sd)
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
