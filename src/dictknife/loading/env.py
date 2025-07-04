import sys
import os.path
from .raw import setup_extra_parser  # noqa
from dictknife.langhelpers import make_dict


def emit_environ(structure, make_dict, parse):
    """Recursively constructs a dictionary from a template structure,
    populating values from environment variables.

    Args:
        structure: The template structure (dict, list, or string).
                   If string, it's treated as an environment variable name.
        make_dict: Function to create dictionary instances (e.g., `dict` or `OrderedDict`).
        parse: Function to parse values, potentially extracting a type conversion function.

    Returns:
        A new dictionary with values substituted from environment variables,
        or a list if the structure was a list, or the environment variable's value
        if the structure was a string. Returns None if an environment variable is not found.
    """
    if hasattr(structure, "keys"):
        d = make_dict()
        for k, v in structure.items():
            name, fn = parse(v)
            emitted = emit_environ(name, make_dict=make_dict, parse=parse)
            if emitted is None:
                continue  # Skip if the environment variable is not set
            if fn is not None:
                try:
                    emitted = fn(emitted)
                except (ValueError, TypeError) as e:
                    # Handle cases where conversion fails, e.g., int("non-numeric")
                    # Or decide to raise an error, log, or return a default
                    print(f"Warning: Could not convert '{emitted}' using {fn.__name__} for key '{k}': {e}", file=sys.stderr)
                    continue # Or d[k] = None or some default
            d[k] = emitted
        return d
    elif isinstance(structure, (list, tuple)):
        # Filter out None values if environment variables are missing for list items
        return [item for item in (emit_environ(x, make_dict=make_dict, parse=parse) for x in structure) if item is not None]
    else:
        return os.environ.get(structure)


def parse_value(v: str, builtins=sys.modules["builtins"]):
    """Parses a string value to extract an environment variable name and an optional
    built-in type conversion function (e.g., "MY_VAR:int").

    Args:
        v: The string value to parse.
        builtins: The module to look for type conversion functions (defaults to `builtins`).

    Returns:
        A tuple (name, function). `function` is None if no type conversion is specified
        or if the specified function is not a valid builtin.
    """
    if ":" not in v:
        return v, None

    name, fnname = v.rsplit(":", 1)
    if not hasattr(builtins, fnname):
        # Consider logging a warning if fnname is present but not a valid builtin
        return v, None  # Treat as if no function was specified
    else:
        return name, getattr(builtins, fnname)


def load(fp, *, loader=None, make_dict=make_dict, parse=parse_value, errors=None):
    """Loads data from a file, using its structure as a template and populating
    values from environment variables.

    The input file itself (e.g., a JSON or YAML file) defines the structure
    and specifies which environment variables to use for values.

    Example:
        If `config.env.json` contains:
        ```json
        {
          "database_host": "DB_HOST",
          "database_port": "DB_PORT:int",
          "debug_mode": "DEBUG_MODE:bool"
        }
        ```
        And environment variables are DB_HOST=localhost, DB_PORT=5432, DEBUG_MODE=true,
        this function will return:
        ```python
        {'database_host': 'localhost', 'database_port': 5432, 'debug_mode': True}
        ```

    Args:
        fp: A file-like object for the template file. The format of this file
            (e.g., JSON, YAML) is determined by its extension (or the part of
            the filename before `.env`).
        loader: The loader instance, used to dispatch to the correct underlying
                format loader (e.g., json.load, yaml.load).
        make_dict: Function to create dictionary instances.
        parse: Function to parse values from the template, extracting environment
               variable names and optional type conversion functions.
        errors: (Unused) Error handling scheme.

    Returns:
        A dictionary populated with values from environment variables.
    """
    fname = getattr(fp, "name", "(unknown)")
    # Guess the original format by stripping ".env" or similar suffix if present,
    # or rely on the dispatcher's underlying logic if it handles combined extensions.
    # For example, if fname is "config.env.json", we want to load "config.json" logic.
    # This assumes the dispatcher can handle "basename" correctly or that the
    # .env part is just a marker.
    # A more robust way might involve checking registered extensions.
    basename = os.path.splitext(fname)[0] # e.g., "config.env" from "config.env.json"
    if basename.endswith(".env"): # A common pattern for this loader
        basename = os.path.splitext(basename)[0] # e.g., "config" from "config.env"

    # Dispatch to the loader for the base file type (e.g., json, yaml)
    # The `loader.fn_map` contains format -> load_function mappings.
    # `loader.dispatcher.dispatch` uses the filename to guess the format,
    # then looks up the load_function in `loader.fn_map`.
    try:
        base_load_func = loader.dispatcher.dispatch(basename, loader.fn_map)
        # We need to pass the original fp here, as the content is what matters
        # The `base_load_func` will read `fp` according to its format (JSON, YAML, etc.)
        template_dict = base_load_func(fp) # fp is already open
    except Exception as e:
        # It's possible `fp` was already consumed or closed by a previous attempt
        # or the format dispatch failed.
        # This part might need careful handling of fp state if retries are involved.
        # For now, assume fp is readable here.
        sys.stderr.write(f"Error loading template file '{fname}' with base format for '{basename}': {e}\n")
        return make_dict() # Return an empty dict or raise

    return emit_environ(template_dict, make_dict=make_dict, parse=parse)
