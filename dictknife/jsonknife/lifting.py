import copy
from collections import OrderedDict
from dictknife.langhelpers import titleize


class LiftingState:
    def __init__(self, path, r=None):
        self.path = path
        self.r = r or OrderedDict()

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


class Extractor:
    def __init__(self, return_definition):
        self.return_definition = return_definition or self.return_definition_default

    def extract(self, data, state):
        self._extract(data, state)
        for k in list(state.r.keys()):
            state.r[k] = copy.deepcopy(state.r[k])
        return state.r

    def _extract(self, data, state, from_array=False):
        typ = data.get("type")
        if typ == "array" and "items" in data:
            return self.on_array_has_items(data, state)
        elif (typ is None or typ == "object") and (
            from_array or "properties" in data or hasattr(data.get("additionalProperties"), "keys")
        ):
            return self.on_object_has_properties(data, state)
        else:
            return data

    def return_definition_default(self, definition, fullname, typ="object"):
        return definition

    def on_object_has_properties(self, data, state):
        for name in data.get("properties") or {}:
            state.add_name(name)
            data["properties"][name] = self._extract(data["properties"][name], state)
            state.pop_name()

        if "$ref" in data:
            return data
        fullname = state.full_name()
        state.save_object(fullname, data)
        return self.return_definition(data, fullname, typ="object")

    def on_array_has_items(self, data, state):
        if "$ref" in data["items"]:
            return data
        fullname = state.full_name()
        state.add_array_item()
        data["items"] = self._extract(data["items"], state, from_array=True)
        state.save_array(fullname, data)
        state.pop_name()
        return self.return_definition(data, fullname, typ="array")


Handler = LiftingState  # for backward compatibility


class Flattener(Extractor):
    """this is existed for backward compatibility. don't use it"""

    def __init__(self, replace=True):
        self.replace = replace

    def return_definition(self, definition, fullname, typ="object"):
        if self.replace:
            return {"$ref": "#/definitions/{}".format(fullname)}
        else:
            return self.return_definition_default(definition, fullname, typ=typ)
