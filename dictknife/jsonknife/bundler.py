import sys
import logging
import os.path
from dictknife.langhelpers import make_dict, titleize
from dictknife import DictWalker
from dictknife.langhelpers import reify, pairrsplit
from dictknife import Accessor
from dictknife import deepmerge
from .relpath import relpath
from .accessor import CachedItemAccessor

logger = logging.getLogger("jsonknife.bundler")


class Bundler:
    def __init__(self, resolver, strict=False):
        self.resolver = resolver
        self.accessor = CachedItemAccessor(resolver)
        self.item_map = make_dict()  # localref -> item
        self.strict = strict

    @reify
    def scanner(self):
        return Scanner(self.accessor, self.item_map, strict=self.strict)

    @reify
    def emitter(self):
        return Emitter(self.accessor, self.item_map)

    def bundle(self, doc=None):
        doc = doc or self.resolver.doc
        self.scanner.scan(doc)
        return self.emitter.emit(self.resolver, doc)


class Scanner:
    def __init__(self, accessor, item_map, strict=False):
        self.accessor = accessor
        self.item_map = item_map
        self.strict = strict

    @reify
    def ref_walking(self):
        return DictWalker(["$ref"])

    @reify
    def conflict_fixer(self):  # todo: rename
        return SimpleConflictFixer(self.item_map, strict=self.strict)

    @reify
    def localref_fixer(self):  # todo: rename
        return LocalrefFixer()

    def scan(self, doc):
        for path, sd in self.ref_walking.iterate(doc):
            try:
                item = self.accessor.access(sd["$ref"])
                item = self.localref_fixer.fix_localref(path, item)
                if item.localref not in self.item_map:
                    self.item_map[item.localref] = item
                    self.scan(doc=item.data)
                if item.globalref != self.item_map[item.localref].globalref:
                    newitem = self.conflict_fixer.fix_conflict(
                        self.item_map[item.localref], item
                    )
                    if newitem is None:
                        continue
                    self.scan(doc=newitem.data)
            finally:
                self.accessor.pop_stack()


class Emitter:
    def __init__(self, accessor, item_map):
        self.raw_accessor = Accessor()
        self.accessor = accessor
        self.item_map = item_map

    @reify
    def ref_walking(self):
        return DictWalker(["$ref"])

    def get_item_by_globalref(self, globalref):
        return self.accessor.cache[globalref]

    def get_item_by_localref(self, localref):
        return self.item_map[localref]

    def emit(self, resolver, doc):
        # side effect
        d = make_dict()
        for path, sd in self.ref_walking.iterate(doc):
            self.replace_ref(resolver, sd)

        d = deepmerge(d, doc)
        for name, item in self.item_map.items():
            if name == "":
                continue
            data = item.data
            # replace: <file.yaml>#/<ref> -> #/<ref>
            for path, sd in self.ref_walking.iterate(data):
                if sd["$ref"].startswith("#/"):
                    continue
                self.replace_ref(item.resolver, sd)
            self.raw_accessor.assign(d, name.split("/"), data)

        # adhoc paths support
        will_removes = set()
        paths = d.get("paths") or {}
        for path, sub in list(paths.items()):
            if "$ref" in sub and sub["$ref"].startswith("#/"):
                related_path = tuple(sub["$ref"][2:].split("/"))
                paths[path] = self.raw_accessor.access(d, related_path).copy()
                will_removes.add(related_path)
        for related_path in will_removes:
            self.raw_accessor.maybe_remove(d, related_path)
        return d

    def replace_ref(self, resolver, sd):
        filename, _, pointer = resolver.resolve_pathset(sd["$ref"])
        related = self.get_item_by_globalref((filename, pointer))
        new_ref = "#/{}".format(related.localref)
        if sd["$ref"] != new_ref:
            logger.debug(
                "fix ref: %r -> %r (where=%r)", sd["$ref"], new_ref, resolver.filename
            )
            sd["$ref"] = new_ref


class LocalrefFixer:  # todo: rename
    def guess_name(self, path, item):
        name = pairrsplit(item.globalref[1], "/")[1]
        if name:
            return name
        return os.path.splitext(pairrsplit(item.globalref[0], "/")[1])[0]

    def fix_localref(self, path, item):
        localref = item.localref
        if localref.startswith("/"):
            localref = localref[1:]

        prefix, name = pairrsplit(localref, "/")
        if not prefix:
            prefix = "definitions"  # xxx:
        if not name:
            name = self.guess_name(path, item)

        # xxx: side effect
        item.localref = "{}/{}".format(prefix, name)
        if item.localref != localref:
            logger.info("fix localref %s -> %s", localref, item.localref)
        return item


class SimpleConflictFixer:  # todo: rename
    def __init__(self, item_map, strict=False):
        self.item_map = item_map
        self.strict = strict

    def is_same_item(self, olditem, newitem):
        if not ("$ref" in newitem.data and len(newitem.data) == 1):
            return False
        filename, ref = pairrsplit(newitem.data["$ref"], "#/")
        return olditem.localref == ref and olditem.globalref[0] == relpath(
            filename, where=newitem.globalref[0]
        )

    def fix_conflict(self, olditem, newitem):
        if self.is_same_item(olditem, newitem):
            return None
        if self.is_same_item(newitem, olditem):
            self.item_map[newitem.localref] = newitem
            return None

        msg = "conficted. {!r} <-> {!r}".format(olditem.globalref, newitem.globalref)
        if self.strict:
            raise RuntimeError(msg)
        print(msg, file=sys.stderr)

        if olditem.globalref[0] != newitem.globalref[0]:
            dirpath, name = pairrsplit(newitem.localref, "/")
            prefix = os.path.splitext(pairrsplit(newitem.globalref[0], "/")[1])[0]
            newitem.localref = "{}/{}{}".format(dirpath, prefix, titleize(name))
        else:
            i = 1
            while True:
                new_localref = "{}{}".format(newitem.localref, i)
                if new_localref not in self.item_map:
                    newitem.localref = new_localref
                    break
                i += 1
        self.item_map[newitem.localref] = newitem
        return newitem
