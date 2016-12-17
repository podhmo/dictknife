import json
import os
import logging
from pathresolver import PathResolver
from dictknife import LooseDictWalker
from dictknife import Accessor
from dictknife.contexts import SimpleContext
logger = logging.getLogger(__name__)


class WithResolverContext(SimpleContext):
    def __init__(self, resolver):
        self.resolver = resolver

    def __call__(self, walker, fn, value):
        return fn(walker, self.resolver, value)


def link(src):
    accessor = Accessor()
    cache = {}
    with open(src) as rf:
        data = json.load(rf)

    def on_has_ref(walker, resolver, d):
        logger.info("ref %s (on %s)", d["$ref"], resolver.path.replace(os.getcwd(), "."))
        file_path, ref = d["$ref"].split("#", 1)
        ref_path = ref.lstrip("/").split("/")
        if not file_path:
            subdata = accessor.access(cache[resolver.path], ref_path)
        else:
            subresolver = resolver.resolve(file_path)
            if subresolver.path not in cache:
                with subresolver.open() as rf:
                    data = json.load(rf)
                    cache[subresolver.path] = data
            data = cache[subresolver.path]
            walker.walk(["$ref"], data, ctx=WithResolverContext(subresolver))
            subdata = accessor.access(data, ref_path)

        d.pop("$ref")
        d.update(subdata)

    resolver = PathResolver(src)
    walker = LooseDictWalker(on_container=on_has_ref)
    walker.walk(["$ref"], data, ctx=WithResolverContext(resolver))
    return data


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--out", default=None)
    parser.add_argument("--logging", default=False, action="store_true")
    args = parser.parse_args()
    if args.logging:
        logging.basicConfig(level=logging.INFO)
    data = link(args.file)
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
