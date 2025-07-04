import logging
import os.path
from collections import defaultdict
from functools import partial
from typing import TYPE_CHECKING, cast

from dictknife.langhelpers import make_dict, titleize, reify, pairrsplit
from dictknife import DictWalker
from dictknife import Accessor
from dictknife import deepmerge

from .relpath import relpath
from .accessor import CachedItemAccessor
from .accessor import is_ref

if TYPE_CHECKING:
    from .accessor import CachedItem


logger = logging.getLogger("jsonknife.bundler")


def create_scanner_factory_from_flavor(flavor: str):
    # thid is temporary, implementation
    if flavor == "openapiv2":
        return partial(
            Scanner, localref_fixer=LocalrefFixer(default_position="definitions")
        )
    elif flavor == "openapiv3":
        return partial(
            Scanner, localref_fixer=LocalrefFixer(default_position="components/schemas")
        )
    else:
        raise ValueError(
            "unexpected flavor {!r}, available flavors are ['openapiv2', 'openapiv3']".format(
                flavor
            )
        )


class Bundler:
    def __init__(self, resolver, strict: bool=False, *, scanner_factory=None) -> None:
        self.resolver = resolver
        self.accessor = CachedItemAccessor(resolver)
        self.item_map: dict[str, "CachedItem"] = make_dict()  # localref -> item
        self.strict = strict
        self._scanner_factory = scanner_factory or Scanner

    @reify
    def scanner(self):
        return self._scanner_factory(self.accessor, self.item_map, strict=self.strict)

    @reify
    def emitter(self):
        return Emitter(self.accessor, self.item_map)

    def bundle(self, doc=None):
        doc = doc or self.resolver.doc
        conflicted = self.scanner.scan(doc)
        return self.emitter.emit(self.resolver, doc, conflicted=conflicted)


class Scanner:
    def __init__(self, accessor, item_map, strict: bool=False, localref_fixer=None) -> None:
        self.accessor = accessor
        self.item_map = item_map
        self.strict = strict
        self.seen: set[str] = set()

        # todo: rename
        self.localref_fixer = localref_fixer or LocalrefFixer(
            default_position="definitions"
        )

    @reify
    def ref_walking(self):
        return DictWalker([is_ref])

    @reify
    def conflict_fixer(self):  # todo: rename
        return SimpleConflictFixer(self.item_map, strict=self.strict)

    def scan(self, doc):
        conflicted: dict[str, list] = defaultdict(list)
        self._scan_refs(doc, conflicted=conflicted)
        self._scan_toplevel(doc, conflicted=conflicted)
        return conflicted

    def _scan_toplevel(self, doc, *, conflicted) -> None:
        assert len(self.accessor.stack) == 1
        for name in list(self.item_map.keys()):
            try:
                toplevel_item = self.accessor.access("#/" + name)
                if "$ref" in toplevel_item.data:
                    continue
                ref_item = self.item_map[name]
                if ref_item == toplevel_item:
                    continue

                self.item_map[name] = toplevel_item
                new_item = self.conflict_fixer.fix_conflict(toplevel_item, ref_item)
                if new_item is None:
                    continue
                conflicted[name].append(new_item)
            except KeyError:
                continue
            finally:
                self.accessor.pop_stack()
        assert len(self.accessor.stack) == 1

    def _scan_refs(self, doc, *, conflicted) -> None:
        for path, sd in self.ref_walking.iterate(doc):
            try:
                item = self.accessor.access(sd["$ref"])
                if item in self.seen:
                    continue
                self.seen.add(item)

                item = self.localref_fixer.fix_localref(path, item)
                if item.localref not in self.item_map:
                    if not (
                        "$ref" in item.data
                        and sd["$ref"].startswith("#/")
                        and item.data["$ref"].endswith(sd["$ref"])
                    ):
                        self.item_map[item.localref] = item
                    self._scan_refs(doc=item.data, conflicted=conflicted)
                if item.globalref != self.item_map[item.localref].globalref:
                    newitem = self.conflict_fixer.fix_conflict(
                        self.item_map[item.localref], item
                    )
                    if newitem is None:
                        continue
                    conflicted[sd["$ref"]].append(newitem)
                    self._scan_refs(doc=newitem.data, conflicted=conflicted)
            finally:
                self.accessor.pop_stack()


class Emitter:
    def __init__(self, accessor, item_map) -> None:
        self.raw_accessor = Accessor()
        self.accessor = accessor
        self.item_map = item_map

    @reify
    def ref_walking(self):
        return DictWalker([is_ref])

    def get_item_by_globalref(self, globalref):
        return self.accessor.cache[globalref]

    def get_item_by_localref(self, localref):
        return self.item_map[localref]

    def emit(self, resolver, doc, *, conflicted):
        # side effect
        d: dict[str, object] = make_dict()
        for path, sd in self.ref_walking.iterate(doc):
            self.replace_ref(resolver, sd)

        d = deepmerge(d, doc)
        for name, item in self.item_map.items():
            if name == "":
                continue
            data = item.data
            # replace: <file.yaml>#/<ref> -> #/<ref>
            for path, sd in self.ref_walking.iterate(data):
                if not sd["$ref"].startswith("#/"):
                    self.replace_ref(item.resolver, sd)
                if sd["$ref"] in conflicted:
                    self.replace_ref(item.resolver, sd)
            self.raw_accessor.assign(d, name.split("/"), data)

        # adhoc paths support
        will_removes = set()
        paths = cast(dict, d.get("paths", {}))
        for path, sub in list(paths.items()):
            if "$ref" in sub and sub["$ref"].startswith("#/"):
                related_path = tuple(sub["$ref"][2:].split("/"))
                paths[path] = self.raw_accessor.access(d, related_path).copy()
                will_removes.add(related_path)
        for related_path in will_removes:
            self.raw_accessor.maybe_remove(d, related_path)
        return d

    def replace_ref(self, resolver, sd) -> None:
        filename, _, pointer = resolver.resolve_pathset(sd["$ref"])
        related = self.get_item_by_globalref((filename, pointer))
        new_ref = "#/{}".format(related.localref)
        if sd["$ref"] != new_ref:
            logger.debug(
                "fix ref: %r -> %r (where=%r)", sd["$ref"], new_ref, resolver.filename
            )
            sd["$ref"] = new_ref


class LocalrefFixer:  # todo: rename
    def __init__(self, *, default_position: str) -> None:
        self.default_position = default_position

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
            # xxx: "definitions" or "components/schemas"?
            prefix = self.default_position
        if not name:
            name = self.guess_name(path, item)

        # xxx: side effect
        item.localref = "{}/{}".format(prefix, name)
        if item.localref != localref:
            logger.info("fix localref %s -> %s", localref, item.localref)
        return item


class SimpleConflictFixer:  # todo: rename
    def __init__(self, item_map, strict: bool=False) -> None:
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
        if self.strict:
            raise RuntimeError(
                "conficted. %r <-> %r" % (olditem.globalref, newitem.globalref)
            )
        logger.info("conficted. %r <-> %r", olditem.globalref, newitem.globalref)

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
