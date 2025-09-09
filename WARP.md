# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Quick Start Commands

| Task | Command |
|------|---------|
| **Setup** | `uv pip install -e ".[dev]"` |
| **Run Tests** | `pytest` or `python -m pytest -v` |
| **Test with Coverage** | `pytest --cov=src/memberful --cov-report=term-missing` |
| **Format Code** | `ruff format .` |
| **Lint & Fix** | `ruff check --fix .` |
| **Type Check** | `mypy src/` |
| **Build Package** | `uv build` |
| **Run Example** | `python examples/basic_api_usage.py` |

## Architecture Overview

The Memberful Python SDK is a modern async-first client library with two main components:

### GraphQL API Client (`memberful.api`)
- **Async HTTP Transport**: Built on `httpx.AsyncClient` with Bearer token authentication
- **GraphQL Native**: Uses Memberful's actual GraphQL schema with cursor-based pagination
- **Smart Retries**: `stamina` library provides exponential backoff for network errors and rate limits
- **Type Safety**: All responses parsed into Pydantic v2 models with full IDE support

```
MemberfulClient → GraphQL Query → httpx → stamina retry → Pydantic models
```

### Webhook Handler (`memberful.webhooks`)
- **Signature Verification**: HMAC-SHA256 validation of webhook payloads
- **Type-Safe Parsing**: 16+ webhook event types with dedicated Pydantic models
- **Event Discrimination**: Union types automatically route to correct event model

```
Raw Webhook → Signature Check → parse_payload() → Typed Event Model
```

## Project Structure

```
src/memberful/
├── __init__.py              # Package exports (api, webhooks submodules)
├── api/
│   ├── __init__.py         # MemberfulClient with async GraphQL operations  
│   └── models.py           # Member, Subscription, Plan Pydantic models
└── webhooks/
    ├── __init__.py         # parse_payload(), validate_signature() functions
    └── models.py           # 16+ webhook event models + supporting types

tests/
├── test_api.py             # API client tests (async)
├── test_webhooks.py        # Webhook parsing and signature validation
└── test_webhook_models.py  # Pydantic model validation tests

examples/
├── basic_api_usage.py      # Complete async client example
├── basic_webhook_usage.py  # Webhook handling patterns
├── webhook_parsing.py      # Event type parsing examples
└── fastapi_webhook_example/ # Production FastAPI webhook server
```

## Development Patterns

### Async/Await First
All API operations are async. Always use context managers for proper resource cleanup:

```python
async with MemberfulClient(api_key="...") as client:
    members = await client.get_all_members()  # Handles pagination automatically
    member = await client.get_member(member_id=123)
```

### GraphQL Field Alignment  
The SDK uses Memberful's actual GraphQL schema:
- Field names are camelCase (e.g., `fullName`, `stripeCustomerId`)
- Cursor-based pagination with `edges`, `nodes`, `pageInfo`
- Limited to fields actually available in the schema

### Webhook Event Handling
Use pattern matching for type-safe event processing:

```python
event = parse_payload(webhook_data)
match event:
    case MemberSignupEvent():
        handle_signup(event.member)
    case SubscriptionCreatedEvent():
        handle_subscription(event.subscriptions[0])
```

### Pydantic Model Extensions
All models support extra fields via `model_extra = "forbid"` by default. Add new fields by extending base models:

```python
class CustomMember(Member):
    custom_field: Optional[str] = None
```

## Configuration Details

### Ruff (Linting & Formatting)
- **Line Length**: 120 characters
- **Quote Style**: Single quotes (`'`)  
- **Target**: Python 3.10+
- **Rules**: pycodestyle, pyflakes, isort, refurb modernization
- **Conflicts**: Line length handled by formatter, not linter

### Pytest Configuration  
- **Test Discovery**: `tests/test_*.py` pattern
- **Coverage**: 80% minimum threshold with HTML/XML reports
- **Async Support**: `pytest-asyncio` for async test functions
- **Markers**: `slow`, `integration`, `unit` for test categorization

### MyPy Type Checking
- **Strict Mode**: Disallows untyped definitions and decorators
- **Target**: Python 3.10+ type features
- **Coverage**: Full type annotations required for src/, relaxed for tests/

## Testing Strategy

### Test Organization
- **`test_api.py`**: Mock httpx responses for GraphQL queries, test pagination logic
- **`test_webhooks.py`**: Signature validation, payload parsing, error handling  
- **`test_webhook_models.py`**: Pydantic model validation with real webhook JSON samples

### Mock Patterns
Uses `pytest-asyncio` for async tests. API tests should mock httpx responses:

```python
@pytest.mark.asyncio
async def test_get_members():
    # Mock GraphQL response structure
    mock_response = {...}
```

### Coverage Requirements
- **Minimum**: 80% line coverage enforced by pytest
- **Reports**: Terminal, HTML (`htmlcov/`), and XML formats
- **Focus**: Core parsing logic, error handling, retry mechanisms

## Key Architectural Decisions

### Why GraphQL Over REST
Memberful's API is GraphQL-native. The SDK uses actual schema fields rather than assuming REST patterns, providing more efficient data fetching and better type alignment.

### Why Pydantic v2
- **Performance**: Significantly faster than v1 for parsing large webhook payloads
- **Type Safety**: Full runtime validation with static type checking
- **Forward Compatibility**: `extras` field handles new webhook data gracefully

### Why Stamina for Retries
- **Smart Backoff**: Exponential backoff with jitter for rate limits
- **Context Manager**: Clean async patterns with automatic retry logic
- **Error Classification**: Distinguishes network errors from API errors

### Why Async-First
Memberful APIs are I/O bound. Async patterns enable efficient pagination of large member lists and concurrent webhook processing without blocking.

### Package Structure Rationale
- **Namespace Separation**: `memberful.api` vs `memberful.webhooks` prevents import conflicts
- **No Top-Level Pollution**: Users explicitly import what they need
- **Extension Points**: Clear separation enables custom client configurations and webhook handlers
