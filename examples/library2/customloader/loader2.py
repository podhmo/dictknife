from dictknife import DictWalker
from dictknife.jsonknife.resolver import ExternalFileResolver


def load(filename):
    ref_walker = DictWalker(["$include"])

    def onload(data, resolver):
        for _, d in ref_walker.walk(data):
            subresolver, _ = resolver.resolve(d.pop("$include"))
            d.update(subresolver.doc)

    resolver = ExternalFileResolver(filename, onload=onload)
    return resolver.doc


def main():
    from dictknife import loading
    import argparse
    # import logging

    loading.setup()
    # logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")

    args = parser.parse_args()

    data = load(args.filename)
    loading.dumpfile(data)


if __name__ == "__main__":
    main()
