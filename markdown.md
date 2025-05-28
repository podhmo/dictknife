### Refactor: Modernize syntax in `dictknife/_sphinx.py`

**Description:**

The file `dictknife/_sphinx.py` contains opportunities for syntax modernization:
- The `LiteralIncludeReader.show_diff` function uses `os.path.basename`. Consider using `pathlib.Path(self.filename).name` for a more modern approach if `pathlib` is adopted more broadly.
- The string formatting for `{"version": "0.0"}` could use an f-string if other parts are updated, though it's minor.

---
### Refactor: Improve type hinting and initialization in `dictknife/accessing.py`

**Description:**

The file `dictknife/accessing.py` can be improved:
- Class `Accessor`: Methods `assign`, `access`, `maybe_remove`, `exists`, `maybe_access`, `maybe_access_container` could benefit from more detailed type hints for parameters `d` and `path`.
- Class `Scope`: The `accessor` parameter in `__init__` could default to `Accessor()` directly instead of `None` then `accessor or Accessor()`.

---
### Refactor: Modernize string formatting in `dictknife/cliutils/__init__.py`

**Description:**

In `dictknife/cliutils/__init__.py`:
- The string formatting `"\x1b[33m\x1b[1m{e.__class__.__name__}: {e}\x1b[0m".format(e=e)` can be converted to an f-string: `f"\x1b[33m\x1b[1m{e.__class__.__name__}: {e}\x1b[0m"`.

---
### Refactor: Modernize string formatting and review monkeypatching in `dictknife/cliutils/extraarguments.py`

**Description:**

In `dictknife/cliutils/extraarguments.py`:
- Class `ExtraArgumentsParsers`:
    - String formatting like `"{self.prefix} arguments {name}".format(self=self, name=name)` can be changed to f-strings. This applies to several places in the class.
    - `bind` method: `parser.format_help = format_help` is a form of monkeypatching. Ensure this is the intended and clearest way.
- Consider using `Self` for `add_parser` method if it were to return `self` (it currently returns `p`).

---
### Refactor: Modernize string formatting and review parser logic in `dictknife/commands/_monkeypatch.py`

**Description:**

In `dictknife/commands/_monkeypatch.py`:
- `apply_loading_format_extra_arguments_parser`:
    - String formatting `"{m.__name__} doesn't have setup_extra_parser() function".format(m=m)` can be an f-string.
    - The extensive use of `getattr` and manual argument parser manipulation is complex. Review for simplification if `argparse` offers alternative extension mechanisms.

---
### Refactor: Modernize `dictknife/commands/dictknife.py`

**Description:**

The file `dictknife/commands/dictknife.py` has several areas for modernization:
- **Function `cat`**:
    - String formatting for logging like `logger.debug("merge: %s", f)` can be updated to use f-strings or let `logging` handle formatting.
- **Function `transform`**:
    - `transform = lambda x: x  # NOQA` could be simplified.
    - String formatting in `import_symbol("dictknife.transform:{}".format(fn))` can be an f-string.
- **Function `shape`**:
    - Address the `xxx` comment: `d["example"] = ""  # xxx`.
- **Function `main`**:
    - String formatting in `module_path = "dictknife.loading.{}_{}".format(k.replace("_", "."), v)` and `RuntimeError("{}:setup() is not found".format(module_path))` can be f-strings.

---
### Refactor: Modernize `dictknife/commands/jsonknife.py`

**Description:**

In `dictknife/commands/jsonknife.py`:
- Most functions use string formatting with `.format()` which can be modernized to f-strings (e.g., `"{prefix}#/{name}".format(...)`).
- Function `bundle`: The logic for path manipulations with `os.path` could potentially use `pathlib`.
- Consider using `Self` type hint for methods in classes if they returned instances of themselves (though these are mostly standalone functions).

---
### Refactor: Modernize `dictknife/commands/swaggerknife.py`

**Description:**

In `dictknife/commands/swaggerknife.py`:
- Function `merge`: String formatting `"{where}#/{ns}/{name}".format(...)` and `RuntimeError("invalid style: {}".format(style))` can be f-strings.
- Function `json2swagger`: The `CommentWriter` class builds strings; f-strings could be used if preferred.
- General: Throughout the file, `.format()` can be replaced by f-strings.

---
### Refactor: Update custom decorator in `dictknife/deepequal.py`

**Description:**

In `dictknife/deepequal.py`:
- The `_Atom`, `_Collection`, `_Dict` classes use a custom `@reify` decorator. If Python 3.8+ is a target, `@functools.cached_property` could replace `@reify`.

---
### Refactor: Correct ValueError formatting in `dictknife/deepmerge.py`

**Description:**

In `dictknife/deepmerge.py`:
- `ValueError("cannot merge dict and non-dict: left=%s, right=%s", left, right)` is missing `.format()`. It should be `ValueError(f"cannot merge dict and non-dict: left={left}, right={right}")` or similar.
- `RuntimeError("unavailable method not in {METHODS!r}".format(METHODS=METHODS))` can be an f-string.

---
### Refactor: Modernize string formatting in `dictknife/diff/rows.py`

**Description:**

In `dictknife/diff/rows.py`:
- String formatting `"{}/{}".format(i, srow["name"])` can be f-strings.
- The `_all_keys` function has complex list manipulation logic; consider simplifying or adding more comments.

---
### Refactor: Update custom decorator in `dictknife/guessing.py`

**Description:**

In `dictknife/guessing.py`:
- Class `Guesser` uses a custom `@reify` decorator. Consider `@functools.cached_property` if Python 3.8+ is targeted.

---
### Refactor: Modernize string formatting in `dictknife/jsonknife/__init__.py`

**Description:**

In `dictknife/jsonknife/__init__.py`:
- String formatting `"{prefix}#/{jsonref}".format(...)` and `ValueError("{efilename!r} is not json reference. (please <filename>#/<reference>)".format(efilename=efilename))` can be f-strings.

---
### Refactor: Modernize string formatting in `dictknife/jsonknife/accessor.py`

**Description:**

In `dictknife/jsonknife/accessor.py`:
- `repr` formatting `"<{} localref={self.localref!r},  globalref={self.globalref!r}>".format(...)` can be an f-string.

---
### Refactor: Modernize `dictknife/jsonknife/bundler.py`

**Description:**

In `dictknife/jsonknife/bundler.py`:
- `ValueError("unexpected flavor {!r}, available flavors are ['openapiv2', 'openapiv3']".format(flavor))` can be an f-string.
- Class `Scanner` uses `@reify`. Consider `@functools.cached_property`.
- Class `Emitter`: String formatting in `logger.debug` and `sd["$ref"] = "#/{}".format(...)` can be f-strings.
- Class `LocalrefFixer`: String formatting `"{}/{}".format(prefix, name)` can be f-strings.
- Class `SimpleConflictFixer`: `RuntimeError("conficted. %r <-> %r" % (olditem.globalref, newitem.globalref))` is old-style formatting; use f-strings or `.format()`.

---
### Refactor: Update custom decorator in `dictknife/jsonknife/expander.py`

**Description:**

In `dictknife/jsonknife/expander.py`:
- Class `Expander` uses `@reify`. Consider `@functools.cached_property`.

---
### Refactor: Modernize string formatting in `dictknife/jsonknife/lifting.py`

**Description:**

In `dictknife/jsonknife/lifting.py`:
- Class `Handler`: `fullname` in `return_definition` uses `.format()`. Can be an f-string.

---
### Refactor: Modernize string formatting in `dictknife/jsonknife/patch.py`

**Description:**

In `dictknife/jsonknife/patch.py`:
- String formatting in `_merge` like `"/{{prefix}}/{{subpath}}".format(...)` can be f-strings. Note the double curly braces to escape them in f-strings if a literal brace is needed: `f"/{{{prefix}}}/{{{subpath}}}"`.

---
### Refactor: Modernize `dictknife/jsonknife/relpath.py`

**Description:**

In `dictknife/jsonknife/relpath.py`:
- Extensive use of `os.path`. `pathlib` is an alternative for a more object-oriented style if preferred.
- String formatting `filepath = "{}#{}".format(filepath, jsref)` can be f-strings.

---
### Refactor: Modernize `dictknife/jsonknife/resolver.py`

**Description:**

In `dictknife/jsonknife/resolver.py`:
- `ValueError("invalid query {!r}".format(query))` can be an f-string.
- `repr` formatting `<FileResolver {!r}>`.format(self.filename)` can be an f-string.
- Uses `@reify`. Consider `@functools.cached_property`.

---
### Refactor: Modernize string formatting and path handling in `dictknife/jsonknife/separator.py`

**Description:**

In `dictknife/jsonknife/separator.py`:
- String formatting `"{}{}".format(filepath, def_item["$ref"])` can be f-strings.
- Uses `os.path`. `pathlib` is an alternative.

---
### Refactor: Modernize `dictknife/langhelpers.py`

**Description:**

In `dictknife/langhelpers.py`:
- `sys.version_info` check for `make_dict`. If Python < 3.6 is no longer supported, this can be simplified to `make_dict = dict`. Standard dicts are ordered since Python 3.7 (CPython 3.6).
- Uses `@reify` decorator. Consider `@functools.cached_property`.

---
### Refactor: Modernize `dictknife/loading/__init__.py`

**Description:**

In `dictknife/loading/__init__.py`:
- String formatting in `dumpfile` for `FileNotFoundError` retry logic can use f-strings if paths are included in messages.

---
### Refactor: Modernize `dictknife/loading/_gsuite.py`

**Description:**

In `dictknife/loading/_gsuite.py`:
- Uses `typing.Optional`, `typing.Sequence`. For Python 3.9+, these can be `| None` and `collections.abc.Sequence` (or just `list`/`tuple` if specific).
- String formatting in `get_credentials_failback_webbrowser` can use f-strings.
- Uses `@reify`. Consider `@functools.cached_property`.

---
### Refactor: Modernize `dictknife/loading/_lazyimport.py`

**Description:**

In `dictknife/loading/_lazyimport.py`:
- Uses `@reify`. Consider `@functools.cached_property`.
- String formatting `"... ({!r})".format(e)` can be an f-string.

---
### Refactor: Modernize `dictknife/loading/csv.py`

**Description:**

In `dictknife/loading/csv.py`:
- `sys.version_info` check for `make_dictReader`. If Python < 3.6 is no longer supported, this can be simplified.
- String formatting `"... err=%r", self.line_num, e` in logger can be updated.

---
### Refactor: Modernize string formatting in `dictknife/loading/md.py`

**Description:**

In `dictknife/loading/md.py`:
- String formatting ` "| {} |".format(...)` can be f-strings.

---
### Refactor: Remove legacy code in `dictknife/mkdict.py`

**Description:**

In `dictknife/mkdict.py`:
- `sys.version_info[:2] < (3, 6)` check for `shlex` monkeypatch. If Python < 3.6 is not supported, this can be removed. The `shlex` monkeypatch itself is a significant piece of legacy compatibility code.

---
### Refactor: Modernize string formatting in `dictknife/naming.py`

**Description:**

In `dictknife/naming.py`:
- String formatting `r"\1{}\2".format(separator)` and `"{}{}".format(name[0].upper(), name[1:])` can be f-strings.

---
### Refactor: Modernize string formatting in `dictknife/operators.py`

**Description:**

In `dictknife/operators.py`:
- String formatting `"<{{self.__class__.__name__}} args={{args!r}}>".format(self=self, args=self.args)` can be f-strings. Note the double curly braces.

---
### Refactor: Modernize string formatting in `dictknife/shape.py`

**Description:**

In `dictknife/shape.py`:
- String formatting `"?{{}}".format(...)` can be f-strings.

---
### Refactor: Modernize `dictknife/swaggerknife/json2swagger.py`

**Description:**

In `dictknife/swaggerknife/json2swagger.py`:
- `ValueError("unsupported for {!r}".format(val))` can be an f-string.
- `"{}{}".format(name[0].upper(), name[1:])` (titleize) can be f-strings.
- String formatting in `Emitter.make_array_schema` etc. can be f-strings.

---
### Refactor: Modernize `dictknife/swaggerknife/migration.py`

**Description:**

In `dictknife/swaggerknife/migration.py`:
- Uses `@reify`. Consider `@functools.cached_property`.
- String formatting in `diff` method like `"before:{{filename}}".format(filename=filename)` can be f-strings.

---
### Refactor: Modernize string formatting in `dictknife/transform.py`

**Description:**

In `dictknife/transform.py`:
- String formatting `"{}{}{}".format(...)` can be f-strings.

---
### Refactor: Review vendored code `fastentrypoints.py`

**Description:**

The file `fastentrypoints.py` is vendored code.
- It uses older string formatting (`%`) and `re.sub` for path manipulation.
- Evaluate if this script is still providing significant benefits over modern setuptools. If so, consider modernizing its syntax. If not, consider removing it.

---
### Docs: Add module-level docstring to `dictknife/__init__.py`

**Description:**

The file `dictknife/__init__.py` is missing a module-level docstring.
- Add a docstring explaining the main purpose of the `dictknife` package and briefly explain why specific symbols are exposed.

---
### Docs: Improve docstrings and comments in `dictknife/_sphinx.py`

**Description:**

The file `dictknife/_sphinx.py` needs improved documentation:
- Add a module-level docstring.
- Add a docstring to the `setup` function explaining its purpose as a Sphinx extension.
- Add a docstring to the monkeypatched `show_diff` method.
- Add a comment explaining why `LiteralIncludeReader.show_diff` is being monkeypatched.

---
### Docs: Add comprehensive docstrings to `dictknife/accessing.py`

**Description:**

The file `dictknife/accessing.py` requires detailed docstrings:
- Add a module-level docstring.
- Class `Accessor`: `__init__` (detail `make_dict`, `zero_value`), methods `assign`, `access`, `maybe_remove`, `exists`, `maybe_access`, `maybe_access_container` (explain `d`, `path`, returns, side effects).
- Class `Scope`: `__init__`, `get`, `__getitem__`, `push`, `pop`, `scope` methods.
- Classes `ImmutableModifier`, `MutableModifier` methods.
- Function `dictmap`: Explain `fn`, `x`, `mutable`, `with_key`.
- Function `get_modifier`.
- Comment the purpose of `missing = object()`.

---
### Docs: Add docstrings to `dictknife/cliutils/__init__.py`

**Description:**

In `dictknife/cliutils/__init__.py`:
- Add a module-level docstring.
- Add a docstring to `traceback_shortly` explaining its purpose.

---
### Docs: Improve docstrings and comments in `dictknife/cliutils/extraarguments.py`

**Description:**

In `dictknife/cliutils/extraarguments.py`:
- Add a module-level docstring.
- Class `ExtraArgumentsParsers`: `__init__` and methods `add_parser`, `as_epilog`, `bind`, `parse_args`, `_transform_args`, `_parse_args`, `_show_warnigs` need docstrings.
- Expand on the comment: `bind(parser)  # xxx: side effect`.

---
### Docs: Add docstrings to `dictknife/commands/_monkeypatch.py`

**Description:**

In `dictknife/commands/_monkeypatch.py`:
- Add a module-level docstring.
- Functions `apply_rest_arguments_as_extra_arguments_parser` and `apply_loading_format_extra_arguments_parser` need comprehensive docstrings.
- Elaborate or resolve `xxx:` comments.
- Explain the rationale for `if f == "markdown": continue # xxx:`.

---
### Docs: Improve documentation for `dictknife/commands/dictknife.py`

**Description:**

Enhance documentation for `dictknife/commands/dictknife.py`:
- Add a module-level docstring.
- Add docstrings for `_open`, `cat` (detail params like `merge_method`, `slurp`, `extra`), `transform` (explain `code`, `functions`), `diff` (explain params and choices), `shape` (explain params), `shrink` (explain params), `mkdict` (explain params), `main`.
- Explain the hack: `parser.print_usage = parser.print_help`.
- Explain custom help for the transform command.
- Document the `--merge-method` option for `dictknife cat`.
- Document various output formats for `dictknife diff` (e.g., `jsonpatch`, `pair`).
- Document `--fn`/`--function` for `dictknife transform`.

---
### Docs: Improve documentation for `dictknife/commands/jsonknife.py`

**Description:**

Enhance documentation for `dictknife/commands/jsonknife.py`:
- Add a module-level docstring.
- Add detailed docstrings for `cut`, `deref`/`select`, `bundle`, `separate`, `examples`, and `main`.
- Explain the hack: `parser.print_usage = parser.print_help`.
- Update documentation to reflect `deref` being deprecated in favor of `select`.
- Document `--flavor` option for `jsonknife bundle`.
- Document `--use-expand` option for `jsonknife examples`.

---
### Docs: Improve documentation for `dictknife/commands/swaggerknife.py`

**Description:**

Enhance documentation for `dictknife/commands/swaggerknife.py`:
- Add a module-level docstring.
- Add detailed docstrings for `tojsonschema`, `json2swagger` (explain custom usage of `--detector`, `--emitter`, `--emit`), `merge`, `flatten`, and `main`.
- Explain the hack: `parser.print_usage = parser.print_help`.
- Clarify the re-assignment of `info` in `detector.detect`.

---
### Docs: Add comprehensive docstrings to `dictknife/deepequal.py`

**Description:**

In `dictknife/deepequal.py`:
- Add a module-level docstring.
- Function `deepequal`: Explain `normalize`.
- Function `sort_flexibly`: Explain "flexibly".
- Functions `_wrap`, `_unwrap`, `halfequal`.
- Internal classes `_Atom`, `_Collection`, `_Dict` and their methods if logic is complex.
- Comment the purpose of `_NONE = _Atom(None)`.

---
### Docs: Add comprehensive docstrings to `dictknife/deepmerge.py`

**Description:**

In `dictknife/deepmerge.py`:
- Add a module-level docstring.
- Functions `_deepmerge_extend`, `_deepmerge_replace`, `_deepmerge_merge`: Explain strategies.
- Function `deepmerge`: Clearly document `method` choices (the existing docstring is a good start).

---
### Docs: Add docstrings to `dictknife/diff/__init__.py`

**Description:**

In `dictknife/diff/__init__.py`:
- Add a module-level docstring.
- Comment on why `make_jsonpatch` is re-exported.

---
### Docs: Add comprehensive docstrings to `dictknife/diff/diff.py`

**Description:**

In `dictknife/diff/diff.py`:
- Add a module-level docstring.
- Function `diff`: Explain `tostring`, `n`, `terminator`, `normalize`, `sort_keys`.
- Function `_default_tostring`.

---
### Docs: Add comprehensive docstrings to `dictknife/diff/rows.py`

**Description:**

In `dictknife/diff/rows.py`:
- Add a module-level docstring.
- Function `diff_rows`: Explain `diff_key`, `normalize`.
- Function `_all_keys`: Explain its logic.

---
### Docs: Add comprehensive docstrings to `dictknife/guessing.py`

**Description:**

In `dictknife/guessing.py`:
- Add a module-level docstring.
- Class `Guesser`: `__init__` (modifier, default), methods `is_bool`, `is_float`, `is_int`, `is_list`, `is_dict`, `guess`, `guess_default`.
- Function `guess`: Explain `guesser_factory`, `default`, `mutable`.

---
### Docs: Add docstrings to `dictknife/jsonknife/__init__.py`

**Description:**

In `dictknife/jsonknife/__init__.py`:
- Add a module-level docstring.
- Functions `expand`, `bundle`, `separate`: Explain parameters and purpose.

---
### Docs: Add comprehensive docstrings to `dictknife/jsonknife/_wrapped_exception.py`

**Description:**

In `dictknife/jsonknife/_wrapped_exception.py`:
- Add a module-level docstring.
- Class `WrappedExceptionFactory`: `__init__` (prefix, mixin_class), `__call__` (e, where).
- Class `WrappedMixin`: `stack` property and `__str__`.
- Comment on the choice of prefix "Ex" for `wrap_exception`.

---
### Docs: Add comprehensive docstrings to `dictknife/jsonknife/accessor.py`

**Description:**

In `dictknife/jsonknife/accessor.py`:
- Add a module-level docstring.
- Class `AccessingMixin`: Clarify `doc`, `a` params.
- Class `CachedItem`: `__init__`.
- Functions `path_to_json_pointer`, `json_pointer_to_path`, `access_by_json_pointer`, `assign_by_json_pointer`, `maybe_remove_by_json_pointer`.
- Class `StackedAccessor`: `__init__`, `resolver`, `access`, `_access`, `pop_stack`, `push_stack`, `as_json`.
- Class `CachedItemAccessor`: `__init__`, `_access`.
- Comment on the structure detected by `is_ref`.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/jsonknife/bundler.py`

**Description:**

In `dictknife/jsonknife/bundler.py`:
- Add a module-level docstring.
- Function `create_scanner_factory_from_flavor`: Explain `flavor`.
- Classes `Bundler`, `Scanner`, `Emitter`, `LocalrefFixer`, `SimpleConflictFixer` and their methods need detailed docstrings.
- Explain "default_position" in `LocalrefFixer`.
- Address `xxx:` comments.

---
### Docs: Add comprehensive docstrings to `dictknife/jsonknife/example.py`

**Description:**

In `dictknife/jsonknife/example.py`:
- Add a module-level docstring (current one is good for `extract` but could be broader).
- Class `State`: `__init__`.
- Functions `_extract`, `_extract_object`, `_extract_array`.
- Function `extract`: Explain `limit`.

---
### Docs: Add docstrings to `dictknife/jsonknife/expander.py`

**Description:**

In `dictknife/jsonknife/expander.py`:
- Add a module-level docstring.
- Function `detect_circur_reference` (correct typo to `detect_circular_reference`): Explain `doc`, `d`.
- Class `Expander` and its methods.

---
### Docs: Add docstrings to `dictknife/jsonknife/lifting.py`

**Description:**

In `dictknife/jsonknife/lifting.py`:
- Add a module-level docstring.
- Class `Handler` and its methods.
- Class `Flattener` and its methods.

---
### Docs: Add docstrings to `dictknife/jsonknife/merge.py`

**Description:**

In `dictknife/jsonknife/merge.py`:
- Add a module-level docstring mentioning RFC7396.
- Function `merge`: Explain `d`, `q`, `make_dict`.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/jsonknife/patch.py`

**Description:**

In `dictknife/jsonknife/patch.py`:
- Add a module-level docstring.
- Comment `diff` namedtuple.
- Function `make_jsonpatch`: Explain `src`, `dst`, `verbose`.
- Function `_merge`.
- Class `_Walker` and its methods.
- Elaborate on `self.move_map = {}  # todo:`.

---
### Docs: Add docstrings and comments to `dictknife/jsonknife/relpath.py`

**Description:**

In `dictknife/jsonknife/relpath.py`:
- Add a module-level docstring.
- Functions `fixpath`, `fixref`, `relref`, `normpath`: Add brief explanation of `where`, `to` parameters (examples are good).
- Address `# todo: move module` comment.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/jsonknife/resolver.py`

**Description:**

In `dictknife/jsonknife/resolver.py`:
- Add a module-level docstring.
- Classes `OneDocResolver`, `ExternalFileResolver` (and its methods/properties).
- Class `ROOT`: Explain its purpose.
- Functions `get_resolver`, `build_subset`.
- Comment on backward compatibility for `get_resolver_from_filename`.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/jsonknife/separator.py`

**Description:**

In `dictknife/jsonknife/separator.py`:
- Add a module-level docstring.
- Function `_with_format`.
- Classes `Separator`, `Scanner`, `Emitter` and their methods.
- Elaborate or track todos like `# todo: support ~0 and ~1`.

---
### Docs: Add comprehensive docstrings to `dictknife/langhelpers.py`

**Description:**

In `dictknife/langhelpers.py`:
- Add a module-level docstring.
- Comment on `make_dict` conditional import.
- Functions `pairsplit`, `pairrsplit`.
- Class `reify`.
- Functions `as_jsonpointer`, `as_path_node`.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/loading/__init__.py`

**Description:**

In `dictknife/loading/__init__.py`:
- Add a module-level docstring.
- Classes `Loader`, `Dumper`, `Dispatcher` and their methods.
- Functions `get_opener`, `get_formats`, `get_unknown`, `setup`.
- Explain the role of `unknown = "(unknown)"`.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/loading/_gsuite.py`

**Description:**

In `dictknife/loading/_gsuite.py`:
- Add a module-level docstring.
- Functions `get_credentials`, `get_credentials_failback_webbrowser` (detail auth flow).
- Class `MemoryCache` and methods.
- Function `_get_discovery_cache`.
- Class `Loader` and methods.
- Comment on user setup for `DEFAULT_CREDENTIALS_PATH`.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/loading/_lazyimport.py`

**Description:**

In `dictknife/loading/_lazyimport.py`:
- Add a module-level docstring.
- Class `LoadingModule`: Explain lazy-loading properties.
- Inner classes `_TomlAdaptor`, `_fake_yaml` and their methods.
- Comment on `m = LoadingModule()` global instance.

---
### Docs: Add docstrings and address critical comment in `dictknife/loading/_yaml.py`

**Description:**

In `dictknife/loading/_yaml.py`:
- Add a module-level docstring.
- Functions `load`, `dump`: Clarify `ruamel.yaml` specific params.
- Address critical comment: `_pool = {}  # xxx: memory leak`.

---
### Docs: Add comprehensive docstrings to `dictknife/loading/csv.py`

**Description:**

In `dictknife/loading/csv.py`:
- Add a module-level docstring.
- Function `setup_extra_parser`.
- Function `load`: Explain `_registry`, `create_reader_class`.
- Function `dump`: Explain `fullscan`.
- Function `_create_reader_class`: Explain `retry` and custom reader purpose.

---
### Docs: Add docstrings to `dictknife/loading/env.py`

**Description:**

In `dictknife/loading/env.py`:
- Add a module-level docstring.
- Function `emit_environ`: Explain `structure`, `parse`.
- Function `parse_value`: Explain `v`, `builtins`.
- Function `load`: Explain `parse`.

---
### Docs: Add docstrings to `dictknife/loading/json.py`

**Description:**

In `dictknife/loading/json.py`:
- Add a module-level docstring.
- Function `load`: Explain `object_pairs_hook`.
- Function `dump`: Explain `default`.

---
### Docs: Add docstrings to `dictknife/loading/md.py`

**Description:**

In `dictknife/loading/md.py`:
- Add a module-level docstring.
- Function `load`: Explain `null_value`.
- Function `dump`: Explain `null_value`.

---
### Docs: Add docstrings to `dictknife/loading/modification/__init__.py`

**Description:**

In `dictknife/loading/modification/__init__.py`:
- Add a module-level docstring.
- Functions `_get_modifications_history`, `is_used`, `use`.

---
### Docs: Add docstrings to `dictknife/loading/modification/*`

**Description:**

For each file in `dictknife/loading/modification/`:
- `compact.py`, `flatten.py`, `unescape_unicode.py`, `unescape_url.py`:
    - Add a module-level docstring.
    - Function `setup`: Explain its modification effect.
    - Inner `wrap` and `call` functions could have brief docstrings/comments.

---
### Docs: Add docstrings to `dictknife/loading/raw.py`

**Description:**

In `dictknife/loading/raw.py`:
- Add a module-level docstring.
- Functions `load`, `dump`, `setup_extra_parser`.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/loading/spreadsheet.py`

**Description:**

In `dictknife/loading/spreadsheet.py`:
- Add a module-level docstring.
- Comment `Guessed` namedtuple fields.
- Function `guess`: Explain `pattern`, `sheet_rx`.
- Function `load`: Explain `pattern`.
- Function `not_open` (context manager).
- Explain why `_loader` is global.

---
### Docs: Add docstrings to `dictknife/loading/toml.py` and `dictknife/loading/tsv.py`

**Description:**

- `dictknife/loading/toml.py`: Add module-level docstring and docstrings for `load`, `dump`.
- `dictknife/loading/tsv.py`: Add module-level docstring and indicate `load`, `dump` are for TSV.

---
### Docs: Add docstrings to `dictknife/loading/yaml.py`

**Description:**

In `dictknife/loading/yaml.py`:
- Add a module-level docstring.
- Functions `load`, `dump`: Clarify `ruamel.yaml` specific parameters.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/mkdict.py`

**Description:**

In `dictknife/mkdict.py`:
- Add a module-level docstring.
- Class `_AccessorSupportList` and its methods.
- Function `mkdict`: Briefly mention `accessor`, `guess`, `shared` params in its already good docstring.
- Function `_mkdict` (internal, but complex).
- Function `tokenize`.
- Clearly comment the `shlex` monkeypatch for Python <3.6.

---
### Docs: Add comprehensive docstrings to `dictknife/naming.py`

**Description:**

In `dictknife/naming.py`:
- Add a module-level docstring (explaining it's for string case conversions).
- Functions `normalize`, `snakecase`, `kebabcase`, `camelcase`, `pascalcase`, `titleize`, `untitleize` (explain conversions and params).

---
### Docs: Add comprehensive docstrings and comments to `dictknife/operators.py`

**Description:**

In `dictknife/operators.py`:
- Add a module-level docstring.
- Function `apply`: Explain `q`, `v`, `*args`.
- Function `repr` (for classes).
- Classes `Regexp`, `Any`, `Not`, `Or`, `And` and their `__init__`, `__call__`.
- Comment `ANY = Any()` singleton.

---
### Docs: Add docstrings to `dictknife/pp.py`

**Description:**

In `dictknife/pp.py`:
- Add a module-level docstring.
- Function `pp`: Explain `d`, `out`.
- Function `indent` (context manager).

---
### Docs: Add comprehensive docstrings to `dictknife/shape.py`

**Description:**

In `dictknife/shape.py`:
- Add a module-level docstring.
- Comment `Row` namedtuple fields.
- Class `_State` and methods.
- Class `Traverser` and methods.
- Function `_build_pathlist_from_state`.
- Function `shape`: Explain all parameters.

---
### Docs: Add docstrings to `dictknife/swaggerknife/__init__.py` and `flatten.py`

**Description:**

- `dictknife/swaggerknife/__init__.py`: Add module-level docstring if more than a package marker.
- `dictknife/swaggerknife/flatten.py`: Add module-level docstring and docstring for `flatten` function (explain `data`, `replace`).

---
### Docs: Add comprehensive docstrings to `dictknife/swaggerknife/json2swagger.py`

**Description:**

In `dictknife/swaggerknife/json2swagger.py`:
- Add a module-level docstring.
- Function `resolve_type`.
- Class `NameResolver`.
- Function `make_signature`.
- Classes `Detector`, `Emitter`, `CommentWriter` and their methods.

---
### Docs: Add comprehensive docstrings and comments to `dictknife/swaggerknife/migration.py`

**Description:**

In `dictknife/swaggerknife/migration.py`:
- Add a module-level docstring.
- Functions `is_empty`, `is_empty_collection`.
- Class `_Empty`.
- Class `Migration` and its methods (comprehensive docstrings needed).
- Classes `_Differ`, `_Updater` and their methods.
- Explain `xxx` comment related to `tempfile.mkdtemp`.

---
### Docs: Add comprehensive docstrings to `dictknife/transform.py`

**Description:**

In `dictknife/transform.py`:
- Add a module-level docstring.
- Function `_make_key`.
- Function `unflatten` (explain `sep`, `accessor`).
- Function `_fix_unflatten_list`.
- Function `flatten` (explain `sep`).
- Function `rows` (explain `kname`, `vname`).
- Function `update_keys` (explain `key`, `coerce`).
- Partials like `str_dict` should have brief docstrings.
- Functions `only_num`, `only_str`.
- Function `shrink` (explain all parameters).

---
### Docs: Add comprehensive docstrings and comments to `dictknife/walkers.py`

**Description:**

In `dictknife/walkers.py`:
- Add a module-level docstring.
- Classes `SimpleContext`, `PathContext`, `RecPathContext`, `ContainerHandler`, `DataHandler` and their methods.
- Class `DictWalker` and its methods.
- Comment backward compatibility aliases.

---
### Docs: Review comments in `docs/source/conf.py`

**Description:**

In `docs/source/conf.py`:
- Review existing comments, especially for custom settings, to ensure clarity.

---
### Docs: Add docstrings to `fastentrypoints.py`

**Description:**

In `fastentrypoints.py` (vendored code):
- Add/improve docstrings for `get_args` and `main` function if feasible and if the script is to be kept.

---
### Docs: Add comments to `setup.py`

**Description:**

In `setup.py`:
- Add a module-level docstring (optional for `setup.py`).
- Ensure clarity of `extras_require` and `entry_points` if complex.

---
### Docs: Update `README.md` about obsolete ReadTheDocs link

**Description:**

The `README.md` states: "http://dictknife.readthedocs.io (:warning: this document is obsoleted)".
- Verify the current status of the ReadTheDocs page.
- Update `README.md` to:
    - Remove the link if the page is truly gone or unmaintained.
    - Or, clearly mark it as archived and link to the new, up-to-date documentation portal (once established).
    - State if no alternative currently exists and that documentation is within the `docs/` directory or `README.md` itself.

---
### Docs: Create a unified and up-to-date documentation portal

**Description:**

The project lacks a central, modern documentation portal.
- Consolidate documentation from `.md` and `.rst` files.
- Use Sphinx (already partially set up) to build HTML documentation.
- Host the documentation (e.g., GitHub Pages, or fix ReadTheDocs).
- Update `README.md` to point to this new portal.

---
### Docs: Complete missing information in `docs/source/commands.md`

**Description:**

The file `docs/source/commands.md` is missing documentation for some `dictknife` CLI features:
- `dictknife cat`: Document the `--merge-method` option and its choices.
- `dictknife diff`: Document the various output formats (`jsonpatch`, `pair`, `dict`).
- `dictknife transform`: Document the `--fn`/`--function` argument and provide examples.

---
### Docs: Update and complete `docs/source/commands2.rst` (jsonknife)

**Description:**

The file `docs/source/commands2.rst` needs updates for `jsonknife`:
- Prioritize documentation for the `select` command, as `deref` is deprecated. Add examples for `select`.
- `jsonknife bundle`: Document the `--flavor` option.
- `jsonknife examples`: Document the `--use-expand` option.

---
### Docs: Expand documentation in `docs/source/commands3.rst` (swaggerknife)

**Description:**

In `docs/source/commands3.rst` for `swaggerknife`:
- `jsonknife json2swagger`: Provide more explanation or examples for custom usage of `--detector`, `--emitter`, `--emit` options.

---
### Docs: Complete documentation in `docs/source/library.rst`

**Description:**

The file `docs/source/library.rst` has incomplete sections for `dictknife` library usage:
- `loading`: Detail the modification system (e.g., `compact`, `flatten` from `dictknife/loading/modification/`) and specific loader/dumper options.
- `walkers`: Address the "todo: description about chains and operator and context,..." by providing this missing information.
- `accessor`: Show examples for other `Accessor` methods like `maybe_remove`, `exists`. Document the `Scope` class.

---
### Docs: Expand documentation in `docs/source/library2.rst` (jsonknife library)

**Description:**

The file `docs/source/library2.rst` should cover more `jsonknife` library components:
- Document classes like `Expander`, `Bundler`, `Separator`, `Resolver`.
- Document functions like `extract_example` from `dictknife.jsonknife`.
```
