import sys
from dictknife import loading
from dictknife import Accessor
from dictknife import LooseDictWalker


class JSONRefAccessor(object):
    def __init__(self):
        self.accessor = Accessor()

    def access(self, fulldata, ref):
        # not support external file
        if not ref.startswith("#/"):
            raise ValueError("invalid ref {!r}".format(ref))
        path = ref[2:].split("/")
        return self.accessor.access(fulldata, path)

    def expand(self, fulldata, d):
        if "$ref" in d:
            original = self.access(fulldata, d["$ref"])
            d.pop("$ref")
            d.update(self.expand(fulldata, original))
            return d
        else:
            def on_has_ref(path, d):
                self.expand(fulldata, d)
            walker = LooseDictWalker(on_container=on_has_ref)
            walker.walk(["$ref"], d)
            return d

    def extract(self, fulldata, ref):
        return self.expand(fulldata, self.access(fulldata, ref))


def run(src, dst, ref):
    loading.setup()
    accessor = JSONRefAccessor()
    with open(src) as rf:
        data = loading.load(rf)
    if ref is None:
        d = accessor.expand(data, data)
    else:
        d = accessor.extract(data, ref)
    if dst is None:
        loading.dump(d, sys.stdout)
    else:
        with open(dst, "w") as wf:
            loading.dump(d, wf)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", default=None)
    parser.add_argument("--ref", default=None)
    args = parser.parse_args()
    run(args.src, args.dst, args.ref)

if __name__ == "__main__":
    main()
