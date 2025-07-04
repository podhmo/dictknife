import sys
import logging
import os.path
from collections import deque

from dictknife import loading
from dictknife.walkers import DictWalker
from dictknife.langhelpers import reify, pairrsplit

from .accessor import AccessingMixin
from .relpath import normpath
from ._wrapped_exception import wrap_exception

logger = logging.getLogger("jsonknife.resolver")


class OneDocResolver(AccessingMixin):
    def __init__(self, doc, *, name: str="*root*", onload=None, format=None) -> None:
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


class ExternalFileResolver(AccessingMixin):
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
        format=None,
        wrap_exception=wrap_exception,
    ) -> None:
        self.rawfilename = rawfilename or filename
        self.filename = os.path.normpath(os.path.abspath(str(filename)))
        self.cache = {} if cache is None else cache  # filename -> resolver
        self.loader = loader or loading
        self.history = history or [ROOT]
        self.onload = onload
        self.format = format
        self.wrap_exception = wrap_exception
        if doc is not None:
            self.doc = doc
            if self.onload is not None:
                self.onload(doc, self)

    def __repr__(self) -> str:
        return "<FileResolver {!r}>".format(self.filename)

    @property
    def name(self):
        return self.filename

    @reify
    def doc(self):
        try:
            logger.debug(
                "load file[%s]: %r (where=%r)",
                len(self.history),
                self.rawfilename,
                self.history[-1].filename,
            )
            self.doc = self.loader.loadfile(self.filename, format=self.format)

            if self.onload is not None:
                self.onload(self.doc, self)
            return self.doc
        except Exception as e:
            exc = self.wrap_exception(e, where=self.name)
            raise exc from None

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
            wrap_exception=self.wrap_exception,
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
        return (
            self.resolve_subresolver(fullpath, rawfilename=filepath, format=format),
            query,
        )

    def resolve_subresolver(self, filename, rawfilename=None, format=None):
        if filename in self.cache:
            cached = self.cache[filename]
            if cached.history[-1].filename == self.filename:
                return cached
            else:
                return self.new(
                    filename, doc=cached.doc, rawfilename=rawfilename, format=format
                )
        subresolver = self.cache[filename] = self.new(
            filename, rawfilename=rawfilename, format=format
        )
        return subresolver

    def path_list(self, filename: str) -> list:
        resolver = self.cache[filename]
        return [*resolver.history[1:], resolver]


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
        resolver = ExternalFileResolver(
            filename, loader=loader, onload=onload, format=format
        )
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
