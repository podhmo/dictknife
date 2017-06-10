import os.path
from dictknife.jsonknife.resolver import ExternalFileResolver
from dictknife import LooseDictWalkingIterator


class Loader:
    def __init__(self, cwd=None):
        cwd = cwd or os.getcwd()
        self.resolver = ExternalFileResolver(os.path.join(cwd, "*root*"))
        self.ref_walker = LooseDictWalkingIterator(["$include"])

    def load(self, filename, resolver=None):
        resolver = resolver or self.resolver
        subresolver, _ = resolver.resolve(filename)
        for _, d, in self.ref_walker.iterate(subresolver.doc):
            subfilename = d.pop("$include")
            subdata = self.load(subfilename, resolver=subresolver)
            d.update(subdata)
        return subresolver.doc


def main():
    from dictknife import loading
    import argparse
    # import logging

    loading.setup()
    # logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")

    args = parser.parse_args()

    loader = Loader()
    data = loader.load(args.filename)
    loading.dumpfile(data)


if __name__ == "__main__":
    main()
