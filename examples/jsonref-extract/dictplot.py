# -*- coding:utf-8 -*-
import sys
from collections import OrderedDict
from dictknife import loading


class Dictplotter(object):
    def plot(self, d):
        if d["type"] == "object":
            return self.plot_object(d["properties"], OrderedDict())
        elif d["type"] == "array":
            return self.plot_array(d["items"], [])
        elif "example" in d:
            return d["example"]
        elif "default" in d:
            return d["default"]
        elif "enum" in d:
            return d["enum"][0]
        else:
            return "<>"

    def plot_object(self, props, r):
        for name, value in props.items():
            r[name] = self.plot(value)
        return r

    def plot_array(self, items, r):
        r.append(self.plot(items))
        return r


def run(src, dst):
    loading.setup()
    with open(src) as rf:
        data = loading.load(rf)
    d = Dictplotter().plot(data)
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
    args = parser.parse_args()
    run(args.src, args.dst)


if __name__ == "__main__":
    main()
