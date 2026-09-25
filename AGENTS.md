# memberful

Typed Python client for [Memberful](https://memberful.com): Pydantic models and parsing for its webhooks, and an async client for its GraphQL API. Published to PyPI as `memberful`.

## Layout

```
src/memberful/
├── __init__.py          # __version__, exposes the api and webhooks submodules only
├── py.typed             # PEP 561 marker (tests/test_packaging.py checks it ships)
├── api/
│   ├── __init__.py      # MemberfulClient (async, httpx2 + stamina retries, GraphQL)
│   └── models.py        # Member, Subscription, *Response models (camelCase GraphQL fields)
└── webhooks/
    ├── __init__.py      # parse_payload(), validate_signature(), UnsupportedEventError
    └── models.py        # One model per webhook event + supporting models/enums, WebhookEvent alias

tests/                   # test_api, test_webhooks, test_webhook_models, test_packaging
examples/                # basic API/webhook usage, fastapi_webhook_example/
reference/webhooks.md    # Local copy of Memberful's webhook JSON payloads + matching models
reference/api.md         # GraphQL API notes
plans/                   # Working notes from past changes; not shipped
```

The top-level package deliberately exports nothing but the two submodules. Users import from `memberful.api` or `memberful.webhooks`.

## Commands

Use the local `venv/` (Python 3.13). It isn't necessarily activated, so call tools through it:

```bash
uv pip install -e ".[dev]"          # setup
venv/bin/pytest                     # tests; coverage runs automatically, fails under 80%
venv/bin/ruff format . && venv/bin/ruff check --fix .
uvx ty check                        # type checker is ty, not mypy
uv build
```

Run all of these (tests, ruff, ty) before calling a change done.

## Code style

- **Python 3.10 is the floor** (`requires-python = ">=3.10"`). ty checks against 3.10 (`ty.toml`), so don't use newer syntax or stdlib APIs in `src/`, even though the dev venv is 3.13.
- **Formatting comes from `ruff.toml`**: 120-char lines, single quotes.
- **Optionals and unions:** write `Optional[X]` and `Union[A, B]` to match the existing code, not `X | None`. Use builtin generics (`list[int]`, `dict[str, Any]`).
- **Full type annotations on everything public.** The package ships `py.typed`, so downstream type checkers read these annotations.
- Prefer guard clauses and early returns over nested conditionals.
- No `#!/usr/bin/env python3` shebangs in library modules.

## Webhooks: the rules that matter

Memberful retries a failing webhook delivery for up to 24 hours and deletes endpoints that are still failing 3 days later. A model that is too strict breaks users' integrations, so:

- **The official reference is the source of truth:** <https://memberful.com/help/custom-development-and-api/webhook-event-reference/>. Check payload shapes there, then update `reference/webhooks.md` to match. Don't guess field names or nesting.
- **Keep models permissive.** Make fields `Optional` with defaults when Memberful may omit or null them. For enum-like strings, use `Union[TheEnum, str]` with `Field(union_mode='left_to_right')` (see `Order.status`) so that a value Memberful adds later doesn't fail validation.
- **Adding an event** means updating the model in `webhooks/models.py`, the `WebhookEvent` alias, the event-type mapping in `parse_payload()`, `reference/webhooks.md`, tests using the documented JSON payload, and the CHANGELOG.
- Event types we don't model raise `UnsupportedEventError` (a `ValueError` subclass). Keep it that way so handlers can acknowledge those events with a 2xx.

## API client

- Async only. Users use it as `async with MemberfulClient(api_key=..., base_url=...) as client:`.
- The HTTP library is `httpx2` imported as `httpx`, not `httpx`. Retries go through `stamina`.
- API models mirror Memberful's GraphQL schema, so field names are camelCase and pagination is cursor-based (`edges`/`nodes`/`pageInfo`).

## Releases and git

- Work happens on `dev`; `main` is the release branch.
- The version lives in two places: `pyproject.toml` and `src/memberful/__init__.py` (`__version__`). Bump both.
- Record every user-visible change in `CHANGELOG.md` (Keep a Changelog format) under `[Unreleased]`, or under the new version when releasing.
- When examples or the README describe the API, keep them in sync with the models. They have drifted before.
