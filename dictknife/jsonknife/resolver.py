import sys
import logging
import os.path
from collections import deque
from .. import loading
from ..walkers import DictWalker
from ..langhelpers import reify, pairrsplit
from ..accessing import Accessor
from .accessor import (
    access_by_json_pointer,
    assign_by_json_pointer,
)
from .relpath import normpath

logger = logging.getLogger("jsonknife.resolver")


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

    def access_by_json_pointer(self, jsonref, *, doc=None):
        if doc is None:
            doc = self.doc
        return access_by_json_pointer(doc, jsonref)

    def assign_by_json_pointer(self, jsonref, value, *, doc=None):
        if doc is None:
            doc = self.doc
        return assign_by_json_pointer(doc, jsonref, value)


class OneDocResolver(AccessorMixin):
    def __init__(self, doc, *, name="*root*", onload=None, format=None):
        self.doc = doc
        self.name = name
        self.onload = onload
        if self.onload is not None:
            self.onload(self.doc, self)
        self.format = format

    def resolve(self, query, format=None):
        # not support external file
        if not query.startswith("#/"):
            raise ValueError("invalid query {!r}".format(query))
        return self, query[1:]


class ExternalFileResolver(AccessorMixin):
    def __init__(
        self,
        filename,
        *,
        cache=None,
        loader=None,
        history=None,
        doc=None,
        rawfilename=None,
        onload=None,
        format=None
    ):
        self.rawfilename = rawfilename or filename
        self.filename = os.path.normpath(os.path.abspath(filename))
        self.cache = cache or {}  # filename -> resolver
        self.loader = loader or loading
        self.history = history or [ROOT]
        self.onload = onload
        self.format = format
        if doc is not None:
            self.doc = doc
            if self.onload is not None:
                self.onload(doc, self)

    def __repr__(self):
        return "<FileResolver {!r}>".format(self.filename)

    @property
    def name(self):
        return self.filename

    @reify
    def doc(self):
        logger.debug(
            "load file[%s]: %r (where=%r)", len(self.history), self.rawfilename,
            self.history[-1].filename
        )
        with open(self.filename) as rf:
            self.doc = self.loader.load(rf, format=self.format)
        if self.onload is not None:
            self.onload(self.doc, self)
        return self.doc

    def new(self, filename, doc=None, rawfilename=None, format=None):
        rawfilename = rawfilename or filename
        history = self.history[:]
        history.append(self)
        return self.__class__(
            filename,
            cache=self.cache,
            loader=self.loader,
            history=history,
            doc=doc,
            rawfilename=rawfilename,
            onload=self.onload,
            format=format,
        )

    def resolve_pathset(self, query):  # todo: refactoring
        filepath, query = pairrsplit(query, "#")
        if filepath == "":
            return self.filename, self.filename, query
        fullpath = normpath(filepath, where=os.path.dirname(self.filename))
        return fullpath, filepath, query

    def resolve(self, query, format=None):
        if query.startswith("#"):
            return self, query[1:]
        if "#" not in query:
            query = query + "#"

        fullpath, filepath, query = self.resolve_pathset(query)
        return self.resolve_subresolver(fullpath, rawfilename=filepath, format=format), query

    def resolve_subresolver(self, filename, rawfilename=None, format=None):
        if filename in self.cache:
            cached = self.cache[filename]
            if cached.history[-1].filename == self.filename:
                return cached
            else:
                return self.new(filename, doc=cached.doc, rawfilename=rawfilename, format=format)
        subresolver = self.cache[filename] = self.new(
            filename, rawfilename=rawfilename, format=format
        )
        return subresolver


class ROOT:
    filename = "*root*"
    rawfilename = "*root*"
    history = []


def get_resolver(filename, *, loader=loading, doc=None, onload=None, format=None):
    if filename is None:
        if doc is None:
            doc = doc or loading.load(sys.stdin)
        return OneDocResolver(doc, onload=onload, format=format)
    else:
        resolver = ExternalFileResolver(filename, loader=loader, onload=onload, format=format)
        if doc:
            resolver.doc = doc
        return resolver


# for backward compatibility
get_resolver_from_filename = get_resolver


def build_subset(resolver, ref):
    subset = {}

    refs = deque([ref])
    seen = set()
    while refs:
        ref = refs.popleft()
        if ref in seen:
            continue
        seen.add(ref)
        ob = resolver.access_by_json_pointer(ref)
        resolver.assign_by_json_pointer(ref, ob, doc=subset)
        for path, sd in DictWalker(["$ref"]).walk(ob):
            # xxx:
            if sd["$ref"].startswith("#/"):
                refs.append(sd["$ref"][1:])
    return subset
