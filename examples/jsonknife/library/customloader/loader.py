from dictknife import loading
from dictknife.jsonknife import get_resolver
from dictknife import DictWalker


def run(*, filename):
    def onload(d, resolver, w=DictWalker(["$include"])):
        for _, sd, in w.walk(d):
            subresolver, jsref = resolver.resolve(sd.pop("$include"))
            sd.update(subresolver.access_by_json_pointer(jsref))

    resolver = get_resolver(filename, onload=onload)
    loading.dumpfile(resolver.doc)


def main():
    import argparse
    # import logging

    loading.setup()
    # logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("filename")

    args = parser.parse_args()
    return run(**vars(args))


if __name__ == "__main__":
    main()
