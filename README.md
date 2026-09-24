# Memberful Python SDK

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-brightgreen.svg)](https://docs.pydantic.dev/)

A modern, type-safe Python SDK for integrating with [Memberful](https://memberful.com)'s API and webhooks. Built with Pydantic models for comprehensive type hints and runtime validation.

## ✨ Key Features

- **🔒 Type Safety**: Full Pydantic model coverage for all API responses and webhook events
- **🚀 Async First**: Built on `httpx2` for high-performance async operations
- **⚡ GraphQL Powered**: Efficient data fetching with Memberful's GraphQL API
- **🔄 Resilient**: Smart retry logic with exponential backoff handles network hiccups and rate limits automatically
- **📝 Auto-Complete Heaven**: Comprehensive type hints mean your IDE knows exactly what's available
- **🎯 Zero Guesswork**: No more digging through API docs to figure out response formats
- **🪝 Webhook Support**: Parse and validate webhook events with confidence
- **📚 Rich Documentation**: Detailed examples and comprehensive API documentation
- **🧪 Tested**: Test suite covering webhook parsing and the API data models
- **🐍 Modern Python**: Supports Python 3.10+ with all the latest features

## 📦 Installation

```bash
uv pip install memberful
```

Or with uv project management:

```bash
uv add memberful
```

## 🚀 Quick Start

### API Client

```python
import memberful.api

# Initialize the client with your API key and your Memberful account's URL
async with memberful.api.MemberfulClient(
    api_key="YOUR_API_KEY",
    base_url="https://youraccount.memberful.com",
) as client:
    # Get all members with full type safety
    members = await client.get_all_members()
    
    for member in members:
        print(f"{member.full_name} - {member.email}")
        
        # Your IDE provides auto-complete for all attributes!
        if member.subscriptions:
            active_subs = [s for s in member.subscriptions if s.active]
            print(f"  Active subscriptions: {len(active_subs)}")
```

### Webhook Handling

```python
import memberful.webhooks
import json

def handle_webhook(request_body: str, signature_header: str, webhook_secret: str):
    # Verify the webhook signature
    if not memberful.webhooks.validate_signature(
        payload=request_body,
        signature=signature_header,
        secret_key=webhook_secret
    ):
        raise ValueError("Invalid webhook signature")
    
    # Parse the event with full type safety
    try:
        event = memberful.webhooks.parse_payload(json.loads(request_body))
    except memberful.webhooks.UnsupportedEventError:
        # Event types this package doesn't model (e.g. custom_fields.updated).
        # Acknowledge with a 2xx anyway: Memberful retries failures and eventually
        # deletes endpoints that keep failing.
        return
    
    # Handle different event types with isinstance checks
    match event:
        case memberful.webhooks.MemberSignupEvent():
            print(f"New member: {event.member.email}")
        case memberful.webhooks.SubscriptionCreatedEvent():
            print(f"New subscription for: {event.subscription.member.email}")
        case _:
            print(f"Received {event.event} event")
```

## 📖 Documentation

### Comprehensive Guides

- **[API Documentation](reference/api.md)** - Complete guide to using the API client with examples
- **[Webhook Documentation](reference/webhooks.md)** - Detailed webhook event reference and handling guide

### Quick Examples

Check out the [examples directory](examples/) for ready-to-run code:
- [Basic API Usage](examples/basic_api_usage.py) - Simple examples to get started
- [Webhook Usage](examples/basic_webhook_usage.py) - Webhook handling patterns
- [Webhook Parsing](examples/webhook_parsing.py) - Detailed webhook parsing examples
- [FastAPI Integration](examples/fastapi_webhook_example/) - Complete FastAPI webhook server

## 🛠️ Core Features

### API Client Capabilities

- ✅ Fetch members (individual, paginated, or all)
- ✅ Retrieve subscriptions with full plan details
- ✅ Automatic pagination handling
- ✅ **Smart retry logic** with exponential backoff (3 attempts, handles network errors)
- ✅ Configurable request timeout
- ✅ Type-safe responses with Pydantic models
- ✅ Comprehensive error handling

### Webhook Features

- ✅ Type-safe parsing of all webhook event types
- ✅ HMAC signature verification with `validate_signature()`
- ✅ Support for 20 Memberful webhook events:
  - **Member events**: signup, updated, deleted
  - **Subscription events**: created, updated, activated, deactivated, deleted, renewed, reactivated
  - **Order events**: purchased, refunded, completed, suspended
  - **Plan events**: created, updated, deleted
  - **Download events**: created, updated, deleted
- ✅ Pydantic models for each event type
- ✅ `UnsupportedEventError` for events not modeled here (`custom_fields.updated`, `tax_id.updated`), so you can acknowledge and ignore them

## 🏗️ Architecture

This SDK is built with modern Python best practices:

- **GraphQL API** - leverages Memberful's GraphQL endpoint for efficient data fetching
- **Async/await** for efficient I/O operations
- **Pydantic v2** for fast data validation and serialization
- **Type hints** throughout for better IDE support
- **Minimal dependencies** - just `httpx2`, `pydantic`, and `stamina` for resilient retries

## 🧪 Testing

The SDK includes a comprehensive test suite. Run tests with:

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=memberful
```

## 🤝 Contributing

We love contributions! If you've found a bug or have a feature request:

1. **Check existing issues** first to avoid duplicates
2. **Open an issue** to discuss the change
3. **Submit a PR** with your improvements

### Development Setup

```bash
# Clone the repo
git clone https://github.com/mikeckennedy/memberful.git
cd memberful

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff format

# Run linter
ruff check

# Type check
uvx ty check
```

## 📊 Project Status

This SDK is under active development and currently supports:

- ✅ Member operations (read)
- ✅ Subscription operations (read)
- ✅ All documented webhook event types except `custom_fields.updated` and `tax_id.updated`
- ✅ Signature verification
- ⏳ Member operations (create/update) - coming soon
- ✅ GraphQL API integration with automatic retries

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the [Memberful](https://memberful.com) community
- Inspired by modern Python SDK design patterns
- Special thanks to all contributors

## 📬 Support

- 📖 [Read the documentation](reference/)
- 🐛 [Report bugs](https://github.com/mikeckennedy/memberful/issues)
- 💡 [Request features](https://github.com/mikeckennedy/memberful/issues)
- 💬 [Discussions](https://github.com/mikeckennedy/memberful/discussions)

---

**Ready to integrate Memberful into your Python application? [Get started now!](#-quick-start)**
