# Contributing to Django Dead Code

Thank you for your interest in contributing to Django Dead Code! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/django-deadcode.git
   cd django-deadcode
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### 1. Create a Branch

Create a descriptive branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clear, concise code following PEP 8 guidelines
- Add tests for new features or bug fixes
- Update documentation as needed
- Keep commits focused and atomic

### 3. Run Tests

Before submitting, ensure all tests pass:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=django_deadcode --cov-report=html

# Run specific test file
pytest tests/test_template_analyzer.py
```

### 4. Code Quality Checks

Run linting and type checking:

```bash
# Linting with ruff
ruff check .

# Auto-fix issues
ruff check --fix .

# Type checking with mypy
mypy django_deadcode
```

### 5. Commit Your Changes

Write clear commit messages following conventional commits:

```bash
git add .
git commit -m "feat: add support for detecting reverse() calls"
# or
git commit -m "fix: handle empty template directories"
# or
git commit -m "docs: update installation instructions"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to any related issues
- Screenshots/examples if applicable

## Code Style

### Python Style

- Follow PEP 8
- Use type hints for function signatures
- Maximum line length: 88 characters (Black default)
- Use descriptive variable names

### Example:

```python
def analyze_template_file(self, template_path: Path) -> Dict[str, Set[str]]:
    """
    Analyze a single template file.

    Args:
        template_path: Path to the template file

    Returns:
        Dictionary containing analysis results
    """
    try:
        content = template_path.read_text(encoding="utf-8")
        return self._analyze_template_content(content, str(template_path))
    except (IOError, UnicodeDecodeError) as e:
        return {"error": str(e)}
```

### Documentation

- Use Google-style docstrings
- Document all public methods and classes
- Include examples for complex functionality
- Keep README.md up to date

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what is being tested

### Test Structure

```python
class TestFeatureName:
    """Test suite for FeatureName."""

    def test_basic_functionality(self):
        """Test that basic functionality works as expected."""
        # Arrange
        analyzer = Analyzer()

        # Act
        result = analyzer.analyze(data)

        # Assert
        assert result == expected
```

### Coverage

- Aim for at least 80% code coverage
- Focus on critical paths and edge cases
- Don't write tests just for coverage numbers

## Project Structure

```
django-deadcode/
├── django_deadcode/          # Main package
│   ├── analyzers/           # Analysis modules
│   ├── management/          # Django management commands
│   │   └── commands/
│   └── reporters/           # Report generators
├── tests/                   # Test suite
├── agent-os/               # Product documentation
│   └── product/
├── pyproject.toml          # Package configuration
└── README.md               # Main documentation
```

## Adding New Features

When adding new features:

1. **Check the roadmap** in `agent-os/product/roadmap.md`
2. **Open an issue** to discuss the feature first
3. **Write tests** before implementation (TDD approach)
4. **Update documentation** including README and docstrings
5. **Add examples** of the new feature in use

## Reporting Bugs

When reporting bugs, include:

- Django version
- Python version
- django-deadcode version
- Minimal reproducible example
- Expected vs actual behavior
- Stack trace if applicable

## Feature Requests

For feature requests:

- Check existing issues first
- Describe the use case clearly
- Explain why this feature would be valuable
- Suggest a possible implementation if you have ideas

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose:

1. Maintainers will review your code
2. Address any feedback or requested changes
3. Once approved, a maintainer will merge your PR

## Questions?

- Open an issue for questions
- Check existing issues and discussions first
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Django Dead Code! 🚀
