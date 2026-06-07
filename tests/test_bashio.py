"""Tests for the bashio parsers."""

from bashio import parse_calls, parse_entries


class TestParseEntries:
    def test_returns_empty_dict_for_empty_input(self):
        assert parse_entries(b"") == {}

    def test_returns_single_entry(self):
        assert parse_entries(b"53\x00value-53\x1e") == {"53": "value-53"}

    def test_preserves_multiline_value(self):
        assert parse_entries(b"118\x00first\nsecond\x1e") == {"118": "first\nsecond"}

    def test_returns_every_entry(self):
        raw = b"53\x00a\x1e54\x00b\x1e118\x00c\x1e"

        assert parse_entries(raw) == {"53": "a", "54": "b", "118": "c"}

    def test_accepts_str_input(self):
        assert parse_entries("53\x00value\x1e") == {"53": "value"}


class TestParseCalls:
    def test_returns_empty_list_for_empty_input(self):
        assert parse_calls(b"") == []

    def test_parses_a_single_record(self):
        assert parse_calls(b"defaults\x00write\x0053\x00\x1e") == [
            ("defaults", ["write", "53"])
        ]

    def test_skips_empty_records_and_parses_argless_commands(self):
        assert parse_calls(b"a\x00\x1eb\x00\x1e") == [("a", []), ("b", [])]

    def test_keeps_last_field_when_no_trailing_separator(self):
        assert parse_calls(b"cmd\x00arg\x1e") == [("cmd", ["arg"])]

    def test_preserves_multiline_field(self):
        assert parse_calls(b"defaults\x00<dict>\n</dict>\x00\x1e") == [
            ("defaults", ["<dict>\n</dict>"])
        ]