import sys
import logging
import os.path
from functools import partial
from collections import OrderedDict
from dictknife import DictWalker
from dictknife.langhelpers import reify, pairrsplit
from dictknife import Accessor
from dictknife import deepmerge
from .accessor import CachedItemAccessor

logger = logging.getLogger(__name__)


class Bundler(object):
    def __init__(self, resolver, strict=False):
        self.resolver = resolver
        self.accessor = CachedItemAccessor(resolver)
        self.item_map = OrderedDict()  # localref -> item
        self.strict = strict

    def build_localref_fixer(self, doc):
        if "components" in doc or doc.get("openapi", "").startswith("3"):
            prefixes = ["definitions"]
            return SwaggerLocalrefFixer(prefixes, "components/schemas")
        else:
            prefixes = set(["definitions", "paths", "responses", "parameters"])
            return SwaggerLocalrefFixer(prefixes, "definitions")

    def build_fix_conflict(self):
        if self.strict:
            return error_on_conflict
        else:
            return partial(fix_on_conflict, self.item_map)

    def bundle(self, doc=None):
        doc = doc or self.resolver.doc

        localref_fixer = self.build_localref_fixer(doc)
        fix_conflict = self.build_fix_conflict()
        fixref_walker = FixRefWalker(self.accessor, localref_fixer, fix_conflict)
        fixref_walker.walk(doc, self.item_map)

        emitter = Emitter(self.accessor, self.item_map)
        return emitter.emit(self.resolver, doc)


class FixRefWalker:
    def __init__(self, accessor, localref_fixer, fix_conflict):
        self.accessor = accessor
        self.localref_fixer = localref_fixer
        self.fix_conflict = fix_conflict
        self.ref_walking = DictWalker(["$ref"])

    def walk(self, doc, item_map):
        for path, sd in self.ref_walking.iterate(doc):
            try:
                item = self.accessor.access(sd["$ref"])
                item = self.localref_fixer.fix_localref(path, item)
                if item.localref not in item_map:
                    item_map[item.localref] = item
                    self.walk(item.data, item_map)
                if item.globalref != item_map[item.localref].globalref:
                    newitem = self.fix_conflict(item_map[item.localref], item)
                    self.walk(newitem.data, item_map)
            except RuntimeError:
                raise
            except Exception as e:
                raise RuntimeError("{} (where={})".format(e, self.accessor.resolver.name))
            finally:
                self.accessor.pop_stack()


class Emitter(object):
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
        d = OrderedDict()
        for path, sd in self.ref_walking.iterate(doc):
            self.replace_ref(resolver, sd)

        d = deepmerge(d, doc)
        for name, item in self.item_map.items():
            if name == "":
                continue
            data = item.data
            for path, sd in self.ref_walking.iterate(data):
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
            logger.debug("fix ref: %r -> %r (where=%r)", sd["$ref"], new_ref, resolver.filename)
            sd["$ref"] = new_ref


class SwaggerLocalrefFixer(object):  # todo: rename
    def __init__(self, prefixes, definition_prefix):
        self.prefixes = prefixes
        self.definition_prefix = definition_prefix

    def guess_prefix(self, path, item):
        for node in reversed(path):
            if node in self.prefixes:
                return node
            if node == "schema":
                return self.definition_prefix
        logger.info("fix localref: prefix is not found from %s", path)
        return self.definition_prefix

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

        if prefix not in self.prefixes:
            prefix = self.guess_prefix(path, item)

        if not name:
            name = self.guess_name(path, item)

        # xxx: side effect
        item.localref = "{}/{}".format(prefix, name)
        # print("changes: {} -> {}".format(localref, item.localref), file=sys.stderr)
        return item


def error_on_conflict(item_map, olditem, newitem):
    msg = "conficted. {!r} <-> {!r}".format(olditem.globalref, newitem.globalref)
    raise RuntimeError(msg)


def fix_on_conflict(item_map, olditem, newitem):
    msg = "conficted. {!r} <-> {!r}".format(olditem.globalref, newitem.globalref)
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    i = 1
    while True:
        new_localref = "{}{}".format(newitem.localref, i)
        if new_localref not in item_map:
            newitem.localref = new_localref
            break
        i += 1
    item_map[newitem.localref] = newitem
    return newitem
