.PHONY: help install install-dev test lint format type-check security clean deploy destroy diff synth bootstrap setup-github

help:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Setup:'
	@echo '  install          Install production dependencies'
	@echo '  install-dev      Install development dependencies'
	@echo ''
	@echo 'Development:'
	@echo '  test             Run all tests'
	@echo '  test-unit        Run unit tests only'
	@echo '  lint             Run linting checks'
	@echo '  format           Format code'
	@echo '  type-check       Run type checking'
	@echo '  security         Run security scans'
	@echo '  clean            Clean up generated files'
	@echo ''
	@echo 'CDK:'
	@echo '  bootstrap        Bootstrap CDK in your AWS account'
	@echo '  synth            Synthesize CloudFormation template'
	@echo '  diff             Show differences'
	@echo '  deploy           Deploy the stack'
	@echo '  destroy          Destroy the stack'
	@echo '  watch            Watch for changes and deploy'
	@echo ''
	@echo 'GitHub Actions:'
	@echo '  setup-github     Deploy OIDC provider for GitHub Actions (requires GITHUB_ORG and GITHUB_REPO)'
	@echo ''
	@echo 'CI:'
	@echo '  all-checks       Run all checks (lint, type-check, test, security)'
	@echo '  ci               Same as all-checks'

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

test-unit:
	pytest tests/unit/ -v

lint:
	ruff check .
	black --check .

format:
	ruff check --fix .
	black .

type-check:
	mypy app.py order_processing_stack.py

security:
	bandit -r lambdas/ -ll
	safety check --bare

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "cdk.out" -exec rm -rf {} + 2>/dev/null || true

bootstrap:
	cdk bootstrap

synth:
	cdk synth

diff:
	cdk diff

deploy:
	cdk deploy

destroy:
	cdk destroy

watch:
	cdk watch

setup-github:
	@if [ -z "$(GITHUB_ORG)" ] || [ -z "$(GITHUB_REPO)" ]; then \
		echo "Error: GITHUB_ORG and GITHUB_REPO must be set"; \
		echo "Usage: make setup-github GITHUB_ORG=myusername GITHUB_REPO=learn-aws-eventbridge"; \
		exit 1; \
	fi
	cdk deploy -a "python setup_github_oidc.py $(GITHUB_ORG) $(GITHUB_REPO)" GitHubOIDCStack

all-checks: lint type-check test security

ci: all-checks
