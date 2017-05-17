from collections import OrderedDict


class SampleValuePlotter(object):
    """sample value from swagger's example and default"""

    def plot(self, d):
        typ = d.get("type")
        if "properties" in d or typ == "object":
            return self.plot_object(d.get("properties") or {}, OrderedDict())
        elif typ == "array":
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
