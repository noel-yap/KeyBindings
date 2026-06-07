"""Tests for the dump_symbolic_hotkeys helper in test-utils.shlib.

It sources a hotkey shlib and prints each entry as `<action>\\0<value>\\036`.
The tests build fixture shlibs, run the helper, and assert the emitted
records — including that the loop emits nothing for an empty array and that
multiline values survive intact.
"""

import shlex
import subprocess
import textwrap
from pathlib import Path

import pytest

from bashio import parse_entries

TESTS_DIR = Path(__file__).resolve().parent
TEST_UTILS = TESTS_DIR / "test-utils.shlib"
BASH = "/opt/homebrew/bin/bash"  # associative arrays require bash >= 4

pytestmark = pytest.mark.skipif(
    not Path(BASH).exists(),
    reason="requires Homebrew bash (associative array support)",
)


def _dump(shlib):
    script = textwrap.dedent(
        f"""\
        set -u
        source {shlex.quote(str(TEST_UTILS))}
        dump_symbolic_hotkeys {shlex.quote(str(shlib))}
        """
    )
    result = subprocess.run([BASH, "-c", script], capture_output=True)
    assert result.returncode == 0, result.stderr.decode("utf-8")
    return result.stdout


def test_empty_array_emits_nothing(write_hotkeys_shlib):
    shlib = write_hotkeys_shlib({})

    assert _dump(shlib) == b""


def test_single_entry_emits_one_nul_rs_record(write_hotkeys_shlib):
    shlib = write_hotkeys_shlib({"53": "value-53"})

    assert _dump(shlib) == b"53\x00value-53\x1e"


def test_multiline_value_is_preserved(write_hotkeys_shlib):
    value = "first\nsecond\nthird"
    shlib = write_hotkeys_shlib({"118": value})

    assert parse_entries(_dump(shlib)) == {"118": value}


def test_each_entry_is_emitted_once(write_hotkeys_shlib):
    entries = {"53": "a", "54": "b", "118": "c"}
    shlib = write_hotkeys_shlib(entries)

    raw = _dump(shlib)

    assert raw.count(b"\x1e") == len(entries)
    assert parse_entries(raw) == entries