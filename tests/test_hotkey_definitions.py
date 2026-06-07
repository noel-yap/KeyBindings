"""Lint the symbolic-hotkey XML definitions.

Each `*-hotkeys.shlib` defines only a `symbolic_hotkeys` associative array
(no side effects), so it can be sourced purely to read the definitions. For
every entry we wrap its `<dict>...</dict>` value in a minimal plist envelope
and confirm it parses as a valid property list — catching malformed XML or
plist-invalid content. This is well-formedness only; it does not assert the
semantic meaning of any particular hotkey.
"""

import plistlib
import shlex
import subprocess
import textwrap
from pathlib import Path

import pytest

from bashio import parse_entries

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
TEST_UTILS = TESTS_DIR / "test-utils.shlib"
BASH = "/opt/homebrew/bin/bash"  # associative arrays require bash >= 4

HOTKEY_SHLIBS = [
    "brightness-hotkeys.shlib",
    "screenshot-hotkeys.shlib",
    "desktop-hotkeys.shlib",
]

pytestmark = pytest.mark.skipif(
    not Path(BASH).exists(),
    reason="requires Homebrew bash (associative array support)",
)


def _load_entries(shlib: Path):
    """Source a hotkey shlib and return its {action: xml_value} entries."""
    script = textwrap.dedent(
        f"""\
        set -u
        source {shlex.quote(str(TEST_UTILS))}
        dump_symbolic_hotkeys {shlex.quote(str(shlib))}
        """
    )
    result = subprocess.run([BASH, "-c", script], capture_output=True)
    assert result.returncode == 0, result.stderr.decode("utf-8")

    return parse_entries(result.stdout)


def _all_entries(names=HOTKEY_SHLIBS, root=REPO_ROOT):
    """Collect one parametrize case per hotkey entry across the given shlibs."""
    cases = []
    for name in names:
        for action, value in _load_entries(root / name).items():
            cases.append(pytest.param(value, id=f"{name}:{action}"))
    return cases


@pytest.mark.parametrize("value", _all_entries())
def test_hotkey_value_is_well_formed_plist(value):
    wrapped = f'<?xml version="1.0"?><plist version="1.0">{value}</plist>'

    parsed = plistlib.loads(wrapped.encode("utf-8"))

    assert isinstance(parsed, dict)


def test_load_entries_returns_empty_dict_for_empty_array(write_hotkeys_shlib):
    shlib = write_hotkeys_shlib({})

    assert _load_entries(shlib) == {}


def test_load_entries_returns_single_entry(write_hotkeys_shlib):
    shlib = write_hotkeys_shlib({"53": "value-53"})

    assert _load_entries(shlib) == {"53": "value-53"}


def test_load_entries_preserves_multiline_value(write_hotkeys_shlib):
    value = "line-1\nline-2"
    shlib = write_hotkeys_shlib({"118": value})

    assert _load_entries(shlib) == {"118": value}


def test_load_entries_returns_every_entry(write_hotkeys_shlib):
    entries = {"53": "a", "54": "b", "118": "c"}
    shlib = write_hotkeys_shlib(entries)

    assert _load_entries(shlib) == entries


def _ids_and_values(cases):
    return sorted((case.id, case.values[0]) for case in cases)


def test_all_entries_is_empty_when_no_shlibs_given(tmp_path):
    assert _all_entries(names=[], root=tmp_path) == []


def test_all_entries_collects_entries_from_one_shlib(tmp_path, write_hotkeys_shlib):
    write_hotkeys_shlib({"53": "a", "54": "b"}, name="brightness-hotkeys.shlib")

    cases = _all_entries(names=["brightness-hotkeys.shlib"], root=tmp_path)

    assert _ids_and_values(cases) == [
        ("brightness-hotkeys.shlib:53", "a"),
        ("brightness-hotkeys.shlib:54", "b"),
    ]


def test_all_entries_collects_across_multiple_shlibs(tmp_path, write_hotkeys_shlib):
    write_hotkeys_shlib({"53": "a"}, name="brightness-hotkeys.shlib")
    write_hotkeys_shlib({"30": "s"}, name="screenshot-hotkeys.shlib")

    cases = _all_entries(
        names=["brightness-hotkeys.shlib", "screenshot-hotkeys.shlib"], root=tmp_path
    )

    assert _ids_and_values(cases) == [
        ("brightness-hotkeys.shlib:53", "a"),
        ("screenshot-hotkeys.shlib:30", "s"),
    ]