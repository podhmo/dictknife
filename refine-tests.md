# Test Execution Output
```
============================= test session starts ==============================
platform linux -- Python 3.10.17, pytest-8.3.5, pluggy-1.5.0
rootdir: /app
plugins: anyio-4.9.0, cov-6.1.1, json-report-1.5.0, metadata-3.1.1
collected 54 items

dictknife/tests/cliutils/test_extraarguments.py ...                      [  5%]
dictknife/tests/jsonknife/test_accessor.py .                             [  7%]
dictknife/tests/jsonknife/test_deref.py ss                               [ 11%]
dictknife/tests/jsonknife/test_merge.py ..                               [ 14%]
dictknife/tests/jsonknife/test_patch.py .                                [ 16%]
dictknife/tests/jsonknife/test_relpath.py ....                           [ 24%]
dictknife/tests/jsonknife/test_wrapped_exception.py ..                   [ 27%]
dictknife/tests/loading/test_dump.py .                                   [ 29%]
dictknife/tests/loading/test_spreadsheet.py .                            [ 31%]
dictknife/tests/test_accessing_accessor.py .......                       [ 44%]
dictknife/tests/test_accessing_scope.py .......                          [ 57%]
dictknife/tests/test_deepequal.py ......                                 [ 68%]
dictknife/tests/test_deepmerge.py ...                                    [ 74%]
dictknife/tests/test_diff.py ..                                          [ 77%]
dictknife/tests/test_guessing.py ....                                    [ 85%]
dictknife/tests/test_iterator.py .                                       [ 87%]
dictknife/tests/test_mkdict.py ..                                        [ 90%]
dictknife/tests/test_operators.py ....                                   [ 98%]
dictknife/tests/test_shape.py .                                          [100%]

=============================== warnings summary ===============================
dictknife/tests/test_deepmerge.py::TestDeepMerge::test_it__override
dictknife/tests/test_deepmerge.py::TestDeepMerge::test_with_empty
dictknife/tests/test_deepmerge.py::TestDeepMerge::test_with_empty
  /app/dictknife/deepmerge.py:93: DeprecationWarning: override option is deprecated, will be removed, near future
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 52 passed, 2 skipped, 3 warnings in 0.21s ===================
```

# Test Code
## File: dictknife/tests/cliutils/test_extraarguments.py
```python
import textwrap
import unittest


class Tests(unittest.TestCase):
    maxDiff = None

    def _getTarget(self):
        from dictknife.cliutils.extraarguments import ExtraArgumentsParsers

        return ExtraArgumentsParsers

    def _makeOne(self):
        from argparse import ArgumentParser

        parser = ArgumentParser("cmd")
        target = self._getTarget()(parser, "--format", prefix="extra")
        sparser0 = target.add_parser("json")
        sparser0.add_argument("--sort-keys", action="store_true", help="sort keys")

        sparser1 = target.add_parser("toml")  # noqa
        return target

    def test_help_message(self):
        target = self._makeOne()
        expected = textwrap.dedent(
            """
        usage: cmd [-h]

        options:
          -h, --help  show this help message and exit

        extra arguments: (with --extra<option>)
          for --format=json:
            --sort-keys  sort keys
        """
        ).strip()

        actual = target.parser.format_help().strip()
        self.assertEqual(actual, expected)

    def test_parse_extra_arguments(self):
        target = self._makeOne()
        args = target.parse_args("json", ["--extra--sort-keys"])
        actual = vars(args)
        expected = {"sort_keys": True}
        self.assertEqual(actual, expected)

    def test_parse_extra_arguments_are_ignored(self):
        import contextlib
        from io import StringIO

        target = self._makeOne()

        with contextlib.redirect_stderr(StringIO()) as o:
            args = target.parse_args("toml", ["--extra--sort-keys"])
            actual = vars(args)
            expected = {}
            self.assertEqual(actual, expected)

        self.assertIn("--sort-keys", o.getvalue())
        self.assertIn("ignored", o.getvalue())
```
## File: dictknife/tests/jsonknife/test_accessor.py
```python
import unittest


class Tests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.accessor import access_by_json_pointer

        return access_by_json_pointer(*args, **kwargs)

    def test_it(self):
        # from: https://tools.ietf.org/html/rfc6901#section-5
        doc = {
            "foo": ["bar", "baz"],
            "": 0,
            "a/b": 1,
            "c%d": 2,
            "e^f": 3,
            "g|h": 4,
            "i\\j": 5,
            'k"l': 6,
            " ": 7,
            "m~n": 8,
        }

        candidates = [
            ("", doc),  # the whole document
            ("/foo", ["bar", "baz"]),
            ("/foo/0", "bar"),
            ("/", 0),
            ("/a~1b", 1),
            ("/c%d", 2),
            ("/e^f", 3),
            ("/g|h", 4),
            ("/i\\j", 5),
            ('/k"l', 6),
            ("/ ", 7),
            ("/m~0n", 8),
        ]

        for query, expected in candidates:
            with self.subTest(query=query, expected=expected):
                actual = self._callFUT(doc, query)
                self.assertEqual(actual, expected)
```
## File: dictknife/tests/jsonknife/test_deref.py
```python
import unittest
import textwrap
import ruamel.yaml
from io import StringIO


def loads(s):
    return ruamel.yaml.load(StringIO(s))


class Tests(unittest.TestCase):
    def _callFUT(self, doc):
        from dictknife.jsonknife.resolver import OneDocResolver
        from dictknife.jsonknife.expander import Expander

        expander = Expander(OneDocResolver(doc))
        return expander.expand()

    def assert_defs(self, actual, expected):
        from dictknife import diff

        self.assertEqual("\n".join(diff(expected, actual)), "")

    @unittest.skip("hmm")
    def test_self_recursion(self):
        defs_text = textwrap.dedent(
            """
        definitions:
          foo:
            type: string
          my:
            type: object
            properties:
              foo:
                $ref: "#/definitions/foo"
              bar:
                $ref: "#/definitions/my"
        """
        )
        defs = loads(defs_text)
        actual = self._callFUT(defs)
        expected = {
            "definitions": {
                "foo": {"type": "string"},
                "my": {
                    "type": "object",
                    "properties": {
                        "foo": {"type": "string"},
                        "bar": {"$ref": "#/definitions/my"},
                    },
                },
            }
        }
        self.assert_defs(actual, expected)

    @unittest.skip("hmm")
    def test_mutual_recursion(self):
        defs_text = textwrap.dedent(
            """
        definitions:
          text_assets:
            properties:
              asset:
                $ref: "#/definitions/asset_image"
          asset_image:
            properties:
              caption:
                $ref: "#/definitions/text_assets"
        """
        )
        defs = loads(defs_text)
        actual = self._callFUT(defs)
        expected = {
            "definitions": {
                "text_assets": {
                    "properties": {"asset": {"$ref": "#/definitions/asset_image"}}
                },
                "asset_image": {
                    "properties": {
                        "caption": {
                            "properties": {
                                "asset": {"$ref": "#/definitions/asset_image"}
                            }
                        }
                    }
                },
            }
        }
        self.assert_defs(actual, expected)
```
## File: dictknife/tests/jsonknife/test_merge.py
```python
import unittest


class Tests(unittest.TestCase):
    def _callFUT(self, d, q):
        from dictknife.jsonknife.merge import merge

        return merge(d, q)

    def test_empty(self):
        from dictknife import diff

        d = {}
        q = {"a": {"b": {"c": "d"}}}
        actual = self._callFUT(d, q)
        self.assertFalse(list(diff(actual, {"a": {"b": {"c": "d"}}})))

    def test_it(self):
        from dictknife import diff

        d = {
            "title": "Goodbye!",
            "author": {"givenName": "John", "familyName": "Doe"},
            "tags": ["example", "sample"],
            "content": "This will be unchanged",
        }

        q = {
            "title": "Hello!",
            "phoneNumber": "+01-123-456-7890",
            "author": {"familyName": None},
            "tags": ["example"],
        }

        expected = {
            "title": "Hello!",
            "author": {"givenName": "John"},
            "tags": ["example"],
            "content": "This will be unchanged",
            "phoneNumber": "+01-123-456-7890",
        }

        actual = self._callFUT(d, q)
        self.assertFalse(list(diff(expected, actual)))
```
## File: dictknife/tests/jsonknife/test_patch.py
```python
import unittest
import json
from collections import namedtuple


class Tests(unittest.TestCase):
    def _callFUT(self, src, dst):
        from dictknife.jsonknife.patch import make_jsonpatch

        return make_jsonpatch(src, dst)

    maxDiff = None

    def test(self):
        import jsonpatch

        C = namedtuple("C", "src, dst, want, skip_patch")
        cases = [
            C(src={"name": "foo"}, dst={"name": "foo"}, want=[], skip_patch=False),
            C(
                src={"name": "foo"},
                dst={"name": "bar"},
                want=[{"op": "replace", "path": "/name", "value": "bar"}],
                skip_patch=False,
            ),
            C(
                src={"name": "foo"},
                dst={},
                want=[{"op": "remove", "path": "/name"}],
                skip_patch=False,
            ),
            C(
                src={},
                dst={"name": "bar"},
                want=[{"op": "add", "path": "/name", "value": "bar"}],
                skip_patch=False,
            ),
            C(
                src={"point0": {"value": 10}},
                dst={"point1": {"value": 10}},
                # todo: move
                want=[
                    {"op": "remove", "path": "/point0"},
                    {"op": "add", "path": "/point1", "value": {"value": 10}},
                ],
                skip_patch=False,
            ),
            C(
                src={"point0": {"value": 10}},
                dst={"point0": {"value": 20}},
                want=[{"op": "replace", "path": "/point0/value", "value": 20}],
                skip_patch=False,
            ),
            C(
                src={"person": {"name": "foo", "age": 20, "type": "P"}},
                dst={"person": {"name": "bar", "nickname": "B", "type": "P"}},
                want=[
                    {"op": "replace", "path": "/person/name", "value": "bar"},
                    {"op": "remove", "path": "/person/age"},
                    {"op": "add", "path": "/person/nickname", "value": "B"},
                ],
                skip_patch=False,
            ),
            C(
                src=[{}, {"person": {"name": "foo", "age": 20, "type": "P"}}],
                dst=[{"person": {"name": "bar", "nickname": "B", "type": "P"}}, {}],
                want=[
                    {
                        "path": "/0/person",
                        "op": "add",
                        "value": {"name": "bar", "nickname": "B", "type": "P"},
                    },
                    {"path": "/1/person", "op": "remove"},
                ],
                skip_patch=False,
            ),
            C(
                src=None,
                dst=1,
                want=[{"op": "add", "path": "", "value": 1}],  # root is ""
                skip_patch=True,
            ),
            # runtime error
            # C(
            #     src={},
            #     dst=1,
            #     want=[{
            #         "op": "add",
            #         "path": "/",
            #         "value": 1
            #     }],
            #     skip_patch=True,
            # )
            C(
                src={"v": 1},
                dst={"v": [1]},
                want=[{"op": "replace", "path": "/v", "value": [1]}],
                skip_patch=False,
            ),
            C(
                src={"v": [1]},
                dst={"v": 1},
                want=[{"op": "replace", "path": "/v", "value": 1}],
                skip_patch=False,
            ),
            C(
                src={"name": "foo", "age": 20},
                dst={"person": {"name": "foo", "age": 20}},
                # move ?
                want=[
                    {
                        "op": "add",
                        "path": "/person",
                        "value": {"age": 20, "name": "foo"},
                    },
                    {"op": "remove", "path": "/age"},
                    {"op": "remove", "path": "/name"},
                ],
                skip_patch=False,
            ),
            C(
                src={"person": {"name": "foo", "age": 20}},
                dst={"name": "foo", "age": 20},
                # move ?
                want=[
                    {"op": "remove", "path": "/person"},
                    {"op": "add", "path": "/age", "value": 20},
                    {"op": "add", "path": "/name", "value": "foo"},
                ],
                skip_patch=False,
            ),
        ]

        for i, c in enumerate(cases):
            with self.subTest(i):
                got = list(self._callFUT(c.src, c.dst))
                if not c.skip_patch:
                    self.assertEqual(jsonpatch.JsonPatch(got).apply(c.src), c.dst)
                self.assertListEqual(
                    sorted([json.dumps(x, sort_keys=True) for x in got]),
                    sorted([json.dumps(x, sort_keys=True) for x in c.want]),
                )
```
## File: dictknife/tests/jsonknife/test_relpath.py
```python
import unittest
import os.path
import contextlib

here = os.path.abspath(os.path.dirname(__file__))


@contextlib.contextmanager
def _curdir(here):
    curdir = os.path.abspath(".")
    os.chdir(here)
    try:
        yield
    finally:
        os.chdir(curdir)


class fixRelpathTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.relpath import fixpath

        return fixpath(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple

        C = namedtuple("C", "relpath, where, to, expected")
        with _curdir(here):
            # yapf: disable
            candidates = [
                C(relpath="../a.html", expected="../a.html", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(relpath="../a.html", expected="a.html", where="foo/bar/b.html", to="foo/c.html"),
                C(relpath="../a.html", expected="foo/a.html", where="foo/bar/b.html", to="c.html"),
                C(relpath="a.html", expected="a.html", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(relpath="a.html", expected="bar/a.html", where="foo/bar/b.html", to="foo/c.html"),
                C(relpath="a.html", expected="foo/bar/a.html", where="foo/bar/b.html", to="c.html"),
                C(relpath="boo/a.html", expected="boo/a.html", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(relpath="boo/a.html", expected="bar/boo/a.html", where="foo/bar/b.html", to="foo/c.html"),
                C(relpath="boo/a.html", expected="foo/bar/boo/a.html", where="foo/bar/b.html", to="c.html"),
                C(relpath="a.html", expected="a.html", where="b.html", to="c.html"),
                C(relpath="a.html", expected="a.html", where="b.html", to=os.path.abspath(os.path.join(here, "c.html"))),
                C(relpath="a.html", expected="a.html", where=os.path.abspath(os.path.join(here, "b.html")), to="c.html"),
                C(relpath="a.html", expected="jsonknife/foo/bar/a.html", where="foo/bar/b.html", to="../c.html"),
                C(relpath="a.html", expected="tests/jsonknife/foo/bar/a.html", where="foo/bar/b.html", to="../../c.html"),
            ]
            # yapf: enable
            for c in candidates:
                with self.subTest(relpath=c.relpath, where=c.where, to=c.to):
                    got = self._callFUT(c.relpath, where=c.where, to=c.to)
                    self.assertEqual(got, c.expected)


class fixRefTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.relpath import fixref

        return fixref(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple

        C = namedtuple("C", "ref, where, to, expected")
        with _curdir(here):
            # yapf: disable
            candidates = [
                C(ref="a.html#/definitions/foo", expected="a.html#/definitions/foo", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(ref="#/definitions/foo", expected="b.html#/definitions/foo", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(ref="../a.html#/definitions/foo", expected="../a.html#/definitions/foo", where="foo/bar/b.html", to="foo/bar/c.html"),
                C(ref="../a.html#/definitions/foo", expected="a.html#/definitions/foo", where="foo/bar/b.html", to="foo/c.html"),
                C(ref="../a.html#/definitions/foo", expected="foo/a.html#/definitions/foo", where="foo/bar/b.html", to="c.html"),
            ]
            # yapf: enable
            for c in candidates:
                with self.subTest(ref=c.ref, where=c.where, to=c.to):
                    got = self._callFUT(c.ref, where=c.where, to=c.to)
                    self.assertEqual(got, c.expected)


class relRefTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.relpath import relref

        return relref(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple

        C = namedtuple("C", "ref, where, expected")
        with _curdir(here):
            # yapf: disable
            candidates = [
                C(ref="a.html#/definitions/foo", expected=("foo/bar/a.html", "/definitions/foo"), where="foo/bar/b.html"),
                C(ref="#/definitions/foo", expected=("foo/bar/b.html", "/definitions/foo"), where="foo/bar/b.html"),
                C(ref="../a.html#/definitions/foo", expected=("foo/a.html", "/definitions/foo"), where="foo/bar/b.html")
            ]
            # yapf: enable
            for c in candidates:
                with self.subTest(ref=c.ref, where=c.where):
                    got = self._callFUT(c.ref, where=c.where)
                    self.assertEqual(got, c.expected)


class NormpathTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.jsonknife.relpath import normpath

        return normpath(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple

        C = namedtuple("C", "relpath, where, expected")
        with _curdir(here):
            # yapf: disable
            candidates = [
                C(relpath="a.html", expected=os.path.join(here, "a.html"), where="."),
                C(relpath="a.html", expected=os.path.normpath(os.path.join(here, "../", "a.html")), where="../"),
                C(relpath="a.html", expected=os.path.normpath(os.path.join(here, "foo", "a.html")), where="foo/"),
            ]
            # yapf: enable
            for c in candidates:
                with self.subTest(relpath=c.relpath, where=c.where):
                    got = self._callFUT(c.relpath, where=c.where)
                    self.assertEqual(got, c.expected)


if __name__ == "__main__":
    unittest.main()
```
## File: dictknife/tests/jsonknife/test_wrapped_exception.py
```python
import unittest


class Tests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from dictknife.jsonknife._wrapped_exception import WrappedExceptionFactory

        return WrappedExceptionFactory(*args, **kwargs)

    def test_it(self):
        prefix = "Wrapped"
        create_class = self._makeOne(prefix=prefix)
        try:
            raise KeyError("hmm")
        except KeyError as e:
            e2 = create_class(e, where="<toplevel>")
            self.assertIsInstance(e2, KeyError)
            self.assertEqual(e2.args, e.args)

            self.assertEqual(e2.__class__.__name__, f"{prefix}KeyError")
            self.assertListEqual(e2.stack, ["<toplevel>"])
        else:
            self.fail("must be raised")

    def test_nested(self):
        create_class = self._makeOne()

        def f():
            try:
                return g()
            except Exception as e:
                raise create_class(e, where="f") from None

        def g():
            try:
                return h()
            except Exception as e:
                raise create_class(e, where="g") from None

        def h():
            raise MyException("hmm", context="oyoyo")

        class MyException(Exception):
            def __init__(self, val, *, context):
                super().__init__(val)
                self.context = context

        try:
            f()
        except Exception as e:
            self.assertIsInstance(e, MyException)
            self.assertListEqual(e.stack, ["g", "f"])
            self.assertEqual(getattr(e, "context", None), "oyoyo")
        else:
            self.fail("must be raised")
```
## File: dictknife/tests/loading/test_dump.py
```python
import unittest


class Tests(unittest.TestCase):
    def _getTarget(self):
        from dictknife import loading

        return loading.dumpfile

    def _callFUT(self, d, *, format):
        from contextlib import redirect_stdout
        from io import StringIO

        o = StringIO()
        with redirect_stdout(o):
            self._getTarget()(d, format=format)
        return o.getvalue()

    def test_dumpfile_with_iterator(self):
        from collections import namedtuple

        def iterator():
            yield {"name": "foo"}
            yield {"name": "bar"}
            yield {"name": "boo"}

        C = namedtuple("C", "format, output, input")
        # yapf: disable
        candidates = [
            C(format="csv", input=iterator(), output='''"name"\r\n"foo"\r\n"bar"\r\n"boo"\r\n'''),
            C(format="json", input=iterator(), output='''[\n  {\n    "name": "foo"\n  },\n  {\n    "name": "bar"\n  },\n  {\n    "name": "boo"\n  }\n]\n'''),
            C(format="yaml", input=iterator(), output='''- name: foo\n- name: bar\n- name: boo\n'''),
            C(format="md", input=iterator(), output='''| name |\n| :--- |\n| foo |\n| bar |\n| boo |\n'''),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(format=c.format):
                got = self._callFUT(c.input, format=c.format)
                self.assertEqual(got.strip(), c.output.strip())


if __name__ == "__main__":
    unittest.main()
```
## File: dictknife/tests/loading/test_spreadsheet.py
```python
import unittest
from collections import namedtuple


class GuessTests(unittest.TestCase):
    # https://developers.google.com/sheets/guides/concepts
    # example: https://docs.google.com/spreadsheets/d/1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps/edit#gid=0

    def _callFUT(self, *args, **kwargs):
        from dictknife.loading.spreadsheet import guess

        return guess(*args, **kwargs)

    def test_it(self):
        from dictknife.loading.spreadsheet import Guessed

        C = namedtuple("C", "input, output")
        # yapf: disable
        candidates = [
            C(
                input="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range=None, sheet_id=None)
            ),
            C(
                input="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps#/A1:B2",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range="A1:B2", sheet_id=None)
            ),
            C(
                input="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps#/sheet!A1:B2",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range="sheet!A1:B2", sheet_id=None)
            ),
            C(
                input="https://docs.google.com/spreadsheets/d/1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps/edit",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range=None, sheet_id=None)
            ),
            C(
                input="https://docs.google.com/spreadsheets/d/1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps/edit#gid=0",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range=None, sheet_id="0")
            ),
            C(
                input="https://docs.google.com/spreadsheets/d/1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps/edit?ranges=A1:B2#gid=0",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range="A1:B2", sheet_id="0")
            ),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(input=c.input):
                got = self._callFUT(c.input)
                self.assertEqual(got, c.output)
```
## File: dictknife/tests/test_accessing_accessor.py
```python
import unittest


class AssignTests(unittest.TestCase):
    def _callFUT(self, d, k, v):
        from dictknife import Accessor

        a = Accessor(make_dict=dict)
        return a.assign(d, k, v)

    def test_assign_dict(self):
        d = {}
        self._callFUT(d, ["x"], 1)
        expected = {"x": 1}
        self.assertDictEqual(d, expected)

    def test_assign_deeply(self):
        d = {}
        self._callFUT(d, [1, 2, 3, 4, 5, 6, 7, 8, 9], "foo")
        expected = {1: {2: {3: {4: {5: {6: {7: {8: {9: "foo"}}}}}}}}}
        self.assertDictEqual(d, expected)

    def test_assign_list(self):
        from collections import namedtuple

        C = namedtuple("C", "d, path, v, expected")
        cases = [
            C(d={"x": []}, path=["x", 0], v=1, expected={"x": [1]}),
            C(d={"x": []}, path=["x", 1], v=1, expected={"x": [None, 1]}),
            C(d={"x": [1, 2, 3]}, path=["x", 1], v=10, expected={"x": [1, 10, 3]}),
            C(
                d={"x": [1, 2, 3]},
                path=["x", 5],
                v=10,
                expected={"x": [1, 2, 3, None, None, 10]},
            ),
            C(
                d={"x": [1, 2]},
                path=["x", 1, "a"],
                v=10,
                expected={"x": [1, {"a": 10}]},
            ),
            C(
                d={"x": [1]},
                path=["x", 2, "a"],
                v=10,
                expected={"x": [1, {}, {"a": 10}]},
            ),
        ]
        for c in cases:
            with self.subTest(d=c.d, path=c.path, v=c.v):
                self._callFUT(c.d, c.path, c.v)
                self.assertDictEqual(c.d, c.expected)

    def test_assign_list2(self):
        d = {"x": [1]}
        self._callFUT(d, ["x", 2], 3)
        self._callFUT(d, ["x", 1, "a"], 10)
        expected = {"x": [1, {"a": 10}, 3]}
        self.assertDictEqual(d, expected)

    def test_assign_list_nested(self):
        from collections import namedtuple

        C = namedtuple("C", "d, path, v, expected")
        cases = [
            C(
                d={"x": []},
                path=["x", 0, "name"],
                v="foo",
                expected={"x": [{"name": "foo"}]},
            ),
            C(
                d={"x": []},
                path=["x", 1, "name"],
                v="foo",
                expected={"x": [{}, {"name": "foo"}]},
            ),
            C(
                d={"x": [{"name": "foo"}, {"name": "bar"}]},
                path=["x", 3, "name"],
                v="boo",
                expected={"x": [{"name": "foo"}, {"name": "bar"}, {}, {"name": "boo"}]},
            ),
        ]
        for c in cases:
            with self.subTest(d=c.d, path=c.path, v=c.v):
                self._callFUT(c.d, c.path, c.v)
                self.assertDictEqual(c.d, c.expected)

    def test_assign_list_nested2(self):
        d = {"x": [{"name": "foo"}]}
        self._callFUT(d, ["x", 3, "name"], "boo")
        self._callFUT(d, ["x", 1, "name"], "bar")
        expected = {"x": [{"name": "foo"}, {"name": "bar"}, {}, {"name": "boo"}]}
        self.assertDictEqual(d, expected)


class MaybeAccessTests(unittest.TestCase):
    def _callFUT(self, d, path):
        from dictknife import Accessor

        a = Accessor(make_dict=dict)
        return a.maybe_access(d, path)

    def test_maybe_access(self):
        from collections import namedtuple

        C = namedtuple("C", "d, path, expected")

        cases = [
            C(d=None, path=["k"], expected=None),
            C(d={"k": "v"}, path=["k"], expected="v"),
            C(d={"k": "v"}, path=["z"], expected=None),
            C(d=[], path=["k"], expected=None),
            C(d=[1], path=[0], expected=1),
            C(d=[1], path=[1], expected=None),
            C(d=[{"k": "v"}], path=[0, "k"], expected="v"),
            C(d=[{"k": "v"}], path=[0, "z"], expected=None),
        ]
        for c in cases:
            with self.subTest(d=c.d, path=c.path):
                got = self._callFUT(c.d, c.path)
                self.assertEqual(got, c.expected)


if __name__ == "__main__":
    unittest.main()
```
## File: dictknife/tests/test_accessing_scope.py
```python
import unittest


class Tests(unittest.TestCase):
    def _makeOne(self, init):
        from dictknife.accessing import Scope

        return Scope(init)

    def test_access(self):
        s = self._makeOne({"x": 10})
        self.assertEqual(s[["x"]], 10)

    def test_key_error(self):
        s = self._makeOne({})
        with self.assertRaises(KeyError):
            s[["x"]]

    def test_access_nested(self):
        s = self._makeOne({"x": {"y": 10}})
        self.assertEqual(s[["x", "y"]], 10)

    def test_access_stacked(self):
        s = self._makeOne({"x": 10})
        s.push({"x": 100})
        self.assertEqual(s[["x"]], 100)

    def test_access_stacked_nested(self):
        s = self._makeOne({"x": {"y": 10}})
        s.push({"x": {"y": 100}})
        self.assertEqual(s[["x", "y"]], 100)

    def test_access_stacked_nested__but_not_wrapped(self):
        s = self._makeOne({"x": {"y": 10}})
        s.push({"x": {"z": 100}})
        self.assertEqual(s[["x", "y"]], 10)

    def test_access_with_scope(self):
        s = self._makeOne({"x": {"y": 10}})
        with s.scope({"x": {"y": 100}}):
            self.assertEqual(s[["x", "y"]], 100)
        self.assertEqual(s[["x", "y"]], 10)
```
## File: dictknife/tests/test_deepequal.py
```python
# -*- coding:utf-8 -*-
import unittest


class ref(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == self.value


class DeepEqualTests(unittest.TestCase):
    def _callFUT(self, left, right, normalize):
        from dictknife import deepequal

        return deepequal(left, right, normalize=normalize)

    def test_it(self):
        d0 = {
            "a": ref(1),
            "b": {"x": {"i": ref(2)}, "y": {"j": ref(3)}},
        }
        d1 = {
            "a": ref(1),
            "b": {"x": {"i": ref(2)}, "y": {"j": ref(3)}},
        }
        self.assertEqual(ref(1), ref(1), msg="prepare")
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it2(self):
        d0 = {"color": {"type": "string", "enum": ["C", "M", "Y", "K"]}}
        d1 = {"color": {"type": "string", "enum": ["K", "Y", "M", "C"]}}
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it3(self):
        from dictknife.langhelpers import make_dict

        d0 = make_dict([("type", "string"), ("enum", ["C", "M", "Y", "K"])])
        d1 = make_dict([("type", "string"), ("enum", ["K", "Y", "M", "C"])])
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it4(self):
        d0 = [[[1, 2, 3], [1]], [[1, 2], [2, 3], [3, 4]]]
        d1 = [[[1], [1, 2, 3]], [[1, 2], [3, 4], [2, 3]]]
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it5(self):
        d0 = [
            {"xs": [{"name": "i"}, {"name": "j"}, {"name": "k"}]},
            {"xs": [{"name": "x"}, {"name": "y"}, {"name": "z"}]},
        ]
        d1 = [
            {"xs": [{"name": "y"}, {"name": "x"}, {"name": "z"}]},
            {"xs": [{"name": "k"}, {"name": "j"}, {"name": "i"}]},
        ]
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))

    def test_it6(self):
        d0 = [
            [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
            [[10, 11, 12], [11, 12, 13], [12, 13, 14]],
            [[100, 101, 102], [101, 102, 103], [102, 103, 104]],
        ]
        d1 = [
            [[11, 12, 13], [12, 13, 14], [10, 11, 12]],
            [[2, 3, 4], [1, 2, 3], [0, 1, 2]],
            [[102, 103, 104], [100, 101, 102], [101, 102, 103]],
        ]
        self.assertNotEqual(d0, d1)
        self.assertTrue(self._callFUT(d0, d1, normalize=True))
```
## File: dictknife/tests/test_deepmerge.py
```python
import unittest


class TestDeepMerge(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife import deepmerge

        return deepmerge(*args, **kwargs)

    def test_it(self):
        d0 = {
            "a": {"x": 1},
            "b": {"y": 10},
        }
        d1 = {"a": {"x": 1}, "b": {"z": 10}, "c": 100}
        actual = self._callFUT(d0, d1)
        expected = {"a": {"x": 1}, "b": {"y": 10, "z": 10}, "c": 100}
        self.assertEqual(actual, expected)
        self.assertNotEqual(actual, d0, msg="not modified!!")

    def test_it__override(self):
        d0 = {
            "name": "foo",
            "object": {"x": 1, "z": 1},
            "children": [1],
        }
        d1 = {
            "name": "bar",
            "object": {"y": 2, "z": 3},
            "children": [1, 2, 3],
            "a": {"b": {"c": "d"}},
        }
        actual = self._callFUT(d0, d1, override=True)
        expected = {
            "name": "bar",
            "object": {"x": 1, "y": 2, "z": 3},
            "children": [1, 2, 3],
            "a": {"b": {"c": "d"}},
        }
        self.assertEqual(actual, expected)
        self.assertNotEqual(actual, d0, msg="not modified!!")

    def test_with_empty(self):
        from collections import namedtuple

        C = namedtuple("C", "d0 d1 override expected")

        candidates = [
            C(d0={1: 10}, d1=None, override=False, expected={1: 10}),
            C(d0={1: 10}, d1={}, override=False, expected={1: 10}),
            C(d0={1: 10}, d1=None, override=True, expected={1: 10}),
            C(d0={1: 10}, d1={}, override=True, expected={1: 10}),
        ]
        for c in candidates:
            with self.subTest(d0=c.d0, d1=c.d1):
                actual = self._callFUT(c.d0, c.d1, override=c.override)
                self.assertEqual(actual, c.expected)
```
## File: dictknife/tests/test_diff.py
```python
import unittest
from collections import namedtuple, OrderedDict


class DiffRowsTests(unittest.TestCase):
    maxDiff = None

    def _callFUT(self, d0, right):
        from dictknife.diff import diff_rows

        return diff_rows(d0, right)

    def test_primitives(self):
        C = namedtuple("C", "left, right, expected, msg")
        # yapf: disable
        candidates = [
            C(msg="str, without diff",
              left={"x": "10"}, right={"x": "10"}, expected=[{"name": "x", "left": "10", "right": "10", "diff": ""}]),
            C(msg="str, with diff",
              left={"x": "10"}, right={"x": "100"}, expected=[{"name": "x", "left": "10", "right": "100", "diff": "  1  0+ 0"}]),
            C(msg="int, without diff",
              left={"x": 10}, right={"x": 10}, expected=[{"name": "x", "left": 10, "right": 10, "diff": 0}]),
            C(msg="int, with diff",
              left={"x": 10}, right={"x": 9}, expected=[{"name": "x", "left": 10, "right": 9, "diff": -1}]),
            C(msg="missing right",
              left={"x": 10}, right={}, expected=[{"name": "x", "left": 10, "right": None, "diff": None}]),
            C(msg="missing left",
              left={}, right={"x": 10}, expected=[{"name": "x", "left": None, "right": 10, "diff": None}]),
            C(msg="nested",
              left={"a": {"b": {"c": "foo"}}}, right={"a": {"b": {"c": "bar"}}}, expected=[{"name": "a/b/c", "left": "foo", "right": "bar", "diff": "- f- o- o+ b+ a+ r"}]),
            C(msg="list, primitive",
              left=[1, 2, 3], right=[2, 2, 2], expected=[
                  {"name": "0", "left": 1, "right": 2, "diff": 1},
                  {"name": "1", "left": 2, "right": 2, "diff": 0},
                  {"name": "2", "left": 3, "right": 2, "diff": -1},
              ]),
            C(msg="list, mismatched",
              left=[1, 2], right=[2], expected=[
                  {"name": "0", "left": 1, "right": 2, "diff": 1},
                  {"name": "1", "left": 2, "right": 0, "diff": -2},
              ]),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(msg=c.msg):
                got = self._callFUT(c.left, c.right)
                self.assertListEqual(got, c.expected)

    def test_it(self):
        left = OrderedDict(
            [
                ("x", 10),
                ("y", 100),
                (
                    "nested",
                    OrderedDict(
                        [
                            ("v1", 0),
                            ("v2", 1),
                            ("vs", [0, 1, 2, 3]),
                            ("vs2", [{"z": "foo"}]),
                        ]
                    ),
                ),
            ]
        )
        right = OrderedDict(
            [
                ("x", 10),
                ("y", 110),
                (
                    "nested",
                    OrderedDict(
                        [
                            ("v1", 10),
                            ("v2", -1),
                            ("vs", [0, 2, 2, 2]),
                            ("vs2", [{"z": "bar"}]),
                        ]
                    ),
                ),
            ]
        )
        got = self._callFUT(left, right)
        # yapf: disable
        expected = [
            {'name': 'x', 'left': 10, 'right': 10, 'diff': 0},
            {'name': 'y', 'left': 100, 'right': 110, 'diff': 10},
            {'name': 'nested/v1', 'left': 0, 'right': 10, 'diff': 10},
            {'name': 'nested/v2', 'left': 1, 'right': -1, 'diff': -2},
            {'name': 'nested/vs/0', 'left': 0, 'right': 0, 'diff': 0},
            {'name': 'nested/vs/1', 'left': 1, 'right': 2, 'diff': 1},
            {'name': 'nested/vs/2', 'left': 2, 'right': 2, 'diff': 0},
            {'name': 'nested/vs/3', 'left': 3, 'right': 2, 'diff': -1},
            {'name': 'nested/vs2/0/z', 'left': "foo", 'right': "bar", 'diff': '- f- o- o+ b+ a+ r'},
        ]
        # yapf: enable
        self.assertListEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
```
## File: dictknife/tests/test_guessing.py
```python
import unittest


class Tests(unittest.TestCase):
    def _callFUT(self, v, *args, **kwargs):
        from dictknife.guessing import guess

        return guess(v, *args, **kwargs)

    def test_nan(self):
        import math

        v = {"nan": "nan"}
        got = self._callFUT(v)
        self.assertTrue(math.isnan(got["nan"]))

    def test_it(self):
        v = [
            {
                "ints": [{"zero": "0", "nums": ["10", "-2000"]}],
                "floatnums": [
                    {"full": "0.1", "mini": ".1", "epsilon": "5.551115123125783e-17"}
                ],
                "infs": ["inf", "-inf"],
            }
        ]
        got = self._callFUT(v)
        expected = [
            {
                "floatnums": [
                    {"full": 0.1, "mini": 0.1, "epsilon": 5.551115123125783e-17}
                ],
                "ints": [{"nums": [10, -2000], "zero": 0}],
                "infs": [float("inf"), float("-inf")],
            }
        ]

        self.assertEqual(got, expected)

    def test_mutable(self):
        v = [{"1": 2}]
        got = self._callFUT(v, mutable=True)
        self.assertEqual(id(got), id(v), msg="list")
        self.assertEqual(id(got[0]), id(v[0]), msg="dict")
        self.assertEqual(id(got[0]["1"]), id(v[0]["1"]), msg="item")

    def test_immutable(self):
        v = [{"1": 2}]
        got = self._callFUT(v, mutable=False)
        self.assertNotEqual(id(got), id(v), msg="list")
        self.assertNotEqual(id(got[0]), id(v[0]), msg="dict")
        # self.assertEqual(id(got[0]["1"]), id(v[0]["1"]), msg="item")
```
## File: dictknife/tests/test_iterator.py
```python
import unittest


class IteratorTests(unittest.TestCase):
    def _getTargetClass(self):
        from dictknife import DictWalker

        return DictWalker

    def _makeOne(self, *args, **kwargs):
        return self._getTargetClass()(*args, **kwargs)

    def test_rec(self):
        from ..operators import ANY

        s = []

        d = {"a": {"b": {"a": {"b": {"a": {"b": 10}}}}}}
        iterator = self._makeOne([ANY, "b"])
        for path, value in iterator.iterate(d):
            s.append(value)
            for path, value in iterator.iterate(value):
                s.append(value)
                for path, value in iterator.iterate(value):
                    s.append(value)

        expected = [
            {"b": {"a": {"b": {"a": {"b": 10}}}}},
            {"b": {"a": {"b": 10}}},
            {"b": 10},
        ]

        self.assertEqual(s, expected)
```
## File: dictknife/tests/test_mkdict.py
```python
import unittest


class TokenizeTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.mkdict import tokenize

        return tokenize(*args, **kwargs)

    def test_it(self):
        from collections import namedtuple

        C = namedtuple("C", "input, output")
        candidates = [
            C(input="name foo", output=["name", "foo"]),
            C(input='"name" "foo"', output=["name", "foo"]),
            C(input="--name=foo", output=["name", "foo"]),
            C(input="--name foo", output=["name", "foo"]),
            C(input="--name 'foo=bar'", output=["name", "foo=bar"]),
            C(input="name foo; name bar", output=["name", "foo", ";", "name", "bar"]),
            C(
                input='"@x" val use "&x" dont-ref "&&x" "@@dont-assign" "v"',
                output=[
                    "@x",
                    "val",
                    "use",
                    "&x",
                    "dont-ref",
                    "&&x",
                    "@@dont-assign",
                    "v",
                ],
            ),
        ]
        for c in candidates:
            with self.subTest(input=c.input):
                got = self._callFUT(c.input)
                self.assertEqual(list(got), c.output)


class MkDictTests(unittest.TestCase):
    def _getTarget(self):
        from dictknife.mkdict import _mkdict

        return _mkdict

    def _callFUT(self, tokens):
        from dictknife.mkdict import _AccessorSupportList as Accessor
        from dictknife.guessing import guess

        return self._getTarget()(
            iter(tokens), delimiter=";", separator="/", accessor=Accessor(), guess=guess
        )

    def test_it(self):
        from collections import namedtuple

        C = namedtuple("C", "tokens, expected")
        # yapf: disable
        candidates = [
            C(tokens=["name", "foo"],
              expected={"name": "foo"}),
            C(tokens=["name", "foo", "age", "20"],
              expected={"name": "foo", "age": 20}),
            C(tokens=["name", "foo", "age", 20],
              expected={"name": "foo", "age": 20}),
            C(tokens=["name", "foo", "age", 20, "parent/name", "bar"],
              expected={"name": "foo", "age": 20, "parent": {"name": "bar"}}),
            C(tokens=["name", "foo", "age", 20, "parent/name", "bar", "parent/name", "*overwrite*"],
              expected={"name": "foo", "age": 20, "parent": {"name": "*overwrite*"}}),
            C(tokens=["name", "foo", ";", "name", "bar"],
              expected=[{"name": "foo"}, {"name": "bar"}]),
            C(tokens=[
                "@ob/name", "foo", "@ob/age", 40,
                "name", "bar", "age", 20, "parent", "&ob", ";",
                "name", "boo", "age", 18, "parent", "&ob"
            ],
              expected=[
                  {"name": "bar", "age": 20, "parent": {"name": "foo", "age": 40}},
                  {"name": "boo", "age": 18, "parent": {"name": "foo", "age": 40}},
              ]),
            # array
            C(tokens=["xs/", "a", "xs/", "b", "xs/", "c"],
              expected={"xs": ["a", "b", "c"]}),
            C(tokens=["xs//name", "a", "xs//name", "b", "xs//name", "c"],
              expected={"xs": [{"name": "a"}, {"name": "b"}, {"name": "c"}]}),
            C(tokens=["xs//name", "a", "xs/-1/age", 20, "xs//name", "b", "xs/-1/age", 10],
              expected={"xs": [{"name": "a", "age": 20}, {"name": "b", "age": 10}]}),
            C(tokens=["xs//name", "a", "xs/0/age", 20, "xs//name", "b", "xs/1/age", 10],
              expected={"xs": [{"name": "a", "age": 20}, {"name": "b", "age": 10}]}),
            C(tokens=["xs/0/name", "a", "xs/0/age", 20, "xs/1/name", "b", "xs/1/age", 10],
              expected={"xs": [{"name": "a", "age": 20}, {"name": "b", "age": 10}]}),
            C(tokens=["xs//name", "a", "xs//age", 20, "xs//name", "b", "xs//age", 10],
              expected={"xs": [{"name": "a"}, {"age": 20}, {"name": "b"}, {"age": 10}]}),
            C(tokens=["xs//name", "a", "xs/-1/age", 20, "xs/-1/name", "b", "xs/-1/age", 10],
              expected={"xs": [{"name": "b", "age": 10}]}),
            C(tokens=[
                "@xs/", "a", "@xs/", "b", "@xs/", "c",
                "ys", "&xs",
                "zs/0", "&xs/0", "zs/1", "&xs/-1"],
              expected={"ys": ["a", "b", "c"], "zs": ["a", "c"]}),
            C(tokens=[
                "@xs/0/name", "a", "@xs/0/age", 20, "@xs/1/name", "b", "@xs/1/age", 10,
                "names/", "&xs/0/name", "names/", "&xs/1/name"],
              expected={"names": ["a", "b"]}),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(tokens=c.tokens):
                got = self._callFUT(c.tokens)
                self.assertEqual(_to_dict(got), c.expected)


def _to_dict(d):
    if isinstance(d, (list, tuple)):
        return [_to_dict(x) for x in d]
    elif hasattr(d, "keys"):
        return {k: _to_dict(v) for k, v in d.items()}
    else:
        return d


if __name__ == "__main__":
    unittest.main()
```
## File: dictknife/tests/test_operators.py
```python
import unittest
from collections import namedtuple


class OperatorsTests(unittest.TestCase):
    def _callFUT(self, op, value):
        from dictknife.operators import apply

        return apply(op, value)

    def test_it(self):
        C = namedtuple("C", "value, expected")

        candidates = [
            C(value="x", expected=False),
            C(value="xx", expected=True),
            C(value="xxx", expected=False),
        ]

        op = "xx"
        for c in candidates:
            with self.subTest(op=op, value=c.value):
                actual = self._callFUT(op, c.value)
                self.assertEqual(actual, c.expected)

    def test_and(self):
        from ..operators import And

        C = namedtuple("C", "value, expected")

        candidates = [
            C(value="x", expected=False),
            C(value="xx", expected=False),
            C(value="xxx", expected=False),
        ]

        op = And(["x", "xx", "xxx"])
        for c in candidates:
            with self.subTest(op=op, value=c.value):
                actual = self._callFUT(op, c.value)
                self.assertEqual(actual, c.expected)

    def test_or(self):
        from ..operators import Or

        C = namedtuple("C", "value, expected")

        candidates = [
            C(value="x", expected=True),
            C(value="xx", expected=True),
            C(value="xxx", expected=True),
        ]

        op = Or(["x", "xx", "xxx"])
        for c in candidates:
            with self.subTest(op=op, value=c.value):
                actual = self._callFUT(op, c.value)
                self.assertEqual(actual, c.expected)

    def test_and2(self):
        from ..operators import And, Not

        C = namedtuple("C", "value, expected")

        candidates = [
            C(value="x", expected=False),
            C(value="xx", expected=True),
            C(value="xxx", expected=False),
        ]

        op = And([Not("x"), "xx", Not("xxx")])
        for c in candidates:
            with self.subTest(op=op, value=c.value):
                actual = self._callFUT(op, c.value)
                self.assertEqual(actual, c.expected)
```
## File: dictknife/tests/test_shape.py
```python
import unittest
from collections import namedtuple


class Tests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from dictknife.shape import shape

        return shape(*args, **kwargs)

    def test_it(self):
        C = namedtuple("C", "input, output, squash, skiplist")
        candidates = [
            C(input={}, output=[], squash=False, skiplist=False),
            C(input={"name": "foo"}, output=["name"], squash=False, skiplist=False),
            C(
                input={"name": "foo", "skills": []},
                output=["name", "skills"],
                squash=False,
                skiplist=False,
            ),
            C(
                input={"name": "foo", "skills": ["x"]},
                output=["name", "skills", "skills/[]"],
                squash=False,
                skiplist=False,
            ),
            C(
                input={"name": "foo", "age": 10},
                output=["age", "name"],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[
                    {"name": "foo", "age": 10},
                    {"nickname": "BIGb", "name": "bar", "age": 10},
                ],
                output=["[]", "[]/age", "[]/name", "?[]/nickname"],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[
                    [
                        {"name": "foo", "age": 10},
                        {"nickname": "BIGb", "name": "bar", "age": 10},
                    ]
                ],
                output=["[]", "[]/[]", "[]/[]/age", "[]/[]/name", "?[]/[]/nickname"],
                squash=False,
                skiplist=False,
            ),
            C(
                input={"person": {"name": "foo", "age": 10}},
                output=["person", "person/age", "person/name"],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[{"person": {"name": "foo", "age": 10}}],
                output=["[]", "[]/person", "[]/person/age", "[]/person/name"],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10}},
                    {"person": {"nickname": "BIGb", "name": "bar", "age": 10}},
                ],
                output=[
                    "[]",
                    "[]/person",
                    "[]/person/age",
                    "[]/person/name",
                    "?[]/person/nickname",
                ],
                squash=False,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10}},
                    {"person": {"nickname": "BIGb", "name": "bar", "age": 10}},
                ],
                output=["person", "person/age", "person/name", "?person/nickname"],
                squash=True,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10, "skills": []}},
                    {"person": {"name": "bar", "age": 10, "skills": ["x"]}},
                ],
                output=[
                    "person",
                    "person/age",
                    "person/name",
                    "person/skills",
                    "?person/skills/[]",
                ],
                squash=True,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10}},
                    {"person": {"name": "bar", "age": 10, "skills": ["x"]}},
                ],
                output=[
                    "person",
                    "person/age",
                    "person/name",
                    "?person/skills",
                    "person/skills/[]",  # xxx
                ],
                squash=True,
                skiplist=False,
            ),
            C(
                input=[
                    {"person": {"name": "foo", "age": 10}},
                    {"person": {"name": "bar", "age": 10, "skills": ["x"]}},
                ],
                output=["person", "person/age", "person/name", "?person/skills"],
                squash=True,
                skiplist=True,
            ),
        ]
        for c in candidates:
            with self.subTest(input=c.input, squash=c.squash, skiplist=c.skiplist):
                got = self._callFUT(c.input, squash=c.squash, skiplist=c.skiplist)
                got = [row.path for row in got]
                self.assertEqual(c.output, got)
```
