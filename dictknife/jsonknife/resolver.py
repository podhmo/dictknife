import sys
import logging
import os.path
from .. import loading
from ..langhelpers import reify, pairrsplit
from .relpath import normpath
from .accessor import (
    access_by_json_pointer,
    assign_by_json_pointer,
)

logger = logging.getLogger("jsonknife.resolver")


class AccessorMixin:
    def access(self, doc, jsonref):
        return access_by_json_pointer(doc, jsonref)

    def assign(self, doc, jsonref, value):
        return assign_by_json_pointer(doc, jsonref, value)


class OneDocResolver(AccessorMixin):
    def __init__(self, doc, name="*root*", onload=None):
        self.doc = doc
        self.name = name
        self.onload = onload
        if self.onload is not None:
            self.onload(self.doc, self)

    def resolve(self, query, format=None):
        # not support external file
        if not query.startswith("#/"):
            raise ValueError("invalid query {!r}".format(query))
        return self, query[1:]


class ExternalFileResolver(AccessorMixin):
    def __init__(
        self,
        filename,
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


def get_resolver(filename, loader=loading, doc=None, onload=None):
    if filename is None:
        doc = doc or loading.load(sys.stdin)
        return OneDocResolver(doc, onload=onload)
    else:
        resolver = ExternalFileResolver(filename, loader=loader, onload=onload)
        if doc:
            resolver.doc = doc
        return resolver


# for backward compatibility
get_resolver_from_filename = get_resolver
