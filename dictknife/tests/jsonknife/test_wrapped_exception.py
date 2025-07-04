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

    def test_nested(self) -> None:
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
            def __init__(self, val, *, context) -> None:
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
