import copy
import os.path
import logging

from dictknife import DictWalker
from dictknife import loading
from dictknife.langhelpers import reify, pairrsplit, make_dict


from .resolver import ExternalFileResolver
from .accessor import is_ref
from .relpath import relpath, fixref


logger = logging.getLogger(".".join(__name__.split(".")[1:]))


# todo: support ~0 and ~1
# todo: support recursion
# todo: multiple files input
# todo: aggregate primitive types
# todo: guess targets from ns
# todo: test


class Separator:  # todo: rename
    def __init__(self, resolver):
        self.resolver = resolver

    @reify
    def scanner(self):
        return Scanner(self.resolver)

    @reify
    def emitter(self):
        return Emitter(self.resolver)

    def separate(self, doc=None, *, name="main"):
        doc = doc or self.resolver.doc

        ns_map = self.scanner.scan(doc)
        for ns, def_items in ns_map.items():
            for def_item in def_items:
                self.emitter.emit(def_item)
        self.emitter.emit_main(doc=doc, name=name)


class Scanner:
    def __init__(self, resolver: ExternalFileResolver, *, here=None, format=None):
        self.resolver = resolver
        self.here = here or resolver.name
        self.format = format or "yaml"

    @reify
    def ref_walker(self) -> DictWalker:
        return DictWalker([is_ref])

    def scan(self, doc: dict) -> dict:
        namespaces = self._collect_namespaces(doc)
        r = {}
        for ns in namespaces:
            r[ns] = self._collect_def_items(ns)
        return r

    def _collect_def_items(self, ns):
        data = self.resolver.access_by_json_pointer(ns)
        defs = []
        for name, definition in data.items():
            fullname = "/".join([ns, name])
            new_filepath = relpath(fullname, where=self.here)
            defs.append(
                {
                    "ns": ns,
                    "name": name,
                    "fullname": fullname,
                    "$ref": "#/{}".format(fullname),
                    "path": "/".split(fullname),
                    # "is_self_recursion": is_self_recursion,  # ?
                    "new_filepath": "{}.{}".format(new_filepath, self.format),
                }
            )
        return defs

    def _collect_namespaces(self, doc: dict) -> dict:
        namespaces = []
        seen = set()

        for path, d in self.ref_walker.walk(doc):
            if "#/" not in d["$ref"]:
                continue

            _, ref = pairrsplit(d["$ref"], "#/")
            tokens = ref.strip("/").split("/")

            ns = "/".join(tokens[:-1])
            if ns in seen:
                continue
            seen.add(ns)
            namespaces.append(ns)
        return namespaces


class Emitter:
    def __init__(self, resolver, *, here: str = None, format=None):
        self.resolver = resolver
        self.here = here or resolver.name
        self.format = format or "yaml"
        self.registered = []  # List[Tuple[str, dict]]

    @reify
    def ref_walker(self) -> DictWalker:
        return DictWalker([is_ref])

    def emit(self, def_item: dict, *, retry: bool = False) -> None:
        logger.info("emit file %s", def_item["new_filepath"])
        try:
            return self._emit(def_item)
        except Exception as e:
            if retry:
                raise
            os.makedirs(os.path.dirname(def_item["new_filepath"]), exist_ok=True)
            logger.warning("emit file %r is occured, trying retry", e)
            return self.emit(def_item, retry=True)

    def _emit(self, def_item: dict) -> None:
        sresolver, query = self.resolver.resolve(def_item["$ref"])
        data = sresolver.access_by_json_pointer(query)

        doc = make_dict()
        self.resolver.assign_by_json_pointer(def_item["$ref"], data, doc=doc)

        for _, d in self.ref_walker.walk(data):
            ref = d["$ref"]
            if ref.startswith("#/"):
                ref = "{filepath}.{ext}{ref}".format(
                    filepath=relpath(d["$ref"].lstrip("#/"), where=self.here),
                    ext=self.format,
                    ref=d["$ref"],
                )
            d["$ref"] = fixref(ref, where=self.here, to=def_item["new_filepath"])

        # abspath -> relpath
        filepath = os.path.relpath(
            def_item["new_filepath"], start=os.path.dirname(self.here)
        )
        self.registered.append(
            (def_item["$ref"], {"$ref": "{}{}".format(filepath, def_item["$ref"])})
        )

        # todo: to dumper
        loading.dumpfile(doc, def_item["new_filepath"])

    def emit_main(self, *, doc: dict = None, name: str = "main"):
        doc = doc or self.resolver.doc
        new_doc = copy.deepcopy(doc)
        for ref, data in self.registered:
            self.resolver.assign_by_json_pointer(ref, data, doc=new_doc)

        # finding unseparated reference
        keep_refs = set()
        for path, d in self.ref_walker.walk(new_doc):
            if d["$ref"].startswith("#/"):
                keep_refs.add(d["$ref"])

        if keep_refs:
            for ref, data in self.registered:
                if ref in keep_refs:
                    continue
                self.resolver.maybe_remove_by_json_pointer(ref, doc=new_doc)

        new_filepath = relpath("{}.{}".format(name, self.format), where=self.here)
        logger.info("emit file %s", new_filepath)
        loading.dumpfile(new_doc, new_filepath)


def main():
    import argparse
    from dictknife.jsonknife import get_resolver

    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("--log", default="INFO")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log))

    resolver = get_resolver(args.src)
    separator = Separator(resolver)

    separator.separate()
    # emitter


if __name__ == "__main__":
    main()
