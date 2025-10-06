# Contributing to Remnawave Bot

Thank you for your interest in contributing to Remnawave Bot! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the behavior
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, dependencies versions
- **Logs**: Relevant log output (use DEBUG mode)
- **Screenshots**: If applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title**: Descriptive title for the suggestion
- **Detailed description**: Explain the enhancement and why it would be useful
- **Examples**: Provide examples of how it would work
- **Mockups**: If applicable, include mockups or diagrams

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** if applicable
4. **Update documentation** as needed
5. **Ensure tests pass** locally
6. **Commit your changes** with clear commit messages
7. **Push to your fork** and submit a pull request

## Development Setup

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

Quick start:

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/remnabot.git
cd remnabot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run in debug mode
DEBUG=True LOG_LEVEL=DEBUG python -m src.main
```

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Code Formatting

Use automated formatters:

```bash
# Format code
black src/
isort src/

# Check formatting
black --check src/
isort --check-only src/
flake8 src/
```

### Example Code Style

```python
"""
Module docstring explaining the purpose
"""
from typing import Dict, Any, Optional

from telegram import Update
from telegram.ext import ContextTypes

from src.core.logger import log
from src.middleware.auth import admin_only


@admin_only
async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler function description
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        None
    """
    query = update.callback_query
    
    try:
        # Implementation
        result = await some_async_function()
        
        await query.edit_message_text(
            f"Result: {result}",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        log.error(f"Error in my_handler: {e}")
        await query.answer("Error occurred", show_alert=True)


async def some_async_function() -> Dict[str, Any]:
    """Helper function with clear purpose"""
    return {"status": "success"}
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:

```
feat: add user search functionality
fix: correct pagination calculation in users list
docs: update README with new features
style: format code with black
refactor: extract API client to separate module
test: add tests for user handlers
chore: update dependencies
```

## Testing

### Writing Tests

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.handlers.users import users_list_callback


@pytest.mark.asyncio
async def test_users_list_callback():
    """Test users list callback"""
    # Setup
    update = MagicMock()
    context = MagicMock()
    
    # Mock API response
    api_client.get_users = AsyncMock(return_value={
        'data': [{'username': 'test', 'uuid': '123'}],
        'total': 1
    })
    
    # Execute
    await users_list_callback(update, context)
    
    # Assert
    update.callback_query.edit_message_text.assert_called_once()
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_handlers/test_users.py

# Run specific test
pytest tests/test_handlers/test_users.py::test_users_list_callback
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Brief description of function
    
    Longer description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something is wrong
    """
    pass
```

### Updating Documentation

When adding new features:

1. Update README.md if it affects user-facing features
2. Update DEVELOPMENT.md if it affects development setup
3. Update STRUCTURE.md if it changes project structure
4. Add entries to CHANGELOG.md

## Review Process

### Pull Request Checklist

Before submitting:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main branch

### What to Expect

1. **Automated checks**: CI will run linters and tests
2. **Code review**: Maintainers will review your code
3. **Feedback**: You may be asked to make changes
4. **Approval**: Once approved, PR will be merged

## Questions?

- Check [README.md](README.md)
- Check [DEVELOPMENT.md](DEVELOPMENT.md)
- Open an issue with your question
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
