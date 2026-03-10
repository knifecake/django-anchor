# Agent instructions

## Formatting

This project uses `ruff` for formatting via pre-commit. CI will fail if files
are not formatted. Before committing, run:

```bash
ruff format .
```

If `ruff` is not installed locally, you can run it through the pre-commit hook:

```bash
uv run pre-commit run ruff-format --all-files
```

## Tests

Run the test suite with:

```bash
uv run python -m django test tests/ --settings=tests.settings
```
