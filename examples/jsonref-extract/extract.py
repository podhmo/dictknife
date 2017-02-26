from dictknife import loading
from dictknife.jsonknife import JSONRefAccessor


def run(src, dst, ref):
    loading.setup()
    accessor = JSONRefAccessor()
    data = loading.loadfile(src)
    if ref is None:
        d = accessor.expand(data, data)
    else:
        sd = accessor.access(data, ref)
        d = accessor.expand(data, sd)
    loading.dumpfile(d, dst)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=None)
    parser.add_argument("--dst", default=None)
    parser.add_argument("--ref", default=None)
    args = parser.parse_args()
    run(args.src, args.dst, args.ref)

if __name__ == "__main__":
    main()
