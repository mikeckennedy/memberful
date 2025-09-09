# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Fixed `AttributeError: module stamina has no attribute retry_async` by updating to use correct `stamina.retry_context()` API

### Added
- **Async Memberful API client** (`memberful.api.MemberfulClient`)
  - Support for common endpoints: members, subscriptions with full pagination
  - Automatic retry logic with exponential backoff using stamina
  - Async context manager support for proper resource cleanup
  - Type-safe responses with comprehensive Pydantic models
  - Rate limiting consideration with configurable delays
- **Comprehensive webhook handling** (`memberful.webhooks`)
  - `parse_payload()` function for type-safe webhook parsing
  - `validate_signature()` function for webhook signature verification
  - Support for all documented webhook events (member, subscription, order, plan, download)
  - Automatic event type mapping to appropriate Pydantic models
  - **NEW**: Added support for 4 additional webhook events:
    - `member.deleted` - Handle member deletion events
    - `subscription.activated` - Handle subscription activation events  
    - `subscription.deleted` - Handle subscription deletion events
    - `subscription.renewed` - Handle subscription renewal events
- **Robust Pydantic models** for both API and webhook data
  - Type-safe parsing and validation with permissive field handling
  - Enum support for known values (signup methods, order statuses, renewal periods)
  - Optional fields with sensible defaults for real-world data variations
  - Extra field handling via `extras` property for forward compatibility
- **Clean package structure** with namespace-based access
  - Users access functionality via `memberful.api` and `memberful.webhooks` submodules
  - No top-level namespace pollution - explicit imports required
- **Comprehensive test suite** with 25 passing tests covering:
  - API client functionality and error handling
  - Webhook parsing for all supported event types
  - Model validation with real-world data scenarios
  - Signature verification and security features
- **Complete example implementations**
  - Basic API usage with async/await patterns
  - Webhook processing with signature validation
  - FastAPI webhook server example with testing utilities
- **Development infrastructure**
  - Linting and formatting with ruff
  - Type checking with mypy
  - Pre-commit hooks for code quality
  - PyPI packaging configuration with uv dependency management
