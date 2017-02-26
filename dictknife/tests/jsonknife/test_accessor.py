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
            "k\"l": 6,
            " ": 7,
            "m~n": 8
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
            ("/k\"l", 6),
            ("/ ", 7),
            ("/m~0n", 8),
        ]

        for query, expected in candidates:
            with self.subTest(query=query, expected=expected):
                actual = self._callFUT(doc, query)
                self.assertEqual(actual, expected)
