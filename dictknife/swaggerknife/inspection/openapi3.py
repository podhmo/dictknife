from dictknife.langhelpers import reify


class Inspector:
    def __init__(self, doc):
        self.doc = doc

    def inspect_version(self):
        return self.doc.get("openapi") or 3

    def inspect_default_position(self):
        return "#/components/schemas"

    @reify
    def repository(self):
        return Repository()


class Repository:
    @reify
    def localref_fixer(self):
        from dictknife.jsonknife.bundler import SwaggerLocalrefFixer
        prefixes = {"paths": "paths"}
        definition_prefix = self.inspector.inspect_default_position().lstrip("#/")
        return SwaggerLocalrefFixer(
            prefixes,
            definition_prefix,
            failback=lambda path, item: "/".join(path[:2]) if path[0] == "components" else definition_prefix,
        )
