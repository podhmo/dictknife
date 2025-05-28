# Code Analysis

## Suggestions for Outdated or Unnecessary Code and Modernization (Python 3.11)

- **File:** `dictknife/_sphinx.py`
  - **Suggestion:** The `LiteralIncludeReader.show_diff` function uses `os.path.basename`. Consider using `pathlib.Path(self.filename).name` for a more modern approach if `pathlib` is adopted more broadly.
  - **Suggestion:** The string formatting for `{"version": "0.0"}` could use an f-string if other parts are updated, though it's minor.

- **File:** `dictknife/accessing.py`
  - **Suggestion:** Class `Accessor`: Methods `assign`, `access`, `maybe_remove`, `exists`, `maybe_access`, `maybe_access_container` could benefit from more detailed type hints for parameters `d` and `path`.
  - **Suggestion:** Class `Scope`: The `accessor` parameter in `__init__` could default to `Accessor()` directly instead of `None` then `accessor or Accessor()`.
  - **Suggestion:** Function `dictmap`: The `mutable` parameter is boolean. Consider if `match` statements could simplify the `get_modifier` logic if it were more complex, though it's simple now.
  - **Suggestion:** `get_modifier`: The type hint `bool` for `mutable` is good.

- **File:** `dictknife/cliutils/__init__.py`
  - **Suggestion:** The string formatting `"\x1b[33m\x1b[1m{e.__class__.__name__}: {e}\x1b[0m".format(e=e)` can be converted to an f-string: `f"\x1b[33m\x1b[1m{e.__class__.__name__}: {e}\x1b[0m"`.

- **File:** `dictknife/cliutils/extraarguments.py`
  - **Suggestion:** Class `ExtraArgumentsParsers`:
    - String formatting like `"{self.prefix} arguments {name}".format(self=self, name=name)` can be changed to f-strings: `f"{self.prefix} arguments {name}"`. This applies to several places in the class.
    - The `parser_factory` parameter defaulting to `argparse.ArgumentParser` is fine.
    - `bind` method: `parser.format_help = format_help` is a form of monkeypatching. Ensure this is the intended and clearest way.
  - **Suggestion:** Consider using `Self` for `add_parser` if it were to return `self` (though it returns `p`).

- **File:** `dictknife/commands/_monkeypatch.py`
  - **Suggestion:** `apply_loading_format_extra_arguments_parser`:
    - String formatting `"{m.__name__} doesn't have setup_extra_parser() function".format(m=m)` can be an f-string.
    - The extensive use of `getattr` and manual argument parser manipulation is complex. It might be an area to review for simplification if `argparse` offers alternative extension mechanisms, though this pattern is sometimes necessary for deep customization.

- **File:** `dictknife/commands/dictknife.py`
  - **Suggestion:** Function `cat`:
    - `merge_method` parameter is used with `deepmerge`.
    - String formatting `logger.debug("merge: %s", f)` is an older style. `logging` supports direct formatting: `logger.debug("merge: %s", f)` is fine, or use f-strings if desired for consistency with other code: `logger.debug(f"merge: {f}")`.
  - **Suggestion:** Function `transform`:
    - `transform = lambda x: x  # NOQA` could be `transform = lambda x: x` or simply `transform = None` and check for `None` before calling.
    - String formatting in `import_symbol("dictknife.transform:{}".format(fn))` can be an f-string.
  - **Suggestion:** Function `diff`:
    - `output_format == "pair"`: The manual string padding and iteration could potentially be simplified, but it's specific to the desired output.
  - **Suggestion:** Function `shape`:
    - `typenames = [t.__name__ for t in row.type]` is good.
    - `d["example"] = ""  # xxx` - the comment `xxx` implies something to review.
  - **Suggestion:** Function `mkdict`:
    - `args.append(repr(x))` and string joining: This is for constructing a command-line-like string.
  - **Suggestion:** Function `main`:
    - `parser = argparse.ArgumentParser(formatter_class=type("_HelpFormatter", ...` is a way to create a custom formatter class on the fly.
    - `params.pop("subcommand")(**params)` is a common pattern for dispatching subcommands.
    - `module_path = "dictknife.loading.{}_{}".format(k.replace("_", "."), v)` and similar can be f-strings.
    - `RuntimeError("{}:setup() is not found".format(module_path))` can be an f-string.

- **File:** `dictknife/commands/jsonknife.py`
  - **Suggestion:** Most functions use string formatting with `.format()` which can be modernized to f-strings (e.g., `"{prefix}#/{name}".format(...)`).
  - **Suggestion:** Function `bundle`: The logic for `filename, jsonref = pairrsplit(filename, "#/")` and subsequent path manipulations with `os.path` could potentially use `pathlib` for a more object-oriented approach to paths, though `os.path` is perfectly functional.
  - **Suggestion:** Consider `Self` for methods in classes if they returned instances of themselves (though these are mostly standalone functions).

- **File:** `dictknife/commands/swaggerknife.py`
  - **Suggestion:** Function `merge`:
    - String formatting `"{where}#/{ns}/{name}".format(...)` and similar can be f-strings.
    - `RuntimeError("invalid style: {}".format(style))` can be an f-string.
  - **Suggestion:** Function `json2swagger`:
    - `"{}{}".format(name[0].upper(), name[1:])` (in `titleize` which is used here implicitly) is a common way to capitalize; f-strings are not necessarily better here.
    - The `CommentWriter` class builds strings; f-strings could be used if preferred.
  - **Suggestion:** Throughout the file, `.format()` can be replaced by f-strings.

- **File:** `dictknife/deepequal.py`
  - **Suggestion:** The `_Atom`, `_Collection`, `_Dict` classes are internal helpers for the comparison logic. They use `@reify`. If Python 3.8+ is a target, `@functools.cached_property` could replace `@reify`.
  - **Suggestion:** `repr(self.value)` and similar in `uid` methods: f-strings are not necessarily an improvement for `repr()`.

- **File:** `dictknife/deepmerge.py`
  - **Suggestion:** `ValueError("cannot merge dict and non-dict: left=%s, right=%s", left, right)` - this looks like it's missing `.format()`. It should be `ValueError(f"cannot merge dict and non-dict: left={left}, right={right}")` or similar.
  - **Suggestion:** `RuntimeError("unavailable method not in {METHODS!r}".format(METHODS=METHODS))` can be an f-string.
  - **Suggestion:** The `override` option is deprecated with a `warnings.warn`. This is good practice.

- **File:** `dictknife/diff/diff.py`
  - **Suggestion:** `_default_tostring` uses `json.dumps`. This is standard.

- **File:** `dictknife/diff/rows.py`
  - **Suggestion:** String formatting `"{}/{}".format(i, srow["name"])` can be f-strings.
  - **Suggestion:** The `_all_keys` function has manual list extension and iteration logic. It's a bit complex and might be simplified or further commented.

- **File:** `dictknife/guessing.py`
  - **Suggestion:** Class `Guesser`: Uses `re.compile().match`. This is standard.
  - **Suggestion:** `@reify` decorator is used. Consider `@functools.cached_property` if Python 3.8+ is targeted.

- **File:** `dictknife/jsonknife/__init__.py`
  - **Suggestion:** String formatting `"{prefix}#/{jsonref}".format(...)` and similar can be f-strings.
  - **Suggestion:** `ValueError("{efilename!r} is not json reference. (please <filename>#/<reference>)".format(efilename=efilename))` can be an f-string.

- **File:** `dictknife/jsonknife/_wrapped_exception.py`
  - **Suggestion:** Class `WrappedExceptionFactory`: `f"{self.prefix}{e.__class__.__name__}"` is already an f-string. Good.
  - **Suggestion:** Class `WrappedMixin`: `f"{super().__str__()} (where={tuple(reversed(self.stack))})"` is an f-string. Good.

- **File:** `dictknife/jsonknife/accessor.py`
  - **Suggestion:** `repr` formatting `"<{} localref={self.localref!r},  globalref={self.globalref!r}>".format(...)` can be an f-string.
  - **Suggestion:** `path_to_json_pointer` and `json_pointer_to_path` use string methods that are appropriate.

- **File:** `dictknife/jsonknife/bundler.py`
  - **Suggestion:** Flavor check `if flavor == "openapiv2":` etc. could be a `match` statement if there were more flavors or more complex logic per flavor, but for two options, `if/elif` is fine.
  - **Suggestion:** `ValueError("unexpected flavor {!r}, available flavors are ['openapiv2', 'openapiv3']".format(flavor))` can be an f-string.
  - **Suggestion:** Class `Scanner`: Uses `@reify`. Consider `@functools.cached_property`.
  - **Suggestion:** Class `Emitter`: String formatting in `logger.debug` and `sd["$ref"] = "#/{}".format(...)` can be f-strings.
  - **Suggestion:** Class `LocalrefFixer`: String formatting `"{}/{}".format(prefix, name)` can be f-strings.
  - **Suggestion:** Class `SimpleConflictFixer`: `RuntimeError("conficted. %r <-> %r" % (olditem.globalref, newitem.globalref))` is old-style formatting; use f-strings or `.format()`.

- **File:** `dictknife/jsonknife/example.py`
  - **Suggestion:** No specific outdated syntax noted, logic is fairly direct.

- **File:** `dictknife/jsonknife/expander.py`
  - **Suggestion:** Class `Expander`: Uses `@reify`. Consider `@functools.cached_property`.

- **File:** `dictknife/jsonknife/lifting.py`
  - **Suggestion:** Class `Handler`: `fullname` in `return_definition` uses `.format()`. Can be f-string.

- **File:** `dictknife/jsonknife/merge.py`
  - **Suggestion:** Seems fine. Merge logic is specific.

- **File:** `dictknife/jsonknife/patch.py`
  - **Suggestion:** String formatting in `_merge` like `"/{{prefix}}/{{subpath}}".format(...)` can be f-strings. Note the double curly braces to escape them in f-strings if a literal brace is needed: `f"/{{{prefix}}}/{{{subpath}}}"`.

- **File:** `dictknife/jsonknife/relpath.py`
  - **Suggestion:** Extensive use of `os.path`. This is functional. `pathlib` is an alternative for a more object-oriented style if preferred.
  - **Suggestion:** String formatting `filepath = "{}#{}".format(filepath, jsref)` can be f-strings.

- **File:** `dictknife/jsonknife/resolver.py`
  - **Suggestion:** `ValueError("invalid query {!r}".format(query))` can be an f-string.
  - **Suggestion:** `repr` formatting `<FileResolver {!r}>`.format(self.filename)` can be an f-string.
  - **Suggestion:** `@reify` is used. Consider `@functools.cached_property`.

- **File:** `dictknife/jsonknife/separator.py`
  - **Suggestion:** String formatting `"{}{}".format(filepath, def_item["$ref"])` can be f-strings.
  - **Suggestion:** Uses `os.path`. `pathlib` is an alternative.

- **File:** `dictknife/langhelpers.py`
  - **Suggestion:** `sys.version_info` check for `make_dict`. If Python < 3.6 is no longer supported, this can be simplified to `make_dict = dict`. If 3.6 is the minimum but 3.7+ features (ordered dict by default) are desired, this alias might still be useful for clarity or future change. Standard dicts are ordered since 3.7 (CPython 3.6).
  - **Suggestion:** `@reify` decorator. Consider `@functools.cached_property`.

- **File:** `dictknife/loading/__init__.py`
  - **Suggestion:** `os.environ.get("DICTKNIFE_LOAD_FORMAT")`: Environment variable usage is a feature.
  - **Suggestion:** String formatting in `dumpfile` for `FileNotFoundError` retry logic can use f-strings if paths are included in messages.
  - **Suggestion:** `get_unknown`: `sys.modules[loader.__module__]` is introspection.

- **File:** `dictknife/loading/_gsuite.py`
  - **Suggestion:** Uses `typing.Optional`, `typing.Sequence`. For Python 3.9+, these can be `| None` and `collections.abc.Sequence` (or just `list`/`tuple` if specific).
  - **Suggestion:** String formatting in `get_credentials_failback_webbrowser` can use f-strings.
  - **Suggestion:** Uses `@reify`. Consider `@functools.cached_property`.

- **File:** `dictknife/loading/_lazyimport.py`
  - **Suggestion:** Uses `@reify`. Consider `@functools.cached_property`.
  - **Suggestion:** String formatting `"... ({!r})".format(e)` can be an f-string.
  - **Suggestion:** `_fake_yaml` class: `json.dump` arguments `indent=2`, `ensure_ascii=False` are fine.

- **File:** `dictknife/loading/_yaml.py`
  - **Suggestion:** Uses `ruamel.yaml`. Specific to that library's API.

- **File:** `dictknife/loading/csv.py`
  - **Suggestion:** `sys.version_info` check for `make_dictReader`. If Python < 3.6 is no longer supported, this can be simplified.
  - **Suggestion:** String formatting `"... err=%r", self.line_num, e` in logger can be `logger.info("... err=%r", self.line_num, e, exc_info=e)` or f-string.

- **File:** `dictknife/loading/env.py`
  - **Suggestion:** String formatting in `load` (commented out or via logger) can be f-strings.

- **File:** `dictknife/loading/json.py`
  - **Suggestion:** Fairly standard use of `json` module.

- **File:** `dictknife/loading/md.py`
  - **Suggestion:** String formatting ` "| {} |".format(...)` can be f-strings.

- **File:** `dictknife/loading/modification/compact.py`
  - **Suggestion:** Uses `functools.partial`. Standard.

- **File:** `dictknife/loading/modification/flatten.py`
  - **Suggestion:** Wraps dumper functions. Standard.

- **File:** `dictknife/loading/modification/unescape_unicode.py`
  - **Suggestion:** `s.encode("utf-8").decode("unicode-escape")` is specific for the unescaping logic.

- **File:** `dictknife/loading/modification/unescape_url.py`
  - **Suggestion:** Uses `urllib.parse.unquote_plus`. Standard.

- **File:** `dictknife/mkdict.py`
  - **Suggestion:** Class `_AccessorSupportList`: Complex list/dict creation logic.
  - **Suggestion:** `sys.version_info[:2] < (3, 6)` check for `shlex` monkeypatch. If <3.6 not supported, this can be removed.
  - **Suggestion:** The `shlex` monkeypatch itself is a significant piece of legacy compatibility code.

- **File:** `dictknife/naming.py`
  - **Suggestion:** String formatting `r"\1{}\2".format(separator)` and `"{}{}".format(name[0].upper(), name[1:])` can be f-strings.

- **File:** `dictknife/operators.py`
  - **Suggestion:** String formatting `"<{{self.__class__.__name__}} args={{args!r}}>".format(self=self, args=self.args)` can be f-strings. Note the double curly braces.

- **File:** `dictknife/pp.py`
  - **Suggestion:** Uses `json.dump`. Standard.

- **File:** `dictknife/shape.py`
  - **Suggestion:** String formatting `"?{{}}".format(...)` can be f-strings.

- **File:** `dictknife/swaggerknife/flatten.py`
  - **Suggestion:** Logic seems straightforward.

- **File:** `dictknife/swaggerknife/json2swagger.py`
  - **Suggestion:** `ValueError("unsupported for {!r}".format(val))` can be an f-string.
  - **Suggestion:** `"{}{}".format(name[0].upper(), name[1:])` (titleize) can be f-strings, though current form is fine.
  - **Suggestion:** String formatting in `Emitter.make_array_schema` etc. can be f-strings.

- **File:** `dictknife/swaggerknife/migration.py`
  - **Suggestion:** Uses `@reify`. Consider `@functools.cached_property`.
  - **Suggestion:** String formatting in `diff` method like `"before:{{filename}}".format(filename=filename)` can be f-strings.
  - **Suggestion:** `tempfile.mkdtemp(prefix="migration-", dir=where)`: Standard library usage.

- **File:** `dictknife/transform.py`
  - **Suggestion:** String formatting `"{}{}{}".format(...)` can be f-strings.

- **File:** `docs/source/conf.py`
  - **Suggestion:** Standard Sphinx configuration file. `%` formatting for `version` and `release` is typical here.

- **File:** `fastentrypoints.py`
  - **Suggestion:** This is vendored code. It uses older string formatting (`%`) and `re.sub` for path manipulation. If kept, could be modernized, but the primary question is its necessity.

- **File:** `setup.py`
  - **Suggestion:** Uses `open().read().strip()` for version. Standard. `extras_require` uses dictionary literals. Standard. Entry points defined via string. Standard.

## Missing or Incomplete Docstrings and Comments

- **File:** `dictknife/__init__.py`
  - **Docstring:** Module-level docstring is missing.
  - **Comment:** Briefly explain why these specific symbols are exposed via `__all__` (implicitly) or what the main purpose of `dictknife` is.

- **File:** `dictknife/_sphinx.py`
  - **Docstring:** Module-level docstring is missing.
  - **Docstring:** Function `setup` is missing a docstring explaining its purpose as a Sphinx extension setup.
  - **Docstring:** Method `show_diff` (monkeypatched) lacks a docstring explaining what it does with the diff.
  - **Comment:** Add a comment explaining why `LiteralIncludeReader.show_diff` is being monkeypatched.

- **File:** `dictknife/accessing.py`
  - **Docstring:** Module-level docstring is missing.
  - **Docstring:** Class `Accessor`: `__init__` could detail `make_dict` and `zero_value` params more. Methods like `assign`, `access`, `maybe_remove`, `exists`, `maybe_access`, `maybe_access_container` need docstrings explaining parameters (esp. `d`, `path`) and return values or side effects.
  - **Docstring:** Class `Scope`: `__init__`, `get`, `__getitem__`, `push`, `pop`, `scope` methods need docstrings.
  - **Docstring:** Classes `ImmutableModifier`, `MutableModifier` methods (`modify_list`, `modify_dict`, `modify_dict_with_keys`) need docstrings.
  - **Docstring:** Function `dictmap` needs a docstring explaining `fn`, `x`, `mutable`, `with_key`.
  - **Docstring:** Function `get_modifier` needs a docstring.
  - **Comment:** `missing = object()` could have a comment explaining its use as a sentinel.

- **File:** `dictknife/cliutils/__init__.py`
  - **Docstring:** Module-level docstring is missing.
  - **Docstring:** Function `traceback_shortly` needs a docstring explaining its purpose as a context manager for CLI error handling.

- **File:** `dictknife/cliutils/extraarguments.py`
  - **Docstring:** Module-level docstring is missing.
  - **Docstring:** Class `ExtraArgumentsParsers`: `__init__` needs to detail its parameters. Methods `add_parser`, `as_epilog`, `bind`, `parse_args`, `_transform_args`, `_parse_args`, `_show_warnigs` need docstrings.
  - **Comment:** `bind(parser)  # xxx: side effect` - expand on this side effect.

- **File:** `dictknife/commands/__init__.py`
  - **Docstring:** Module-level docstring is missing (though it's an `__init__.py`, so might be intentional if it's just for package structure).

- **File:** `dictknife/commands/_monkeypatch.py`
  - **Docstring:** Module-level docstring is missing.
  - **Docstring:** Functions `apply_rest_arguments_as_extra_arguments_parser` and `apply_loading_format_extra_arguments_parser` need comprehensive docstrings explaining what they patch and why.
  - **Comment:** The `xxx:` comments (e.g., `xxx: side effect`, `xxx: Action has state`) should be elaborated or resolved.
  - **Comment:** Explain the rationale for choices like `if f == "markdown": continue # xxx:`.

- **File:** `dictknife/commands/dictknife.py`
  - **Docstring:** Module-level docstring could briefly state it's the main CLI for `dictknife`.
  - **Docstring:** Function `_open` is missing a docstring.
  - **Docstring:** Function `cat` has a brief one-liner from `add_parser`, but could be more detailed about params like `merge_method`, `slurp`, `extra`.
  - **Docstring:** Function `transform`: Parameters `code`, `functions` could be explained more.
  - **Docstring:** Function `diff`: Parameters like `normalize`, `skip_empty`, `n`, `output_format` choices need explanation.
  - **Docstring:** Function `shape`: Parameters `squash`, `skiplist`, `with_type`, `with_example`, `full` need explanation.
  - **Docstring:** Function `shrink`: Parameters like `max_length_of_string`, `cont_suffix`, `with_tail` need explanation.
  - **Docstring:** Function `mkdict`: Parameters `separator`, `delimiter`, `squash`, `extra` need explanation.
  - **Docstring:** Function `main`: Overall CLI setup function, could have a brief docstring.
  - **Comment:** `parser.print_usage = parser.print_help  # hack` - explain this hack.
  - **Comment:** `sparser.print_help = print_help` (for transform command) - explain why this custom help is needed.

- **File:** `dictknife/commands/jsonknife.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `cut`, `deref` (and its deprecation notice is good), `select`, `bundle`, `separate`, `examples` need more detailed docstrings for their parameters.
  - **Docstring:** `main` function could have a brief docstring.
  - **Comment:** `parser.print_usage = parser.print_help  # hack` - explain this hack.

- **File:** `dictknife/commands/swaggerknife.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `tojsonschema`, `json2swagger`, `merge`, `flatten` need more detailed docstrings for their parameters.
  - **Docstring:** `main` function could have a brief docstring.
  - **Comment:** `parser.print_usage = parser.print_help  # hack` - explain this hack.
  - **Comment:** `info = detector.detect(data, name, info=info)` - the re-assignment of `info` could be clarified.

- **File:** `dictknife/deepequal.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `deepequal`: Explain `normalize` parameter.
  - **Docstring:** Function `sort_flexibly`: Explain what "flexibly" means here.
  - **Docstring:** Functions `_wrap`, `_unwrap`, `halfequal` need docstrings.
  - **Docstring:** Internal classes `_Atom`, `_Collection`, `_Dict` and their methods need docstrings if their logic is complex enough to warrant it for maintainers.
  - **Comment:** `_NONE = _Atom(None)` - explain its purpose as a sentinel or placeholder.

- **File:** `dictknife/deepmerge.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `_deepmerge_extend`, `_deepmerge_replace`, `_deepmerge_merge` need docstrings explaining their specific merge strategies.
  - **Docstring:** Function `deepmerge`: The `override` parameter is deprecated (good), `method` parameter and its choices should be clearly documented. The docstring refers to `METHODS` which is good.

- **File:** `dictknife/diff/__init__.py`
  - **Docstring:** Module-level docstring missing.
  - **Comment:** Explain why `make_jsonpatch` is re-exported here.

- **File:** `dictknife/diff/diff.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `diff`: Parameters `tostring`, `n`, `terminator`, `normalize`, `sort_keys` need explanation.
  - **Docstring:** Function `_default_tostring` needs a docstring.

- **File:** `dictknife/diff/rows.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `diff_rows`: Parameters `diff_key`, `normalize` need explanation.
  - **Docstring:** Function `_all_keys` needs a docstring explaining its logic for merging key lists.

- **File:** `dictknife/guessing.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `Guesser`: `__init__` needs docstring for `modifier`, `default`. Methods `is_bool`, `is_float`, `is_int`, `is_list`, `is_dict`, `guess`, `guess_default` need docstrings.
  - **Docstring:** Function `guess`: Parameters `guesser_factory`, `default`, `mutable` need explanation.

- **File:** `dictknife/jsonknife/__init__.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `expand`, `bundle`, `separate` need docstrings explaining their parameters and purpose.

- **File:** `dictknife/jsonknife/_wrapped_exception.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `WrappedExceptionFactory`: `__init__` (prefix, mixin_class), `__call__` (e, where) need docstrings.
  - **Docstring:** Class `WrappedMixin`: `stack` property and `__str__` need docstrings.
  - **Comment:** `wrap_exception = WrappedExceptionFactory(prefix="Ex")` - why "Ex"?

- **File:** `dictknife/jsonknife/accessor.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `AccessingMixin`: Methods need docstrings clarifying `doc`, `a` (Accessor instance) parameters.
  - **Docstring:** Class `CachedItem`: `__init__` needs docstring for its parameters.
  - **Docstring:** Functions `path_to_json_pointer`, `json_pointer_to_path`, `access_by_json_pointer`, `assign_by_json_pointer`, `maybe_remove_by_json_pointer` need docstrings.
  - **Docstring:** Class `StackedAccessor`: `__init__`, `resolver` property, `access`, `_access`, `pop_stack`, `push_stack`, `as_json` need docstrings.
  - **Docstring:** Class `CachedItemAccessor`: `__init__`, `_access` need docstrings.
  - **Comment:** `is_ref = operators.And(["$ref", _is_string])` - comment on what kind of structure this detects.

- **File:** `dictknife/jsonknife/bundler.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `create_scanner_factory_from_flavor`: Explain `flavor`.
  - **Docstring:** Class `Bundler`: `__init__` (resolver, strict, scanner_factory), `scanner` property, `emitter` property, `bundle` method need docstrings.
  - **Docstring:** Class `Scanner`: `__init__`, `ref_walking`, `conflict_fixer`, `scan`, `_scan_toplevel`, `_scan_refs` need docstrings.
  - **Docstring:** Class `Emitter`: `__init__`, `ref_walking`, `get_item_by_globalref`, `get_item_by_localref`, `emit`, `replace_ref` need docstrings.
  - **Docstring:** Class `LocalrefFixer`: `__init__`, `guess_name`, `fix_localref` need docstrings.
  - **Docstring:** Class `SimpleConflictFixer`: `__init__`, `is_same_item`, `fix_conflict` need docstrings.
  - **Comment:** `localref_fixer=LocalrefFixer(default_position="definitions")` - explain the meaning of "default_position".
  - **Comment:** `xxx:` comments need addressing.

- **File:** `dictknife/jsonknife/example.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `State`: `__init__` needs docstring.
  - **Docstring:** Functions `_extract`, `_extract_object`, `_extract_array` need docstrings.
  - **Docstring:** Function `extract`: `limit` parameter needs explanation. The main docstring "example value from swagger's example and default" is good but could be module-level.

- **File:** `dictknife/jsonknife/expander.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `detect_circur_reference`: Explain `doc`, `d`. (It's `circular` not `circur`).
  - **Docstring:** Class `Expander`: `__init__`, `ref_walking`, `access`, `expand`, `expand_subpart` need docstrings.

- **File:** `dictknife/jsonknife/lifting.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `Handler`: `__init__`, `full_name`, `add_name`, `add_array_item`, `pop_name`, `save_object`, `save_array` need docstrings.
  - **Docstring:** Class `Flattener`: `__init__`, `extract`, `_extract`, `return_definition`, `on_object_has_properties`, `on_array_has_items` need docstrings.

- **File:** `dictknife/jsonknife/merge.py`
  - **Docstring:** Module-level docstring could mention it implements RFC7396.
  - **Docstring:** Function `merge`: Explain `d`, `q`, `make_dict`.

- **File:** `dictknife/jsonknife/patch.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** `diff` namedtuple could have a comment.
  - **Docstring:** Function `make_jsonpatch`: Explain `src`, `dst`, `verbose`.
  - **Docstring:** Function `_merge` needs docstring.
  - **Docstring:** Class `_Walker`: `__init__`, `walk`, `_walk_list`, `_walk_dict`, `_walk_atom` need docstrings.
  - **Comment:** `self.move_map = {}  # todo:` - elaborate on this `todo`.

- **File:** `dictknife/jsonknife/relpath.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `fixpath`, `fixref`, `relref`, `normpath` have good examples in docstrings, but could also have a brief explanation of parameters `where`, `to`.
  - **Comment:** `# todo: move module` - where should it be moved, and why?

- **File:** `dictknife/jsonknife/resolver.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `OneDocResolver`: `__init__`, `resolve` need docstrings.
  - **Docstring:** Class `ExternalFileResolver`: `__init__`, `name` property, `doc` property, `new`, `resolve_pathset`, `resolve`, `resolve_subresolver`, `path_list` need docstrings.
  - **Docstring:** Class `ROOT`: Explain its purpose as a sentinel or root marker.
  - **Docstring:** Function `get_resolver`: Explain parameters.
  - **Docstring:** Function `build_subset`: Explain parameters.
  - **Comment:** `get_resolver_from_filename = get_resolver` - comment on backward compatibility.

- **File:** `dictknife/jsonknife/separator.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `_with_format`: Explain parameters.
  - **Docstring:** Class `Separator`: `__init__`, `scanner`, `emitter`, `separate` need docstrings.
  - **Docstring:** Class `Scanner`: `__init__`, `ref_walker`, `scan`, `_collect_def_items`, `_collect_namespaces` need docstrings.
  - **Docstring:** Class `Emitter`: `__init__`, `ref_walker`, `emit`, `_emit`, `emit_main` need docstrings.
  - **Comment:** `# todo: support ~0 and ~1`, `# todo: multiple files input`, etc. should be elaborated or tracked as issues.

- **File:** `dictknife/langhelpers.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** `make_dict` conditional import: A comment explaining why `OrderedDict` was used for older Python would be helpful.
  - **Docstring:** Functions `pairsplit`, `pairrsplit` need docstrings.
  - **Docstring:** Class `reify`: Needs a docstring explaining it's a cached property decorator.
  - **Docstring:** Functions `as_jsonpointer`, `as_path_node` need docstrings.
  - **Comment:** Backward compatibility comments for re-exported symbols are good.

- **File:** `dictknife/loading/__init__.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `Loader`: `__init__`, `add_format`, `loads`, `load`, `loadfile` need docstrings.
  - **Docstring:** Class `Dumper`: `__init__`, `add_format`, `dumps`, `dump`, `dumpfile` need docstrings.
  - **Docstring:** Class `Dispatcher`: `__init__`, `guess_format`, `dispatch`, `add_format` need docstrings.
  - **Docstring:** Functions `get_opener`, `get_formats`, `get_unknown`, `setup` need docstrings.
  - **Comment:** `unknown = "(unknown)"` - explain its role.

- **File:** `dictknife/loading/_gsuite.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `get_credentials`, `get_credentials_failback_webbrowser` need detailed docstrings for parameters and what they do, especially regarding auth flow.
  - **Docstring:** Class `MemoryCache`: `__init__`, `get`, `set`, `is_empty` need docstrings.
  - **Docstring:** Function `_get_discovery_cache` needs docstring.
  - **Docstring:** Class `Loader`: `__init__`, `cache`, `_save_cache`, `service`, `load_sheet` need docstrings.
  - **Comment:** Default paths like `DEFAULT_CREDENTIALS_PATH` could have comments on how users should set them up.
  - **Comment:** Scope constants `SCOPE`, `SCOPE_READONLY` explain their purpose.

- **File:** `dictknife/loading/_lazyimport.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `LoadingModule`: Properties `json`, `toml`, `csv`, `gsuite`, `yaml` should explain they are lazy-loading properties.
  - **Docstring:** Inner `_TomlAdaptor` and `_fake_yaml` classes and their methods (`load`, `dump`) need docstrings.
  - **Comment:** `m = LoadingModule()` - explain that `m` is the global lazy loader instance.

- **File:** `dictknife/loading/_yaml.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `load`, `dump` should explain `typ` and other `ruamel.yaml` specific params if they are not directly passed through.
  - **Comment:** `_pool = {}  # xxx: memory leak` - This is a critical comment and needs to be addressed or explained in detail.

- **File:** `dictknife/loading/csv.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `setup_extra_parser` needs docstring.
  - **Docstring:** Function `load`: Explain `_registry`, `create_reader_class`.
  - **Docstring:** Function `dump`: Explain `fullscan`.
  - **Docstring:** Function `_create_reader_class`: Explain `retry` and the purpose of the custom DictReader.

- **File:** `dictknife/loading/env.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `emit_environ`: Explain `structure`, `parse`.
  - **Docstring:** Function `parse_value`: Explain `v`, `builtins`.
  - **Docstring:** Function `load`: Explain `parse`.

- **File:** `dictknife/loading/json.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `load`: Explain `object_pairs_hook`.
  - **Docstring:** Function `dump`: Explain `default`.

- **File:** `dictknife/loading/md.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `load`: Explain `null_value`.
  - **Docstring:** Function `dump`: Explain `null_value`.

- **File:** `dictknife/loading/modification/__init__.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `_get_modifications_history`, `is_used`, `use` need docstrings.

- **File:** `dictknife/loading/modification/compact.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `setup` needs docstring explaining it modifies JSON dumping to be compact.

- **File:** `dictknife/loading/modification/flatten.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `setup` needs docstring explaining it modifies dumpers to flatten output.
  - **Docstring:** Inner `wrap` and `call` functions could have brief docstrings or comments.

- **File:** `dictknife/loading/modification/unescape_unicode.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `setup` needs docstring explaining it modifies loaders to unescape Unicode.
  - **Docstring:** Inner `wrap` and `call` functions could have brief docstrings or comments on the unescaping logic.

- **File:** `dictknife/loading/modification/unescape_url.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `setup` needs docstring explaining it modifies loaders to unescape URLs.
  - **Docstring:** Inner `wrap` and `call` functions could have brief docstrings or comments on the unescaping logic.

- **File:** `dictknife/loading/raw.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `load`, `dump`, `setup_extra_parser` need docstrings.

- **File:** `dictknife/loading/spreadsheet.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** `Guessed` namedtuple fields could be commented.
  - **Docstring:** Function `guess`: Explain `pattern`, `sheet_rx`.
  - **Docstring:** Function `load`: Explain `pattern`.
  - **Docstring:** Function `dump`: Current `NotImplementedError` is clear.
  - **Docstring:** Function `not_open` (context manager): Explain its purpose.
  - **Comment:** `_loader = None` - explain why it's a global.

- **File:** `dictknife/loading/toml.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `load`, `dump` need docstrings.

- **File:** `dictknife/loading/tsv.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** `load` and `dump` (partials) should have docstrings indicating they are for TSV.

- **File:** `dictknife/loading/yaml.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `load`, `dump` should clarify `ruamel.yaml` specific parameters if any are exposed or defaulted differently.

- **File:** `dictknife/mkdict.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `_AccessorSupportList`: `__init__`, `assign`, `maybe_access` need docstrings explaining their specialized list/dict creation logic.
  - **Docstring:** Function `mkdict`: The existing detailed docstring is great. Parameters `accessor`, `guess`, `shared` could be briefly mentioned.
  - **Docstring:** Function `_mkdict`: Internal, but complex; could benefit from a docstring explaining its recursive parsing logic and parameters.
  - **Docstring:** Function `tokenize`: Needs a docstring.
  - **Comment:** The `shlex` monkeypatch for Python <3.6 should be clearly commented as such, explaining why it's needed.

- **File:** `dictknife/naming.py`
  - **Docstring:** Module-level docstring missing, could explain it provides various string case conversion utilities.
  - **Docstring:** Functions `normalize`, `snakecase`, `kebabcase`, `camelcase`, `pascalcase`, `titleize`, `untitleize` need docstrings explaining what they convert from/to and parameters like `separator`, `other`, `soft`.

- **File:** `dictknife/operators.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `apply`: Explain `q`, `v`, `*args`.
  - **Docstring:** Function `repr` (meant for classes): Explain its general purpose.
  - **Docstring:** Classes `Regexp`, `Any`, `Not`, `Or`, `And` and their `__init__`, `__call__` methods need docstrings.
  - **Comment:** `ANY = Any()` - explain its use as a singleton.

- **File:** `dictknife/pp.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `pp`: Explain `d`, `out`.
  - **Docstring:** Function `indent` (context manager): Explain `n`, `prefix`, `newline`.

- **File:** `dictknife/shape.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** `Row` namedtuple fields could be commented.
  - **Docstring:** Class `_State`: `__init__`, `emit`, `count`, `__iter__` need docstrings.
  - **Docstring:** Class `Traverser`: `__init__`, `traverse`, `_traverse`, `_traverse_dict`, `_traverse_list`, `_traverse_atom` need docstrings.
  - **Docstring:** Function `_build_pathlist_from_state`: Explain parameters.
  - **Docstring:** Function `shape`: Explain parameters `traverse`, `aggregate`, `squash`, `skiplist`, `separator`, `transform`.

- **File:** `dictknife/swaggerknife/__init__.py`
  - **Docstring:** Module-level docstring missing (if it's more than just a package marker).

- **File:** `dictknife/swaggerknife/flatten.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `flatten`: Explain `data`, `replace`.

- **File:** `dictknife/swaggerknife/json2swagger.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `resolve_type`: Explain `val`.
  - **Docstring:** Class `NameResolver`: `__init__` and purpose.
  - **Docstring:** Function `make_signature`: Explain `info`.
  - **Docstring:** Class `Detector`: `make_info`, `detect`, `_detect` need docstrings.
  - **Docstring:** Class `Emitter`: `__init__`, `resolve_name`, `make_schema`, `make_array_schema`, `make_object_schema`, `make_primitive_schema`, `emit` need docstrings.
  - **Docstring:** Class `CommentWriter`: `__init__`, `write` need docstrings.

- **File:** `dictknife/swaggerknife/migration.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Functions `is_empty`, `is_empty_collection` need docstrings.
  - **Docstring:** Class `_Empty`: `__init__`, `unwrap` need docstrings.
  - **Docstring:** Class `Migration`: `__init__`, `transform`, `differ`, `updater`, `_prepare`, `_migrate_dryrun_and_diff`, `_migrate`, `migrate` need comprehensive docstrings for their roles and parameters.
  - **Docstring:** Class `_Differ`: `__init__`, `diff`, `before_data`, `after_data` need docstrings.
  - **Docstring:** Class `_Updater`: `__init__`, `name`, `resolvers`, `new_child`, `has`, `pop`, `pop_by_path`, `update`, `update_by_path`, `iterate_items` need docstrings.
  - **Comment:** `savedir = tempfile.mkdtemp(prefix="migration-", dir=where)  # xxx` - explain the `xxx`.

- **File:** `dictknife/transform.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Function `_make_key`: Explain parameters.
  - **Docstring:** Function `unflatten`: Explain `sep`, `accessor`.
  - **Docstring:** Function `_fix_unflatten_list`: Explain its purpose in `unflatten`.
  - **Docstring:** Function `flatten`: Explain `sep`.
  - **Docstring:** Function `rows`: Explain `kname`, `vname`.
  - **Docstring:** Function `update_keys`: Explain `key`, `coerce`.
  - **Docstring:** `str_dict`, `normalize_dict`, etc. (partials) should have brief docstrings indicating their function.
  - **Docstring:** Functions `only_num`, `only_str` need docstrings.
  - **Docstring:** Function `shrink`: Explain all parameters.

- **File:** `dictknife/walkers.py`
  - **Docstring:** Module-level docstring missing.
  - **Docstring:** Class `SimpleContext`: `push`, `pop`, `new_child`, `__call__` need docstrings.
  - **Docstring:** Class `PathContext`: `__init__`, `push`, `pop`, `__call__` need docstrings.
  - **Docstring:** Class `RecPathContext`: `__call__` needs docstring explaining difference from `PathContext`.
  - **Docstring:** Class `ContainerHandler`, `DataHandler`: `identity`, `__call__` need docstrings.
  - **Docstring:** Class `DictWalker`: `__init__`, `on_found`, `create_context`, `walk`, `_walk` need docstrings.
  - **Comment:** Backward compatibility aliases `LooseDictWalkingIterator` should be commented.

- **File:** `docs/source/conf.py`
  - **Docstring:** Standard module-level docstring for Sphinx conf is present.
  - **Comment:** Many default Sphinx comments are present; custom settings could be commented further if non-obvious.

- **File:** `fastentrypoints.py`
  - **Docstring:** Module-level docstring (copyright and explanation) is present.
  - **Docstring:** Function `get_args` (classmethod) needs a docstring.
  - **Docstring:** Function `main` needs a docstring.
  - **Comment:** The code is vendored; internal comments are as-is.

- **File:** `setup.py`
  - **Docstring:** Module-level docstring is missing (though often omitted in `setup.py`).
  - **Comment:** `long_description_content_type="text/markdown"` is good.
  - **Comment:** Classifiers are listed. Standard.
  - **Comment:** `extras_require` and `entry_points` are clear.
```
