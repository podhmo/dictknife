class Importer:
    # todo: use this in generated code
    def __init__(self, logger):
        self.logger = logger


class Case:
    def __init__(self, doc: dict):
        self.doc = doc  # {"definitions": {...}}
        self._validators = {}

    def get_validator(self, ref):
        from jsonschema import Draft4Validator

        validator = self._validators.get(ref)
        if validator is not None:
            return validator
        schema = {"$ref": ref, **self.doc}
        Draft4Validator.check_schema(schema)
        self._validators[ref] = validator = Draft4Validator(schema)
        return validator

    def when(self, d, ref) -> bool:
        validator = self.get_validator(ref)
        return validator.is_valid(d)
