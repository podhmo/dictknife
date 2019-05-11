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


class roles:  # todo: rename to roles?
    new_type = "new_type"
    primitive_type = "primitive_type"
    combine_type = "combine_type"  # oneOf,allOf,anyOf

    field_of_something = "field_of_something"
    toplevel_properties = "toplevel_properties"

    has_name = "has_name"  # #/definitions/<name>
    has_enum = "has_enum"
    has_format = "has_format"

    has_properties = "has_properties"
    has_extra_properties = "has_extra_properties"
    has_expanded = "has_expanded"


class annotations:
    name = "name"
    properties = "properties"
    extra_properties = "extra_properties"
    expanded = "expanded"

    links = "links"
    pattern_properties_links = "pattern_properties_links"
    xxx_of_links = "xxx_of_links"
    # additionalPropeties link?
