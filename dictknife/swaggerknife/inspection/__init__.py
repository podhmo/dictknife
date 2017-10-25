def get_inspector(doc):
    if "components" in doc or doc.get("openapi", "").startswith("3"):
        from .openapi3 import Inspector
        return Inspector(doc)
    else:
        from .openapi2 import Inspector
        return Inspector(doc)
