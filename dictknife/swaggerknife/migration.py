import os.path
import contextlib
import logging
import tempfile
import shutil
from collections import ChainMap

from ..jsonknife.bundler import Scanner, CachedItemAccessor
from ..langhelpers import make_dict, pairrsplit, reify
from ..diff import diff
from .. import loading

logger = logging.getLogger(__name__)


class Migration:
    def __init__(self, resolver, *, make_dict=make_dict):
        self.resolver = resolver
        self.item_map = make_dict()
        self.make_dict = make_dict

    @reify
    def differ(self):
        return _Differ()

    @reify
    def updater(self):
        return _Updater(self.item_map, make_dict=self.make_dict)

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

        resolvers = set(item.resolver for item in self.item_map.values())
        for r in resolvers:
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

        resolvers = set(item.resolver for item in self.item_map.values())
        for r in resolvers:
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
            loading.dumpfile(r.doc, savepath)

    def migrate(self, doc=None, *, dry_run=False, where=None, copy=True, keep=False):
        logger.info("migrate (dry_run=%r, copy=%r, where=%r)", dry_run, copy, where)
        if dry_run:
            return self._migrate_dryrun_and_diff(doc=doc, where=where)

        @contextlib.contextmanager
        def _migrate():
            nonlocal where
            where = where or os.getcwd()
            savedir = None
            if copy:
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
    def diff(self, r, *, where):
        filename = os.path.relpath(r.name, start=where)
        before = self.before_data(r.doc)
        after = self.after_data(r.doc)
        yield from diff(
            before, after, fromfile=f"before:{filename}", tofile=f" after:{filename}"
        )

    def before_data(self, d):
        if hasattr(d, "parents"):
            return {k: self.before_data(v) for k, v in d.parents.items()}
        elif hasattr(d, "keys"):
            return {k: self.before_data(v) for k, v in d.items()}
        elif isinstance(d, (list, tuple)):
            return [self.before_data(x) for x in d]
        else:
            return d

    def after_data(self, d):
        if hasattr(d, "keys"):
            return {k: self.after_data(v) for k, v in d.items()}
        elif isinstance(d, (list, tuple)):
            return [self.after_data(x) for x in d]
        else:
            return d


class _Updater:
    def __init__(self, item_map, *, make_dict=make_dict):
        self.item_map = item_map
        self.make_dict = make_dict

    def update(self, resolver, ref, v):
        parent_ref, k = pairrsplit(ref, "/")
        d = resolver.access_by_json_pointer(parent_ref)
        if not hasattr(d, "parents"):  # chainmap?
            d = ChainMap(self.make_dict(), d)
            resolver.assign_by_json_pointer(parent_ref, d)
        d[k] = v

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
