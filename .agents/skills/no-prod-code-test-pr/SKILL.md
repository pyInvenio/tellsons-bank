---
name: no-prod-code-test-pr
description: Use when preparing or reviewing a Tellson's Bank test-coverage PR that must avoid production-code changes.
---

# No Production Code Test PR

Before opening or reviewing a PR:

1. Check changed files.
2. Reject production-code edits unless the human explicitly expanded scope.
3. Confirm tests use synthetic fixtures only.
4. Confirm no real downstreams or network calls are used.
5. Confirm the PR description includes commands, coverage delta, edge cases, and reviewer checklist.

Production paths include:

- `services/*/src/main/**`
- `services/*/*_logger/*.py` outside `tests`
- `services/*/src/*.ts` outside `tests`
- `libs/shared-models/**`

Allowed paths for compliance test-generation tasks include:

- `services/*/src/test/**`
- `services/*/tests/**`
- `services/*/coverage` configuration files
- `.github/workflows/**`
- `.github/scripts/**`
- `docs/**`
- `devin-workspace/**`
