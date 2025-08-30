# Memberful Python Client - Cursor Rules

This is a Python package for interacting with Memberful's webhooks and API, designed for PyPI publication.

## Project Overview

- **Purpose**: Type-safe Python client for Memberful webhooks and API
- **Package Name**: `memberful`
- **Python Version**: 3.13+ (using latest syntax)
- **Key Features**: Pydantic webhook models, async API client, signature verification

## Project Structure

```
src/memberful/
├── __init__.py           # Main package exports
├── client.py            # Async API client (httpx-based)
├── webhooks.py          # Webhook handler with signature verification
└── webhook_models.py    # Pydantic models for all webhook events

tests/
├── test_client.py       # API client tests
├── test_webhooks.py     # Webhook handler tests
└── test_webhook_models.py # Webhook model tests

examples/
├── basic_usage.py       # API usage examples
└── webhook_parsing.py   # Webhook parsing examples

reference/
└── webhooks.md          # 🎯 WEBHOOK REFERENCE - Complete JSON schemas + Pydantic models
```

## 🚨 IMPORTANT: Working with Webhooks

When working with webhooks, **ALWAYS** reference:

1. **`reference/webhooks.md`** - Complete webhook reference with:
   - JSON schemas for all Memberful webhook events
   - Corresponding Pydantic model names
   - Usage examples and import statements
   
2. **`src/memberful/webhook_models.py`** - Type-safe Pydantic models for:
   - All webhook event types (12+ models)
   - Supporting models (Member, Order, Product, etc.)
   - Enums for known values (SignupMethod, OrderStatus, etc.)
   - WebhookEvent union type for parsing

3. **`src/memberful/webhooks.py`** - Webhook handler with:
   - HMAC signature verification
   - Event-based handler registration
   - Decorator pattern for event handling

## Development Standards

### Code Style
- **Language**: Python 3.13+ with latest syntax features
- **Formatting**: Use `ruff format` and `ruff check --fix`
- **Type Hints**: Full type annotations (no `#!/usr/bin/env python3` headers)
- **Imports**: Use builtin types (e.g., `list[int]` not `typing.List[int]`)
- **Optionals**: Use `Optional[type]` not `type | None`
- **Error Handling**: Implement proper error handling with guarding clauses

### Dependencies
- **HTTP Client**: `httpx` for async requests
- **Validation**: `pydantic` for data models
- **Packaging**: `uv` for dependency management
- **Testing**: `pytest` with `pytest-asyncio`
- **Linting**: `ruff`

### Testing
- **Framework**: pytest (19 tests currently passing)
- **Structure**: Separate test files per module
- **Coverage**: Aim for comprehensive coverage of webhook parsing
- **Async Testing**: Use `pytest-asyncio` for API client tests

## Key Conventions

### Webhook Models
- All models are **permissive** - use `Optional` for nullable fields
- Default values applied from JSON examples where appropriate
- Enum classes for known string values (SignupMethod, OrderStatus, etc.)
- Union type `WebhookEvent` for discriminated parsing

### API Client
- Async/await patterns throughout
- Context manager support (`async with client:`)
- Proper error handling and HTTP status checking
- Configurable timeouts and base URLs

### File Naming
- Use descriptive names: `webhook_models.py`, `test_webhook_models.py`
- Follow Python package conventions
- Keep examples in `examples/` directory

## Commands

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run tests
python -m pytest -v

# Format code
ruff format . && ruff check --fix .

# Type checking
mypy src/

# Build package
uv build
```

## Important Files

- **`pyproject.toml`** - Complete PyPI configuration with metadata
- **`pytest.ini`** - Test configuration (separate from pyproject.toml per preference)
- **`reference/webhooks.md`** - 🎯 THE definitive webhook reference
- **`CHANGELOG.md`** - Track all major changes and features

## Notes

- Package follows PyPI best practices for distribution
- All webhook events have corresponding Pydantic models
- Signature verification implements HMAC-SHA256 validation
- Built for production use with comprehensive error handling
