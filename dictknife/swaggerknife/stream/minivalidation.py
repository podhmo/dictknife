"""tiny validation for the subset of jsonschema, distinguish oneof, allof, anyof"""


class Error(Exception):
    def __init__(self, msg, *, errors=None):
        super().__init__(msg)
        self.errors = errors or []
        self.errors.append(msg)


class Validator:
    def __init__(self, resolver):
        self.resolver = resolver

    def resolve_ref(self, ref):
        pass

    def validate(self, ref: str):
        pass

    def _validate(self, data: dict, schema: dict):
        # see only required, propertites, patternProperties, additionalProperties
        # additionalProperties:false?
        if "properties" in schema:
            print("validate properties")
        if "additionalProperties" in schema:
            print("validate additionalProperties")
        if "patternProperties" in schema:
            print("validate patternProperties")


def main():
    
    pass


if __name__ == "__main__":
    main()
