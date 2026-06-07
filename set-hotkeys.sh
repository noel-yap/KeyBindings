#!/opt/homebrew/bin/bash
set -e
set -o pipefail
set -u
shopt -s inherit_errexit

# Apply every symbolic-hotkey group. Each setter runs in its own process
# because they all define a readonly `symbolic_hotkeys` array.
dir="$(dirname "${BASH_SOURCE[0]}")"
"${dir}/set-brightness-hotkeys.sh"
"${dir}/set-screenshot-hotkeys.sh"
"${dir}/set-desktop-hotkeys.sh"