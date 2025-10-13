# Check Quality

Run all quality checks (ruff, black, mypy, tests) before committing code.

## Commands to Run

```bash
# Lint with ruff (auto-fix where possible)
ruff check --fix .

# Format with black
black .

# Type check with mypy
mypy .

# Run tests
pytest
```

## Common Issues and Fixes

### Ruff Linting Errors
- **Import sorting**: Use `ruff check --fix .` to auto-fix
- **Deprecated types**: Replace `Dict[str, Any]` with `dict[str, Any]` (Python 3.9+)
- **Line too long**: Manually split lines that exceed 88 characters

### Black Formatting
- Always run `black .` after making changes
- Black is the final formatting step after ruff

### Pytest Failures
- **NoRegionError**: Ensure boto3 clients use lazy initialization pattern
- Reset global client cache in tests: `module._client_name = None`
- Use `@mock_aws` decorator from moto library

## Best Practice
Run these checks locally BEFORE pushing to avoid CI failures. The GitHub Actions CI pipeline runs the same checks.
