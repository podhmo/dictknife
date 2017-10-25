from dictknife.langhelpers import reify


class Inspector:
    def __init__(self, doc):
        self.doc = doc

    def inspect_version(self):
        return self.doc.get("openapi") or 2

    def inspect_default_position(self):
        return "#/definitions"

    @reify
    def repository(self):
        return Repository(self)


class Repository:
    def __init__(self, inspector):
        self.inspector = inspector

    @reify
    def localref_fixer(self):
        from dictknife.jsonknife.bundler import SwaggerLocalrefFixer
        prefixes = {k: k for k in ["definitions", "paths", "responses", "parameters"]}
        definition_prefix = self.inspector.inspect_default_position().lstrip("#/")
        return SwaggerLocalrefFixer(
            prefixes, definition_prefix, failback=lambda path, item: definition_prefix
        )
