# Contributing to Order Processing Demo

Thank you for your interest in contributing to this AWS EventBridge demo! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.13
- Node.js and npm (for AWS CDK CLI)
- AWS CLI configured with credentials
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/learn-aws-eventbridge.git
   cd learn-aws-eventbridge
   ```

2. **Install dependencies:**
   ```bash
   make install-dev
   ```

   This will:
   - Install Python dependencies (production and development)
   - Set up pre-commit hooks

3. **Verify your setup:**
   ```bash
   make all-checks
   ```

## Development Workflow

### Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below

3. **Run tests and checks:**
   ```bash
   make all-checks
   ```

   This runs:
   - Linting (ruff)
   - Formatting checks (black)
   - Type checking (mypy)
   - Tests (pytest)
   - Security scans (bandit, safety)

4. **Format your code:**
   ```bash
   make format
   ```

### Code Style Guidelines

#### Python Code Style

- **Formatting**: We use `black` with a line length of 100 characters
- **Linting**: We use `ruff` for linting
- **Type Hints**: All functions must have type hints
- **Docstrings**: Use Google-style docstrings for all public functions and classes

Example:
```python
def process_order(order_id: str, items: List[str]) -> Dict[str, Any]:
    """
    Process an order and return the result.

    Args:
        order_id: Unique identifier for the order
        items: List of item names in the order

    Returns:
        Dictionary containing order processing results
    """
    # Implementation here
    pass
```

#### Lambda Functions

- Use **structured JSON logging** for all log statements
- Include `request_id` in all log entries
- Use type hints for `event` and `context` parameters
- Handle errors gracefully with proper logging

#### CDK Code

- Add docstrings to all constructs
- Use type hints for all parameters
- Follow CDK best practices for naming resources
- Add tags to all resources for cost allocation

### Testing

#### Writing Tests

- Place unit tests in `tests/unit/`
- Use `pytest` for testing
- Mock AWS services with `moto`
- Aim for >80% code coverage

Example test:
```python
import pytest
from unittest.mock import MagicMock

def test_handler_success(lambda_context: MagicMock) -> None:
    """Test successful processing."""
    # Test implementation
    pass
```

#### Running Tests

```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run with coverage report
pytest tests/ -v --cov=. --cov-report=html
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit. They check for:

- Trailing whitespace
- YAML/JSON syntax
- Large files
- Private keys
- Code formatting
- Type hints
- Security issues

To run pre-commit manually:
```bash
pre-commit run --all-files
```

## CDK Development

### Testing CDK Changes

1. **Synthesize the stack:**
   ```bash
   make synth
   ```

2. **View differences:**
   ```bash
   make diff
   ```

3. **Deploy to your AWS account:**
   ```bash
   make deploy
   ```

4. **Clean up:**
   ```bash
   make destroy
   ```

### CDK Best Practices

- Use L2/L3 constructs when available
- Add meaningful descriptions to resources
- Use `Tags.of(self).add()` for cost allocation
- Create CloudWatch alarms for monitoring
- Follow the principle of least privilege for IAM permissions

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features
3. **Ensure all checks pass:**
   ```bash
   make all-checks
   ```
4. **Update ARCHITECTURE.md** if you're changing the architecture
5. **Create a pull request** - GitHub will automatically populate a PR template with checklist items

## Common Tasks

### Adding a New Lambda Function

1. Create directory: `lambdas/new_function/`
2. Create `index.py` with typed handler
3. Add structured logging
4. Create `requirements.txt` (even if empty)
5. Add function to CDK stack
6. Add unit tests
7. Update ARCHITECTURE.md

### Adding a New EventBridge Rule

1. Define event pattern in CDK stack
2. Create target Lambda function
3. Add tests for the rule
4. Update ARCHITECTURE.md
5. Document event schema

### Modifying Event Schema

1. Update Lambda handlers to support new schema
2. Update tests with new schema
3. Document schema in ARCHITECTURE.md
4. Consider backward compatibility

## Reporting Issues

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Python version, AWS region, etc.)

### Feature Requests

Include:
- Description of the feature
- Use case / motivation
- Proposed implementation (optional)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Questions?

If you have questions:
1. Check existing issues and discussions
2. Review the README and ARCHITECTURE docs
3. Open a new issue with the "question" label
4. Reach out to your local AWS User Group

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Makefile Commands Reference

```bash
make help           # Show all available commands
make install        # Install production dependencies
make install-dev    # Install development dependencies
make test           # Run all tests
make test-unit      # Run unit tests only
make lint           # Run linting checks
make format         # Format code
make type-check     # Run type checking
make security       # Run security scans
make clean          # Clean up generated files
make bootstrap      # Bootstrap CDK
make synth          # Synthesize CloudFormation template
make diff           # Show stack differences
make deploy         # Deploy stack
make destroy        # Destroy stack
make all-checks     # Run all checks (CI)
```

Thank you for contributing! 🎉
