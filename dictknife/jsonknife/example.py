from dictknife.langhelpers import make_dict


class ExampleExtractor(object):
    """example value from swagger's example and default"""

    def extract(self, d):
        typ = d.get("type")
        if "properties" in d or typ == "object":
            return self.extract_object(d.get("properties") or {}, make_dict())
        elif typ == "array":
            return self.extract_array(d["items"], [])
        elif "example" in d:
            return d["example"]
        elif "default" in d:
            return d["default"]
        elif "enum" in d:
            return d["enum"][0]
        else:
            return "<>"

    def extract_object(self, props, r):
        for name, value in props.items():
            r[name] = self.extract(value)
        return r

    def extract_array(self, items, r):
        r.append(self.extract(items))
        return r


def extract(d):
    extractor = ExampleExtractor()
    return extractor.extract(d)
