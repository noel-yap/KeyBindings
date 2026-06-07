#!/opt/homebrew/bin/bash
set -e
set -o pipefail
set -u
shopt -s inherit_errexit

source "$(dirname "${BASH_SOURCE[0]}")/apply-symbolic-hotkeys.shlib"
source "$(dirname "${BASH_SOURCE[0]}")/screenshot-hotkeys.shlib"

apply_symbolic_hotkeys symbolic_hotkeys