# -*- coding:utf-8 -*-
from collections import OrderedDict
from dictknife import loading


class Dictplotter(object):
    def plot(self, d):
        if d["type"] == "object":
            return self.plot_object(d.get("properties") or {}, OrderedDict())
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
    data = loading.loadfile(src)
    d = Dictplotter().plot(data)
    loading.dumpfile(d, dst)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=None)
    parser.add_argument("--dst", default=None)
    args = parser.parse_args()
    run(args.src, args.dst)


if __name__ == "__main__":
    main()
