import os.path
import contextlib
import logging
import tempfile
import shutil
from collections import ChainMap

from dictknife.jsonknife.bundler import Scanner, CachedItemAccessor
from dictknife.langhelpers import make_dict, reify
from dictknife.jsonknife import json_pointer_to_path
from dictknife.diff import diff
from dictknife import loading

logger = logging.getLogger(__name__)


class _Empty:
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v


class Migration:
    def __init__(
        self, resolver, *, make_dict=make_dict, dump_options=None, transform=None
    ):
        self.resolver = resolver
        self.item_map = make_dict()
        self.make_dict = make_dict
        self.dump_options = dump_options or {}
        self._transform = transform

    def transform(self, data):
        if self._transform is None:
            return data
        return self._transform(data)

    @reify
    def differ(self):
        return _Differ(make_dict=self.make_dict)

    @reify
    def updater(self):
        return _Updater(self.resolver, self.item_map, make_dict=self.make_dict)

    def _prepare(self, *, doc, where):
        logger.debug("prepare (where=%s)", where)
        accessor = CachedItemAccessor(self.resolver)
        scanner = Scanner(accessor, self.item_map, strict=True)
        scanner.scan(self.resolver.doc)

    @contextlib.contextmanager
    def _migrate_dryrun_and_diff(self, doc, *, where=None):
        where = where or os.getcwd()
        doc = doc or self.resolver.doc
        self._prepare(doc=doc, where=where)

        yield self.updater

        for r in self.updater.resolvers:
            is_first = True
            for line in self.differ.diff(r, where=where):
                if is_first:
                    logger.info(
                        "diff is found %s", os.path.relpath(r.filename, start=where)
                    )
                    is_first = False
                print(line)

    @contextlib.contextmanager
    def _migrate(self, doc=None, *, where=None, savedir=None):
        where = where or os.getcwd()
        doc = doc or self.resolver.doc
        self._prepare(doc=doc, where=where)
        yield self.updater

        for r in self.updater.resolvers:
            relpath = os.path.relpath(r.filename, start=where)
            savepath = r.filename
            if savedir:
                savepath = os.path.relpath(
                    os.path.abspath(r.filename).replace(where, savedir), start=where
                )

            diff = "\n".join(self.differ.diff(r, where=where))
            if not diff:
                if savedir is None:
                    logger.debug("skip %s", relpath)
                else:
                    logger.info("copy %s -> %s", relpath, (savepath or relpath))
                    try:
                        shutil.copy(r.filename, savepath)
                    except FileNotFoundError:
                        os.makedirs(os.path.dirname(savepath))
                        shutil.copy(r.filename, savepath)
                continue

            logger.info("update %s -> %s", relpath, (savepath or relpath))
            loading.dumpfile(
                self.transform(self.differ.after_data(r.doc)),
                savepath,
                **self.dump_options
            )

    def migrate(
        self,
        doc=None,
        *,
        dry_run=False,
        where=None,
        inplace=False,
        savedir=None,
        keep=False
    ):
        logger.info(
            "migrate (dry_run=%r, inplace=%r, where=%r)", dry_run, inplace, where
        )
        if dry_run:
            return self._migrate_dryrun_and_diff(doc=doc, where=where)

        @contextlib.contextmanager
        def _migrate():
            nonlocal where
            nonlocal savedir

            where = where or os.getcwd()
            if inplace:
                savedir = None
            elif savedir is None:
                savedir = os.path.abspath(
                    tempfile.mkdtemp(prefix="migration-", dir=where)
                )  # xxx
            try:
                with self._migrate(doc=doc, where=where, savedir=savedir) as u:
                    yield u
            except Exception as e:
                if not keep and savedir:
                    logger.info("rollback. remove %s", savedir)
                    shutil.rmtree(savedir)
                raise
            return savedir

        return _migrate()


class _Differ:
    def __init__(self, *, make_dict=make_dict):
        self.make_dict = make_dict

    def diff(self, r, *, where):
        filename = os.path.relpath(r.name, start=where)
        before = self.before_data(r.doc)
        after = self.after_data(r.doc)
        yield from diff(
            before,
            after,
            fromfile="before:{filename}".format(filename=filename),
            tofile=" after:{filename}".format(filename=filename),
        )

    def before_data(self, d):
        if hasattr(d, "parents"):
            r = self.make_dict()
            for k, v in d.parents.items():
                r[k] = self.before_data(v)
            return r
        elif hasattr(d, "keys"):
            r = self.make_dict()
            for k, v in d.items():
                r[k] = self.before_data(v)
            return r
        elif isinstance(d, (list, tuple)):
            return [self.before_data(x) for x in d]
        else:
            return d.v if isinstance(d, _Empty) else d

    def after_data(self, d):
        if hasattr(d, "keys"):
            r = self.make_dict()
            for k, v in d.items():
                if isinstance(v, _Empty):
                    continue
                r[k] = self.after_data(v)
            return r
        elif isinstance(d, (list, tuple)):
            return [self.after_data(x) for x in d if not isinstance(x, _Empty)]
        else:
            return d


class _Updater:
    def __init__(self, resolver, item_map, *, make_dict=make_dict):
        self.resolver = resolver
        self.item_map = item_map
        self.make_dict = make_dict

    @reify
    def resolvers(self):
        resolvers = set(item.resolver for item in self.item_map.values())
        if self.resolver not in resolvers:
            resolvers.add(self.resolver)
        return resolvers

    def new_child(self, resolver):
        return self.__class__(resolver, self.item_map, make_dict=self.make_dict)

    def has(self, ref, *, resolver=None):
        resolver = resolver or self.resolver
        try:
            return resolver.access_by_json_pointer(ref) is not None
        except KeyError:
            return False  # xxx

    def pop(self, ref, *, resolver=None):
        return self.pop_by_path(json_pointer_to_path(ref), resolver=resolver)

    def pop_by_path(self, path, *, resolver=None):
        resolver = resolver or self.resolver
        v = resolver.access(path)
        self.update_by_path(path, _Empty(v), resolver=resolver)
        return v

    def update(self, ref, v, *, resolver=None):
        return self.update_by_path(json_pointer_to_path(ref), v, resolver=resolver)

    def update_by_path(self, path, v, *, resolver=None):
        resolver = resolver or self.resolver
        if len(path) == 1:
            d = resolver.doc
            if not hasattr(d, "parents"):  # chainmap?
                if not isinstance(d, (list, tuple)):
                    resolver.doc = d = ChainMap(self.make_dict(), d)
        else:
            d = resolver.access(path[:-1])
            if not hasattr(d, "parents"):  # chainmap?
                if not isinstance(d, (list, tuple)):
                    d = ChainMap(self.make_dict(), d)
                    resolver.assign(path[:-1], d)
        d[path[-1]] = v

    def iterate_items(self):
        return self.item_map.items()


# @as_command
# def run(*, src: str) -> None:
#     logging.basicConfig(level=logging.DEBUG)

#     resolver = get_resolver(src)
#     with Migration(resolver).migrate(dry_run=True) as u:
#         for k, item in u.iterate_items():
#             if k == "definitions/person":
#                 ref = "#/definitions/person/properties/value"
#                 u.update(item.resolver, ref, {"type": "integer"})
#             if k == "definitions/name":
#                 ref = "#/definitions/name/description"
#                 u.update(item.resolver, ref, "name of something")
