# Makefile for Wiverno

.PHONY: help install dev test coverage lint format typecheck clean docs serve build all pre-commit benchmark

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Wiverno Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Installation
install: ## Install the package
	@echo "$(BLUE)Installing Wiverno...$(NC)"
	uv pip install .

dev: ## Install in development mode with all dependencies
	@echo "$(BLUE)Installing Wiverno in development mode...$(NC)"
	uv pip install -e ".[dev]"
	@echo "$(GREEN)Done! Installing pre-commit hooks...$(NC)"
	pre-commit install

# Testing
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	uv run pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	uv run pytest tests/integration/ -v

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	uv run pytest-watch

coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run pytest --cov=wiverno --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(NC)"

coverage-xml: ## Generate XML coverage report for CI
	@echo "$(BLUE)Generating XML coverage report...$(NC)"
	uv run pytest --cov=wiverno --cov-report=xml

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	uv run pytest tests/benchmark/ --benchmark-only -v

# Code Quality
lint: ## Run linter (ruff check)
	@echo "$(BLUE)Linting code...$(NC)"
	uv run ruff check .

lint-fix: ## Run linter and fix issues automatically
	@echo "$(BLUE)Linting and fixing code...$(NC)"
	uv run ruff check --fix .

format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run ruff format .

format-check: ## Check if code is formatted correctly
	@echo "$(BLUE)Checking code formatting...$(NC)"
	uv run ruff format --check .

typecheck: ## Run type checker (mypy)
	@echo "$(BLUE)Type checking...$(NC)"
	uv run mypy wiverno

# Combined Quality Checks
quality: lint typecheck ## Run all quality checks (lint + typecheck)
	@echo "$(GREEN)All quality checks passed!$(NC)"

check: format-check lint typecheck test ## Run all checks (format + lint + typecheck + test)
	@echo "$(GREEN)All checks passed!$(NC)"

# Pre-commit
pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "$(BLUE)Updating pre-commit hooks...$(NC)"
	pre-commit autoupdate

# Documentation
docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	uv run mkdocs build

docs-serve: ## Serve documentation locally with live reload
	@echo "$(BLUE)Serving documentation at http://127.0.0.1:8000$(NC)"
	uv run mkdocs serve

docs-deploy: ## Deploy documentation to GitHub Pages
	@echo "$(BLUE)Deploying documentation...$(NC)"
	uv run mkdocs gh-deploy

# Development Server
serve: ## Run development server with auto-reload
	@echo "$(BLUE)Starting development server...$(NC)"
	uv run python -c "from wiverno.dev.dev_server import DevServer; from wiverno.main import Wiverno; DevServer(Wiverno(routes_list=[])).start()"

# Build and Distribution
build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	uv build

publish: build ## Publish package to PyPI
	@echo "$(BLUE)Publishing to PyPI...$(NC)"
	uv publish

publish-test: build ## Publish package to Test PyPI
	@echo "$(BLUE)Publishing to Test PyPI...$(NC)"
	uv publish --repository testpypi

# Cleaning
clean: ## Remove build artifacts and cache files
	@echo "$(BLUE)Cleaning up...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.orig" -delete
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-docs: ## Remove documentation build artifacts
	@echo "$(BLUE)Cleaning documentation...$(NC)"
	rm -rf site/

# Docker (if needed in future)
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t wiverno:latest .

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -p 8000:8000 wiverno:latest

# Dependencies
deps-update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	uv pip compile pyproject.toml -o requirements.txt

deps-sync: ## Sync dependencies
	@echo "$(BLUE)Syncing dependencies...$(NC)"
	uv pip sync requirements.txt

# Git
git-clean: ## Clean git repository (remove untracked files)
	@echo "$(YELLOW)Warning: This will remove all untracked files!$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to cancel, or Enter to continue...$(NC)"
	@read
	git clean -fdx

# All-in-one
all: clean format lint typecheck test docs ## Run all tasks (clean, format, lint, typecheck, test, docs)
	@echo "$(GREEN)All tasks completed successfully!$(NC)"

# Quick checks before commit
quick: format lint test-unit ## Quick checks (format, lint, unit tests)
	@echo "$(GREEN)Quick checks passed!$(NC)"

# CI simulation
ci: format-check lint typecheck coverage ## Simulate CI pipeline
	@echo "$(GREEN)CI pipeline completed successfully!$(NC)"
