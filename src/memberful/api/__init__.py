"""Memberful API client."""

import asyncio
import warnings
from collections.abc import AsyncGenerator
from typing import Any, Optional

import httpx2 as httpx
import stamina
from pydantic import BaseModel

from .. import __version__
from .models import (
    Member,
    MembersResponse,
    Subscription,
    SubscriptionsResponse,
)

PLAN_FIELDS_FRAGMENT = """
fragment PlanFields on Plan {
    id
    name
    price: priceCents
    slug
    intervalUnit
    intervalCount
    forSale
}
"""

MEMBER_FIELDS_FRAGMENT = """
fragment MemberFields on Member {
    id
    email
    fullName
    username
    phoneNumber
    stripeCustomerId
    discordUserId
    unrestrictedAccess
    address {
        city
        country
        state
        postalCode
        street
    }
}
"""

SUBSCRIPTION_FIELDS_FRAGMENT = """
fragment SubscriptionFields on Subscription {
    id
    active
    createdAt
    expiresAt
    activatedAt
    trialEndAt
    trialStartAt
    autorenew
    plan {
        ...PlanFields
    }
    member {
        ...MemberFields
    }
}
"""

# One shared fragment per GraphQL type (Plan, Member, Subscription), so every query below selects
# the same fields the same way instead of drifting apart. Field names and nullability were checked
# against models.py's requirements and against Memberful's live schema (talkpython.memberful.com,
# introspected 2026-09-25); `price: priceCents` is a GraphQL alias because Plan.price is a required
# model field but Memberful's schema has no `price` field, only `priceCents`. See models.py's Plan
# and Subscription docstrings/comments for the fields Memberful's schema doesn't have at all.
_GRAPHQL_FRAGMENTS = PLAN_FIELDS_FRAGMENT + MEMBER_FIELDS_FRAGMENT + SUBSCRIPTION_FIELDS_FRAGMENT

_GET_MEMBERS_QUERY = (
    _GRAPHQL_FRAGMENTS
    + """
query GetMembers($first: Int!, $after: String) {
    members(first: $first, after: $after) {
        edges {
            node {
                ...MemberFields
                subscriptions {
                    ...SubscriptionFields
                }
            }
            cursor
        }
        pageInfo {
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
        }
    }
}
"""
)

_GET_MEMBER_QUERY = (
    _GRAPHQL_FRAGMENTS
    + """
query GetMember($id: ID!) {
    member(id: $id) {
        ...MemberFields
        subscriptions {
            ...SubscriptionFields
        }
    }
}
"""
)

_GET_MEMBER_SUBSCRIPTIONS_QUERY = (
    _GRAPHQL_FRAGMENTS
    + """
query GetMemberSubscriptions($memberId: ID!, $first: Int!, $after: String) {
    member(id: $memberId) {
        subscriptions(first: $first, after: $after) {
            edges {
                node {
                    ...SubscriptionFields
                }
                cursor
            }
            pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
            }
        }
    }
}
"""
)

_GET_ALL_SUBSCRIPTIONS_QUERY = (
    _GRAPHQL_FRAGMENTS
    + """
query GetAllSubscriptions($first: Int!, $after: String) {
    subscriptions(first: $first, after: $after) {
        edges {
            node {
                ...SubscriptionFields
            }
            cursor
        }
        pageInfo {
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
        }
    }
}
"""
)


# ValueError covers GraphQL errors from _graphql_request (and pydantic's ValidationError, a subclass).
_RETRYABLE_ERRORS = (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException, ValueError)


def _check_deprecated_page(page: Optional[int], after: Optional[str]) -> None:
    """Warn about the deprecated `page` argument, and refuse page numbers that can't be honored.

    Memberful's GraphQL API only supports cursors, so page N can't be fetched directly. Returning
    page 1 labelled as page N (the pre-0.4.0 behavior) silently broke callers' loops.
    """
    if page is None:
        return

    warnings.warn(
        "`page` is deprecated: Memberful pagination is cursor-based. Pass the previous response's "
        '`end_cursor` as `after`, or use iter_members()/iter_subscriptions().',
        DeprecationWarning,
        stacklevel=3,
    )
    if page > 1 and after is None:
        raise ValueError(
            f"page={page} requires a cursor: pass the previous page's `end_cursor` as `after`, "
            'or use iter_members()/iter_subscriptions() to walk every page.'
        )


class MemberfulClientConfig(BaseModel):
    """Configuration for the Memberful client."""

    api_key: str
    base_url: str = 'https://youraccount.memberful.com'
    timeout: float = 30.0


class MemberfulClient:
    request_timeout_in_seconds: float = 20.0
    """Client for interacting with the Memberful API."""

    def __init__(
        self, api_key: str, base_url: str = 'https://youraccount.memberful.com', timeout: float = 30.0
    ) -> None:
        """Initialize the Memberful client.

        Args:
            api_key: Your Memberful API key
            base_url: Base URL for the Memberful API
            timeout: Request timeout in seconds
        """
        self.config = MemberfulClientConfig(api_key=api_key, base_url=base_url, timeout=timeout)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> 'MemberfulClient':
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure the HTTP client is initialized."""
        if not self._client:
            headers = {
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': f'memberful-python/{__version__}',
            }
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout,
            )
        return self._client

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make an HTTP request to the Memberful API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments passed to httpx

        Returns:
            httpx.Response object
        """
        client = await self._ensure_client()
        response = await client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def _graphql_request(self, query: str, variables: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make a GraphQL request to the Memberful API.

        Args:
            query: GraphQL query string
            variables: Optional variables for the query

        Returns:
            Response data from GraphQL API
        """
        client = await self._ensure_client()

        payload: dict[str, Any] = {'query': query}
        if variables:
            payload['variables'] = variables

        response = await client.post('/api/graphql', json=payload)
        response.raise_for_status()

        data = response.json()

        # Check for GraphQL errors
        if 'errors' in data:
            error_messages = [error['message'] for error in data['errors']]
            raise ValueError(f'GraphQL errors: {", ".join(error_messages)}')

        return data.get('data', {})

    async def _fetch_members_page(self, per_page: int, after: Optional[str]) -> MembersResponse:
        """Fetch one page of members starting after the `after` cursor (None means the first page).

        Retries re-send the same cursor; callers only advance their cursor once this returns.
        """
        variables = {'first': per_page, 'after': after}

        async for attempt in stamina.retry_context(
            on=_RETRYABLE_ERRORS,
            attempts=3,
            timeout=self.request_timeout_in_seconds,
        ):
            with attempt:
                data = await self._graphql_request(_GET_MEMBERS_QUERY, variables)
                members_data = data.get('members') or {}

                members: list[Member] = []
                for edge in members_data.get('edges') or []:
                    member_node: dict[str, Any] = edge['node']

                    # Subscriptions come back as a plain list; normalize null to an empty list
                    if 'subscriptions' in member_node and member_node['subscriptions'] is None:
                        member_node['subscriptions'] = []

                    members.append(Member(**member_node))

                page_info = members_data.get('pageInfo') or {}
                return MembersResponse(
                    members=members,
                    per_page=per_page,
                    end_cursor=page_info.get('endCursor'),
                    has_next_page=bool(page_info.get('hasNextPage', False)),
                )
        # This line will never be reached due to stamina's retry logic
        raise RuntimeError('Retry exhausted')  # pragma: no cover

    async def get_members(
        self, page: Optional[int] = None, per_page: int = 100, after: Optional[str] = None
    ) -> MembersResponse:
        """Get one page of members.

        Memberful's API is cursor-based. Pass the previous response's `end_cursor` as `after` to get
        the next page, and stop when `has_next_page` is False. To walk every page, use
        `iter_members()` or `get_all_members()` instead.

        Args:
            page: Deprecated. Page numbers can't be mapped to cursors, so `page > 1` without `after`
                raises ValueError. Use `after` instead.
            per_page: Number of members per page (default: 100)
            after: Cursor to start after (the previous page's `end_cursor`); None for the first page

        Returns:
            MembersResponse with the page's members, `end_cursor` and `has_next_page`
        """
        _check_deprecated_page(page, after)

        response = await self._fetch_members_page(per_page, after)
        response.current_page = page
        return response

    async def iter_members(
        self, per_page: int = 100, after: Optional[str] = None
    ) -> AsyncGenerator[MembersResponse, None]:
        """Yield pages of members lazily, following cursors until the last page.

        Each page is requested only when the caller asks for it, so large accounts don't need to hold
        every member in memory. Waits 0.25 seconds between pages to be gentle on Memberful's API.

        Args:
            per_page: Number of members per page (default: 100)
            after: Cursor to resume after (a previous page's `end_cursor`); None starts at the beginning

        Yields:
            MembersResponse for each page
        """
        cursor = after
        while True:
            response = await self._fetch_members_page(per_page, cursor)
            yield response

            # An empty page or a missing cursor would otherwise loop forever
            if not response.members or not response.has_next_page or response.end_cursor is None:
                return

            cursor = response.end_cursor
            await asyncio.sleep(0.25)

    async def get_all_members(self) -> list[Member]:
        """Get all members by following cursors through every page (100 members per page).

        Returns:
            List containing all Member objects
        """
        all_members: list[Member] = []
        async for response in self.iter_members(per_page=100):
            all_members.extend(response.members)

        return all_members

    async def get_member(self, member_id: int) -> Member:
        """Get a specific member by ID.

        Args:
            member_id: The member's ID

        Returns:
            Member object containing member data
        """
        variables = {'id': str(member_id)}

        async for attempt in stamina.retry_context(
            on=_RETRYABLE_ERRORS,
            attempts=3,
            timeout=self.request_timeout_in_seconds,
        ):
            with attempt:
                data = await self._graphql_request(_GET_MEMBER_QUERY, variables)
                member_data = data.get('member')

                if not member_data:
                    raise ValueError(f'Member with ID {member_id} not found')

                # Subscriptions are already in the correct format (no edges needed)
                # Just ensure they exist as a list
                if 'subscriptions' in member_data and member_data['subscriptions'] is None:
                    member_data['subscriptions'] = []

                return Member(**member_data)
        # This line will never be reached due to stamina's retry logic
        raise RuntimeError('Retry exhausted')  # pragma: no cover

    async def _fetch_subscriptions_page(
        self, member_id: Optional[int], per_page: int, after: Optional[str]
    ) -> SubscriptionsResponse:
        """Fetch one page of subscriptions (optionally for one member) starting after the `after` cursor.

        Retries re-send the same cursor; callers only advance their cursor once this returns.
        """
        if member_id:
            query = _GET_MEMBER_SUBSCRIPTIONS_QUERY
            variables: dict[str, Any] = {'memberId': str(member_id), 'first': per_page, 'after': after}
        else:
            query = _GET_ALL_SUBSCRIPTIONS_QUERY
            variables = {'first': per_page, 'after': after}

        async for attempt in stamina.retry_context(
            on=_RETRYABLE_ERRORS,
            attempts=3,
            timeout=self.request_timeout_in_seconds,
        ):
            with attempt:
                data = await self._graphql_request(query, variables)

                if member_id:
                    subscriptions_data = (data.get('member') or {}).get('subscriptions') or {}
                else:
                    subscriptions_data = data.get('subscriptions') or {}

                subscriptions = [Subscription(**edge['node']) for edge in subscriptions_data.get('edges') or []]

                page_info = subscriptions_data.get('pageInfo') or {}
                return SubscriptionsResponse(
                    subscriptions=subscriptions,
                    per_page=per_page,
                    end_cursor=page_info.get('endCursor'),
                    has_next_page=bool(page_info.get('hasNextPage', False)),
                )
        # This line will never be reached due to stamina's retry logic
        raise RuntimeError('Retry exhausted')  # pragma: no cover

    async def get_subscriptions(
        self,
        member_id: Optional[int] = None,
        page: Optional[int] = None,
        per_page: int = 100,
        after: Optional[str] = None,
    ) -> SubscriptionsResponse:
        """Get one page of subscriptions, optionally for a specific member.

        Memberful's API is cursor-based. Pass the previous response's `end_cursor` as `after` to get
        the next page, and stop when `has_next_page` is False. To walk every page, use
        `iter_subscriptions()` or `get_all_subscriptions()` instead.

        Args:
            member_id: Optional member ID to filter subscriptions
            page: Deprecated. Page numbers can't be mapped to cursors, so `page > 1` without `after`
                raises ValueError. Use `after` instead.
            per_page: Number of subscriptions per page (default: 100)
            after: Cursor to start after (the previous page's `end_cursor`); None for the first page

        Returns:
            SubscriptionsResponse with the page's subscriptions, `end_cursor` and `has_next_page`
        """
        _check_deprecated_page(page, after)

        response = await self._fetch_subscriptions_page(member_id, per_page, after)
        response.current_page = page
        return response

    async def iter_subscriptions(
        self, member_id: Optional[int] = None, per_page: int = 100, after: Optional[str] = None
    ) -> AsyncGenerator[SubscriptionsResponse, None]:
        """Yield pages of subscriptions lazily, following cursors until the last page.

        Each page is requested only when the caller asks for it. Waits 0.25 seconds between pages to
        be gentle on Memberful's API.

        Args:
            member_id: Optional member ID to filter subscriptions for a specific member
            per_page: Number of subscriptions per page (default: 100)
            after: Cursor to resume after (a previous page's `end_cursor`); None starts at the beginning

        Yields:
            SubscriptionsResponse for each page
        """
        cursor = after
        while True:
            response = await self._fetch_subscriptions_page(member_id, per_page, cursor)
            yield response

            # An empty page or a missing cursor would otherwise loop forever
            if not response.subscriptions or not response.has_next_page or response.end_cursor is None:
                return

            cursor = response.end_cursor
            await asyncio.sleep(0.25)

    async def get_all_subscriptions(self, member_id: Optional[int] = None) -> list[Subscription]:
        """Get all subscriptions by following cursors through every page (100 subscriptions per page).

        Args:
            member_id: Optional member ID to filter subscriptions for specific member

        Returns:
            List containing all Subscription objects
        """
        all_subscriptions: list[Subscription] = []
        async for response in self.iter_subscriptions(member_id=member_id, per_page=100):
            all_subscriptions.extend(response.subscriptions)

        return all_subscriptions

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


__all__ = [
    # Client
    'MemberfulClient',
    'MemberfulClientConfig',
    # Models returned by the client
    'Member',
    'MembersResponse',
    'Subscription',
    'SubscriptionsResponse',
]
