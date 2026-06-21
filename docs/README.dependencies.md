Dependencies layout
-------------------

- `requirements.txt` — production runtime requirements (kept minimal). Replaced with `requirements-prod.txt` contents.
- `requirements-prod.txt` — explicit runtime requirements used for smoke tests.
- `requirements-dev.txt` — development tools (formatters, linters).
- `requirements-ci.txt` — pinned environment freeze for CI reproducibility.

Workflow recommendations:
- Use `requirements-prod.txt` for local runtime installs.
- Use `requirements-ci.txt` in CI to pin exact versions.
- Keep dev tools in `requirements-dev.txt` and install only in dev environments.
