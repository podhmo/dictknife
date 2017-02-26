import sys
from dictknife import loading
from dictknife.jsonknife import JSONRefAccessor


def run(src, dst, ref):
    loading.setup()
    accessor = JSONRefAccessor()
    with open(src) as rf:
        data = loading.load(rf)
    if ref is None:
        d = accessor.expand(data, data)
    else:
        sd = accessor.access(data, ref)
        d = accessor.expand(data, sd)
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
