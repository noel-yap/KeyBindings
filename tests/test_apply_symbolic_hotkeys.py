"""Tests for the apply_symbolic_hotkeys bash function.

Each test defines its own bash mock functions for `defaults` and
`activateSettings` (the latter reachable because the shlib `@inject`s its
absolute path and then calls it by basename). The mocks record every
invocation to a log file using NUL-separated fields and an RS record
terminator, so arbitrary multiline argument values survive intact. The
assertions then run in Python against the parsed calls.
"""

import shlex
import subprocess
import textwrap
import types
from pathlib import Path

import pytest

from bashio import parse_calls

REPO_ROOT = Path(__file__).resolve().parent.parent
SHLIB = REPO_ROOT / "apply-symbolic-hotkeys.shlib"
BASH = "/opt/homebrew/bin/bash"  # nameref (local -n) requires bash >= 4.3

pytestmark = pytest.mark.skipif(
    not Path(BASH).exists(),
    reason="requires Homebrew bash (local -n nameref support)",
)

# Every `defaults` call should start with these four arguments.
DEFAULTS_PREFIX = [
    "write",
    "com.apple.symbolichotkeys.plist",
    "AppleSymbolicHotKeys",
    "-dict-add",
]


def _ansi_c_quote(value: str) -> str:
    """Render an arbitrary string as a bash $'...' literal."""
    body = (
        value.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
        .replace("\r", "\\r")
    )
    return "$'" + body + "'"


def run_apply(entries, tmp_path):
    """Run apply_symbolic_hotkeys against `entries`; return recorded calls."""
    log = tmp_path / "calls.log"
    entries_block = "\n".join(
        f"  [{key}]={_ansi_c_quote(value)}" for key, value in entries.items()
    )
    script = textwrap.dedent(
        f"""\
        set -u

        _record() {{
          local c="$1"; shift
          {{
            printf '%s\\0' "$c"
            local a
            for a in "$@"; do printf '%s\\0' "$a"; done
            printf '\\036'
          }} >> {shlex.quote(str(log))}
        }}

        # Mocks defined before sourcing so @inject leaves them in place.
        defaults() {{ _record defaults "$@"; }}
        activateSettings() {{ _record activateSettings "$@"; }}

        source {shlex.quote(str(SHLIB))}

        declare -A symbolic_hotkeys=(
        __ENTRIES__
        )

        apply_symbolic_hotkeys symbolic_hotkeys
        """
    ).replace("__ENTRIES__", entries_block)
    result = subprocess.run([BASH, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, (
        f"driver failed (rc={result.returncode})\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    return parse_calls(log.read_bytes()) if log.exists() else []


def test_empty_array_writes_nothing_and_activates_once(tmp_path):
    calls = run_apply({}, tmp_path)

    assert [c for c in calls if c[0] == "defaults"] == []
    assert [c for c in calls if c[0] == "activateSettings"] == [
        ("activateSettings", ["-u"])
    ]


def test_single_entry_is_written_with_multiline_value_intact(tmp_path):
    value = "<dict>\n  <key>enabled</key><false/>\n</dict>"

    calls = run_apply({"53": value}, tmp_path)

    defaults_calls = [c for c in calls if c[0] == "defaults"]
    assert defaults_calls == [("defaults", DEFAULTS_PREFIX + ["53", value])]


def test_single_entry_activates_settings_exactly_once(tmp_path):
    calls = run_apply({"53": "value"}, tmp_path)

    assert sum(1 for c in calls if c[0] == "activateSettings") == 1


def test_each_entry_is_written_exactly_once(tmp_path):
    entries = {"53": "value-53", "118": "multi\nline\nvalue"}

    calls = run_apply(entries, tmp_path)

    defaults_calls = [c for c in calls if c[0] == "defaults"]
    assert len(defaults_calls) == len(entries)

    written = {}
    for _, args in defaults_calls:
        assert args[:4] == DEFAULTS_PREFIX
        action, value = args[4], args[5]
        written[action] = value
    assert written == entries


def test_settings_are_activated_once_after_all_writes(tmp_path):
    entries = {"53": "a", "54": "b"}

    calls = run_apply(entries, tmp_path)

    assert calls[-1] == ("activateSettings", ["-u"])
    assert all(c[0] == "defaults" for c in calls[:-1])
    assert sum(1 for c in calls if c[0] == "activateSettings") == 1


def test_run_apply_returns_parsed_calls_from_the_log(tmp_path, monkeypatch):
    log = tmp_path / "calls.log"

    def fake_run(cmd, *args, **kwargs):
        log.write_bytes(b"defaults\x00write\x0053\x00\x1e")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert run_apply({"53": "x"}, tmp_path) == [("defaults", ["write", "53"])]


def test_run_apply_returns_empty_list_when_no_log_is_written(tmp_path, monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert run_apply({"53": "x"}, tmp_path) == []


def test_run_apply_raises_when_the_driver_fails(tmp_path, monkeypatch):
    def fake_run(cmd, *args, **kwargs):
        return types.SimpleNamespace(returncode=1, stdout="out", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(AssertionError):
        run_apply({"53": "x"}, tmp_path)