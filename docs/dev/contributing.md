# Contributing to Wiverno

## Ways to Contribute

- Report bugs
- Suggest features
- Improve documentation
- Write tests
- Fix bugs
- Add features

## Getting Started

1. Fork the repository: https://github.com/Sayrrexe/Wiverno

2. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/Wiverno.git
cd Wiverno
```

3. Set up environment:

```bash
uv pip install -e ".[dev]"
pre-commit install
```

4. Create a branch:

```bash
git checkout -b feature/name    # For features
git checkout -b fix/name        # For bug fixes
git checkout -b docs/name       # For docs
```

## Development Process

1. **Write code** with tests
2. **Run checks:**

```bash
make check  # Format + lint + typecheck + test
```

3. **Commit** with descriptive message:

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve issue"
git commit -m "docs: clarify readme"
```

4. **Push** to your fork:

```bash
git push origin your-branch
```

5. **Create Pull Request** on GitHub with description

## PR Requirements

- All tests passing
- Coverage > 50%
- Code formatted (ruff format)
- No linting errors (ruff check)
- Types checked (mypy)
- Tests added for new code

## Code Standards

- Descriptive test names: `test_router_matches_exact_path()`
- Google style docstrings
- Type hints required
- Comments for complex logic

## Questions?

Ask in:
- GitHub Issues for bugs/features
- GitHub Discussions for questions

## Code of Conduct

Be respectful and constructive in all interactions.
