# The project's entry points for people and CI. Every check's command lives in CONSTRAINTS.md;
# tools/check.py reads that table, so nothing here repeats a command.

.PHONY: check setup plants hooks

check:  ## every check CONSTRAINTS.md runs in CI, in parallel, one line each
	uv run python tools/check.py

setup:  ## switch the git hooks on for this clone
	git config core.hooksPath tools/git_hooks
	chmod +x tools/git_hooks/pre-commit tools/git_hooks/commit-msg tools/git_hooks/pre-push tools/git_hooks/pre-merge-commit
	@echo "git hooks on: core.hooksPath = tools/git_hooks"

plants:  ## prove every check and hook refuses its planted violation; the variable stops pre-push re-running this
	UIAUDIT_PLANTS=1 uv run python tools/toolkit/prove_checks.py plants.toml
	UIAUDIT_PLANTS=1 uv run python tools/toolkit/prove_checks.py plants-hooks.toml
