from dictknife import Accessor


def access_by_json_pointer(doc, query, accessor=Accessor()):
    if query == "":
        return doc
    path = [p.replace("~1", "/").replace("~0", "~") for p in query[1:].split("/")]
    return accessor.access(doc, path)
