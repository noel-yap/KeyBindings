# KeyBindings

## Symbolic hotkeys

Each `set-*-hotkeys.sh` script applies one group of macOS symbolic hotkeys via
`defaults`, then reloads them with `activateSettings`:

* `set-brightness-hotkeys.sh` — disable F14/F15 (and ⌥F14/⌥F15) brightness
* `set-screenshot-hotkeys.sh` — ⌥⎙ screenshot region
* `set-desktop-hotkeys.sh` — ⌥⌘← / ⌥⌘→ and ⌥⌘1–9 desktop navigation

`set-hotkeys.sh` runs all three. Each script sources its definitions from the
matching `*-hotkeys.shlib` and the shared applier in
`apply-symbolic-hotkeys.shlib`. Running them requires Homebrew bash
(`/opt/homebrew/bin/bash`).

## Tests

```sh
make test
```

This initializes the `bash-mock` submodule (under `vendor/`) if needed and runs
the `pytest` suite in `tests/`.

## Some helpful links

* https://www.unicode.org/Public/MAPPINGS/VENDORS/APPLE/CORPCHAR.TXT
* http://xahlee.info/kbd/osx_keybinding.html
* http://xahlee.info/kbd/osx_keybinding_key_syntax.html
* http://xahlee.info/kbd/apple_pc_kb_diff.html
* http://xahlee.info/kbd/osx_keybinding_action_code.html

* https://gist.github.com/zsimic/1367779#file-defaultkeybinding-dict
* https://math.dartmouth.edu/~sarunas/Linux_Compose_Key_Sequences.html
* http://bob.cakebox.net/osxcompose/DefaultKeyBinding.dict

* https://gist.github.com/stephancasas/74c4621e2492fb875f0f42778d432973
* https://eastmanreference.com/complete-list-of-applescript-key-codes
* https://github.com/NUIKit/CGSInternal/blob/master/CGSHotKeys.h
