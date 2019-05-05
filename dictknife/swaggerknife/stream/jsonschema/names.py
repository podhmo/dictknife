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


class predicates:
    new_type = "new_type"
    primitive_type = "primitive_type"
    combine_type = "combine_type"

    field_of_something = "field_of_something"
    toplevel_properties = "toplevel_properties"

    has_name = "has_name"
    has_enum = "has_enum"
    has_format = "has_format"
    has_links = "has_links"

    has_properties = "has_properties"
    has_extra_properties = "has_extra_properties"


class annotations:
    name = "name"
    links = "links"
    properties = "properties"
    extra_properties = "extra_properties"