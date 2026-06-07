"""Parsers for the NUL/RS-delimited output emitted by the bash test mocks.

Records are terminated by RS (``0x1e``) and empty records are ignored. Two
field conventions appear in that output:

* ``parse_entries`` — each record is a single ``action\\0value`` pair (one NUL
  separating the two); returned as a dict.
* ``parse_calls`` — each record is a run of NUL-*terminated* fields (so a
  trailing empty field is dropped); returned as a list of ``(command, args)``.

Both accept either ``bytes`` or ``str``.
"""


def _records(raw):
    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
    return [record for record in text.split("\x1e") if record]


def parse_entries(raw):
    """Parse ``action\\0value`` records into a ``{action: value}`` dict."""
    entries = {}
    for record in _records(raw):
        action, _, value = record.partition("\x00")
        entries[action] = value
    return entries


def parse_calls(raw):
    """Parse NUL-terminated-field records into ``[(command, [args]), ...]``."""
    calls = []
    for record in _records(raw):
        fields = record.split("\x00")
        if fields and fields[-1] == "":
            fields = fields[:-1]
        if fields:
            calls.append((fields[0], fields[1:]))
    return calls