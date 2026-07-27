## Committing

### Linters and Formatters

Before committing a change run `prek run` to run all pre-commit hooks. Fix any issues that arise, then stage the changes and commit. Prefer using fixes built into the tools over manual fixes, for exmaple:

```
uv run ruff check --fix
```

### Commit Trailers

Every AI-assisted commit MUST include an `Assisted-By` trailer:

```
Assisted-By: <harness> (<model>; <provider>)
```

Examples:

Assisted-By: omp (claude-sonnet-4-5; anthropic)
Assisted-By: omp (gpt-4o; openai)

The trailer MUST appear in the commit message body, after a blank line separating it from the
summary. If multiple models contributed, include one trailer per model.

## Style Guidance

### Naming Conventions

This is application code, not a library. Avoid underscore-prefixed names (`_foo`, `_bar`) to
signal "private" — that convention exists to protect library consumers from implementation
details that might change. In an application there are no external consumers; every function
is already internal. Use plain descriptive names instead.

- Prefer `terminate_proc(proc)` over `_terminate_proc(proc)`
- Prefer `resolve_project(gate_name)` over `_resolve_project(gate_name)`
- Prefer `load_state_or_exit(workspace)` over `_load_state_or_exit(workspace)` (already correct)

## Python Environment

Use `uv` for managinge the Python environment. This includes installing dependencies, running tests, and executing scripts.
If `uv` is not installed, STOP. You MUST inform the user and wait for feedback before proceeding.

## Testing

Run unit tests with `uv run pytest`.

Full e2e test can be run with `spread` (WARNING: this will not work if you are inside a container).
