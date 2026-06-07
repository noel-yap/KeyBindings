.DEFAULT_GOAL := test
.PHONY: test submodule

PYTEST ?= pytest

# Check out the bash-mock submodule (its bash-inject.shlib is sourced by
# apply-symbolic-hotkeys.shlib). The file target means this only runs when
# the submodule hasn't been initialized yet.
vendor/bash-mock/bash-inject.shlib:
	git submodule update --init --recursive

submodule: vendor/bash-mock/bash-inject.shlib

test: vendor/bash-mock/bash-inject.shlib
	$(PYTEST) tests/