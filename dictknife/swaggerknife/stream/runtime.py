import sys
from importlib import import_module


def resolve_node(name, *, logger, here=None):
    here = here or sys._getframe(1).f_globals["__name__"]
    try:
        logger.debug("resolve node: %s", name)
        module_path, symbol = name.rsplit(".", 1)
        module = import_module(module_path, here)
        cls = getattr(module, symbol)
        return cls()
    except ImportError:
        logger.info("resolve node: %s is not found", name)
        return None


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
