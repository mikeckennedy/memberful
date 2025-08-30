# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial package structure with support for Memberful API client
- Webhook handling capabilities with signature verification
- Support for common Memberful API endpoints (members, subscriptions)
- Comprehensive Pydantic models for all Memberful webhook events
  - Type-safe parsing and validation of webhook payloads
  - Support for all documented webhook events (member, subscription, order, plan, download)
  - Permissive field handling with optional fields and default values
  - Enum support for known values (signup methods, order statuses, etc.)
- Comprehensive test suite setup with pytest (19 passing tests)
- Development tooling setup (ruff, mypy, pre-commit)
- PyPI packaging configuration
- Example code for webhook parsing and API usage

## [0.1.0] - 2024-12-28

### Added
- Initial project skeleton created
- Basic project structure for PyPI publishing
- Core modules: client.py and webhooks.py
- Test structure with pytest configuration
- Development environment setup with uv
