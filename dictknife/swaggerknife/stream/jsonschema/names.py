class types:
    # support composite type? [string, float]
    any = "any"  # bottom

    object = "object"
    array = "array"
    boolean = "boolean"
    integer = "integer"
    number = "number"
    float = "float"
    string = "string"

    allOf = "allOf"
    oneOf = "oneOf"
    anyOf = "anyOf"
    not_ = "not"

    unknown = "unknown"


class flavors:
    new_type = "new_type"
    primitive_type = "primitive_type"
    combine_type = "combine_type"

    field_of_something = "field_of_something"
    toplevel_properties = "toplevel_properties"

    has_name = "has_name"
    has_enum = "has_enum"
    has_format = "has_format"

    has_extra_propeties = "has_extra_propeties"
