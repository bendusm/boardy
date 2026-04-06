# Run Backend Tests

Запусти тесты backend.

## Commands

```bash
cd backend && pytest -v $ARGS
```

## Options

- `-v` — verbose output
- `-x` — stop on first failure
- `--tb=short` — shorter traceback
- `-k "test_name"` — run specific test
- `--cov=app` — with coverage

## Examples

```bash
# All tests
cd backend && pytest -v

# Specific module
cd backend && pytest -v tests/test_boards.py

# With coverage
cd backend && pytest -v --cov=app --cov-report=term-missing
```

Если тесты падают, покажи ошибки и предложи исправления.
