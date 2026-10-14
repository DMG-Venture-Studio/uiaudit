# The project's entry points for people and CI. Every check's command lives in CONSTRAINTS.md;
# tools/check.py reads that table, so nothing here repeats a command.

.PHONY: check setup plants hooks

check:  ## every check CONSTRAINTS.md runs in CI, in parallel, one line each
	uv run python tools/check.py

setup:  ## switch the git hooks on for this clone, and keep SSH alive through a long pre-push
	git config core.hooksPath tools/git_hooks
	git config core.sshCommand "ssh -o ServerAliveInterval=15 -o ServerAliveCountMax=40"
	chmod +x tools/git_hooks/pre-commit tools/git_hooks/commit-msg tools/git_hooks/pre-push tools/git_hooks/pre-merge-commit
	@echo "git hooks on: core.hooksPath = tools/git_hooks"

plants:  ## prove every check and hook refuses its planted violation; where it runs is the Plants row of CONSTRAINTS.md
	uv run python tools/toolkit/prove_checks.py plants.toml
	uv run python tools/toolkit/prove_checks.py plants-hooks.toml
