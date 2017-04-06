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
            "author": {
                "givenName": "John",
                "familyName": "Doe"
            },
            "tags": ["example", "sample"],
            "content": "This will be unchanged"
        }

        q = {
            "title": "Hello!",
            "phoneNumber": "+01-123-456-7890",
            "author": {
                "familyName": None
            },
            "tags": ["example"]
        }

        expected = {
            "title": "Hello!",
            "author": {
                "givenName": "John"
            },
            "tags": ["example"],
            "content": "This will be unchanged",
            "phoneNumber": "+01-123-456-7890"
        }

        actual = self._callFUT(d, q)
        self.assertFalse(list(diff(expected, actual)))
