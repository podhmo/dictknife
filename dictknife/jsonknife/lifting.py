import copy
from dictknife.langhelpers import make_dict
from dictknife.langhelpers import titleize


class Handler:
    def __init__(self, path, r=None):
        self.path = path
        self.r = r or make_dict()

    def full_name(self):
        return "".join(self.path)

    def add_name(self, name):
        self.path.append(titleize(name))

    def add_array_item(self):
        self.add_name("item")

    def pop_name(self):
        self.path.pop()

    def save_object(self, name, definition):
        newdef = self.r.__class__()
        newdef["type"] = "object"
        newdef.update(definition)
        self.r[name] = newdef
        return newdef

    def save_array(self, name, definition):
        newdef = self.r.__class__()
        newdef["type"] = "array"
        newdef.update(definition)
        self.r[name] = newdef
        return newdef


class Flattener:
    def __init__(self, replace=True):
        self.replace = replace

    def extract(self, data, ctx):
        self._extract(data, ctx)
        for k in list(ctx.r.keys()):
            ctx.r[k] = copy.deepcopy(ctx.r[k])
        return ctx.r

    def _extract(self, data, ctx, from_array=False):
        typ = data.get("type")
        if typ == "array" and "items" in data:
            return self.on_array_has_items(data, ctx)
        elif (typ is None or typ == "object") and (from_array or "properties" in data or hasattr(data.get("additionalProperties"), "keys")):
            return self.on_object_has_properties(data, ctx)
        else:
            return data

    def return_definition(self, definition, fullname, typ="object"):
        if self.replace:
            return {"$ref": "#/definitions/{}".format(fullname)}
        else:
            return definition

    def on_object_has_properties(self, data, ctx):
        for name in data.get("properties") or {}:
            ctx.add_name(name)
            data["properties"][name] = self._extract(data["properties"][name], ctx)
            ctx.pop_name()

        if "$ref" in data:
            return data
        fullname = ctx.full_name()
        ctx.save_object(fullname, data)
        return self.return_definition(data, fullname, typ="object")

    def on_array_has_items(self, data, ctx):
        if "$ref" in data["items"]:
            return data
        fullname = ctx.full_name()
        ctx.add_array_item()
        data["items"] = self._extract(data["items"], ctx, from_array=True)
        ctx.save_array(fullname, data)
        ctx.pop_name()
        return self.return_definition(data, fullname, typ="array")
