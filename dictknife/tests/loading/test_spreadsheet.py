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
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range=None)
            ),
            C(
                input="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps#/A1:B2",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range="A1:B2")
            ),
            C(
                input="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps#/sheet!A1:B2",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range="sheet!A1:B2")
            ),
            C(
                input="https://docs.google.com/spreadsheets/d/1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps/edit#gid=0",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range=None)
            ),
            C(
                input="https://docs.google.com/spreadsheets/d/1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps/edit?ranges=A1:B2#gid=0",
                output=Guessed(spreadsheet_id="1qpyC0XzvTcKT6EISywvqESX3A0MwQoFDE8p-Bll4hps", range="A1:B2")
            ),
        ]
        # yapf: enable
        for c in candidates:
            with self.subTest(input=c.input):
                got = self._callFUT(c.input)
                self.assertEqual(got, c.output)
