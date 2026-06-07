"""Shared fixtures for the hotkey tests."""

import pytest


@pytest.fixture
def write_hotkeys_shlib(tmp_path):
    """Return a factory that writes a fixture shlib defining `symbolic_hotkeys`.

    Values are embedded literally, so callers must use content free of `"`,
    `$`, backtick, and backslash (newlines are fine). Files are written under
    the test's `tmp_path`, so callers that also need that directory (e.g. as a
    lookup root) can request `tmp_path` themselves.
    """

    def _write(entries, name="fixture-hotkeys.shlib"):
        body = "\n".join(f'  [{action}]="{value}"' for action, value in entries.items())
        path = tmp_path / name
        path.write_text(f"declare -rA symbolic_hotkeys=(\n{body}\n)\n", encoding="utf-8")
        return path

    return _write