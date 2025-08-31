"""Memberful API client."""

import asyncio
from typing import Any, Optional

import httpx
import stamina
from pydantic import BaseModel

from .models import (
    Member,
    MembersResponse,
    Subscription,
    SubscriptionsResponse,
)


class MemberfulClientConfig(BaseModel):
    """Configuration for the Memberful client."""

    api_key: str
    base_url: str = 'https://youraccount.memberful.com'
    timeout: float = 30.0


class MemberfulClient:
    request_timeout_in_seconds: float = 20.0
    """Client for interacting with the Memberful API."""

    def __init__(self, api_key: str, base_url: str = 'https://youraccount.memberful.com', timeout: float = 30.0):
        """Initialize the Memberful client.

        Args:
            api_key: Your Memberful API key
            base_url: Base URL for the Memberful API
            timeout: Request timeout in seconds
        """
        self.config = MemberfulClientConfig(api_key=api_key, base_url=base_url, timeout=timeout)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
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
                'User-Agent': 'memberful-python/0.1.0',
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

    async def get_members(self, page: int = 1, per_page: int = 100) -> MembersResponse:
        """Get list of members.

        Args:
            page: Page number (default: 1)
            per_page: Number of members per page (default: 100)

        Returns:
            MembersResponse containing members data with pagination info
        """
        # For cursor-based pagination, we'll simulate offset behavior
        # by fetching pages sequentially until we reach the desired page
        cursor = None
        if page > 1:
            # We'll need to implement a cursor store or fetch pages sequentially
            # For now, let's use None and handle pagination differently
            pass

        query = """
        query GetMembers($first: Int!, $after: String) {
            members(first: $first, after: $after) {
                edges {
                    node {
                        id
                        email
                        fullName
                        username
                        stripeCustomerId
                        unrestrictedAccess
                        address {
                            city
                            country
                            state
                            postalCode
                            street
                        }
                        subscriptions {
                            id
                            active
                            createdAt
                            expiresAt
                            trialEndAt
                            plan {
                                id
                                name
                                intervalUnit
                                intervalCount
                                slug
                            }
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

        variables = {'first': per_page, 'after': cursor}

        async for attempt in stamina.retry_context(
            on=(httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException, ValueError),
            attempts=3,
            timeout=self.request_timeout_in_seconds,
        ):
            with attempt:
                data = await self._graphql_request(query, variables)
                members_data = data.get('members', {})

                # Transform GraphQL response to match our expected format
                members: list[dict[str, Any]] = []
                if 'edges' in members_data:
                    for edge in members_data['edges']:
                        member_node: dict[str, Any] = edge['node']

                        # Subscriptions are already in the correct format (no edges needed)
                        # Just ensure they exist as a list
                        if 'subscriptions' in member_node and member_node['subscriptions'] is None:
                            member_node['subscriptions'] = []

                        members.append(member_node)

                # Create response with pagination info
                # Since totalCount is not available in the GraphQL schema, we'll estimate based on hasNextPage
                page_info = members_data.get('pageInfo', {})
                has_next_page = page_info.get('hasNextPage', False)
                # Estimate total count - this is imperfect but works for pagination
                total_count: int = len(members) + (per_page if has_next_page else 0)
                total_pages: int = page + (1 if has_next_page else 0)

                response_data: dict[str, Any] = {
                    'members': members,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'current_page': page,
                    'per_page': per_page,
                }

                return MembersResponse(**response_data)
        # This line will never be reached due to stamina's retry logic
        raise RuntimeError('Retry exhausted')  # pragma: no cover

    async def get_all_members(self) -> list[Member]:
        """Get all members by iterating through all pages using cursor-based pagination.

        This method automatically handles pagination by using GraphQL cursors
        until all members are retrieved. Uses 100 members per page for optimal performance.

        Returns:
            List containing all Member objects
        """
        per_page: int = 100
        all_members: list[Member] = []
        cursor: Optional[str] = None
        has_next_page = True

        while has_next_page:
            query = """
            query GetMembers($first: Int!, $after: String) {
                members(first: $first, after: $after) {
                    edges {
                        node {
                            id
                            email
                            fullName
                            username
                            stripeCustomerId
                            unrestrictedAccess
                            address {
                                city
                                country
                                state
                                postalCode
                                street
                            }
                            subscriptions {
                                id
                                active
                                createdAt
                                expiresAt
                                trialEndAt
                                plan {
                                    id
                                    name
                                    intervalUnit
                                    intervalCount
                                    slug
                                }
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

            variables = {'first': per_page, 'after': cursor}

            async for attempt in stamina.retry_context(
                on=(httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException, ValueError),
                attempts=3,
                timeout=self.request_timeout_in_seconds,
            ):
                with attempt:
                    data = await self._graphql_request(query, variables)
                    members_data = data.get('members', {})

                    # Extract members from edges
                    members: list[Member] = []
                    if 'edges' in members_data:
                        for edge in members_data['edges']:
                            member_node: dict[str, Any] = edge['node']

                            # Ensure subscriptions exist as a list
                            if 'subscriptions' in member_node and member_node['subscriptions'] is None:
                                member_node['subscriptions'] = []

                            members.append(Member(**member_node))

                    # Update pagination info
                    page_info = members_data.get('pageInfo', {})
                    has_next_page = page_info.get('hasNextPage', False)
                    cursor = page_info.get('endCursor')

                    # Add members to our collection
                    all_members.extend(members)

                    # Break if no more members
                    if not members or not has_next_page:
                        has_next_page = False
                        break

            # Small delay to be respectful of API rate limits
            await asyncio.sleep(0.25)

        return all_members

    async def get_member(self, member_id: int) -> Member:
        """Get a specific member by ID.

        Args:
            member_id: The member's ID

        Returns:
            Member object containing member data
        """
        query = """
        query GetMember($id: ID!) {
            member(id: $id) {
                id
                email
                fullName
                username
                stripeCustomerId
                unrestrictedAccess
                address {
                    city
                    country
                    state
                    postalCode
                    street
                }
                subscriptions {
                    id
                    active
                    createdAt
                    expiresAt
                    trialEndAt
                    plan {
                        id
                        name
                        intervalUnit
                        intervalCount
                        slug
                    }
                }
            }
        }
        """

        variables = {'id': str(member_id)}

        async for attempt in stamina.retry_context(
            on=(httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException, ValueError),
            attempts=3,
            timeout=self.request_timeout_in_seconds,
        ):
            with attempt:
                data = await self._graphql_request(query, variables)
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

    async def get_subscriptions(
        self, member_id: Optional[int] = None, page: int = 1, per_page: int = 100
    ) -> SubscriptionsResponse:
        """Get subscriptions, optionally for a specific member.

        Args:
            member_id: Optional member ID to filter subscriptions
            page: Page number (default: 1)
            per_page: Number of subscriptions per page (default: 100)

        Returns:
            SubscriptionsResponse containing subscriptions data with pagination info
        """
        # For cursor-based pagination
        cursor = None
        if page > 1:
            # For now, we'll implement this as cursor-based without offset simulation
            pass

        if member_id:
            # Get subscriptions for specific member
            query = """
            query GetMemberSubscriptions($memberId: ID!, $first: Int!, $after: String) {
                member(id: $memberId) {
                    subscriptions(first: $first, after: $after) {
                        edges {
                            node {
                                id
                                active
                                createdAt
                                expiresAt
                                trialEndAt
                                plan {
                                    id
                                    name
                                    intervalUnit
                                    intervalCount
                                    slug
                                }
                                member {
                                    id
                                    email
                                    fullName
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
            }
            """
            variables = {'memberId': str(member_id), 'first': per_page, 'after': cursor}
        else:
            # Get all subscriptions
            query = """
            query GetAllSubscriptions($first: Int!, $after: String) {
                subscriptions(first: $first, after: $after) {
                    edges {
                        node {
                            id
                            active
                            createdAt
                            expiresAt
                            trialEndAt
                            plan {
                                id
                                name
                                intervalUnit
                                intervalCount
                                slug
                            }
                            member {
                                id
                                email
                                fullName
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
            variables = {'first': per_page, 'after': cursor}

        async for attempt in stamina.retry_context(
            on=(httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException, ValueError),
            attempts=3,
            timeout=self.request_timeout_in_seconds,
        ):
            with attempt:
                data = await self._graphql_request(query, variables)

                if member_id:
                    # Extract subscriptions from member query
                    member_data = data.get('member', {})
                    subscriptions_data = member_data.get('subscriptions', {})
                else:
                    # Extract subscriptions from direct query
                    subscriptions_data = data.get('subscriptions', {})

                # Transform GraphQL response to match our expected format
                subscriptions: list[dict[str, Any]] = []
                if 'edges' in subscriptions_data:
                    for edge in subscriptions_data['edges']:
                        subscriptions.append(edge['node'])

                # Create response with pagination info
                # Since totalCount is not available in the GraphQL schema, we'll estimate based on hasNextPage
                page_info = subscriptions_data.get('pageInfo', {})
                has_next_page = page_info.get('hasNextPage', False)
                # Estimate total count - this is imperfect but works for pagination
                total_count: int = len(subscriptions) + (per_page if has_next_page else 0)
                total_pages: int = page + (1 if has_next_page else 0)

                response_data: dict[str, Any] = {
                    'subscriptions': subscriptions,
                    'total_count': total_count,
                    'total_pages': total_pages,
                    'current_page': page,
                    'per_page': per_page,
                }

                return SubscriptionsResponse(**response_data)
        # This line will never be reached due to stamina's retry logic
        raise RuntimeError('Retry exhausted')  # pragma: no cover

    async def get_all_subscriptions(self, member_id: Optional[int] = None) -> list[Subscription]:
        """Get all subscriptions by iterating through all pages using cursor-based pagination.

        This method automatically handles pagination by using GraphQL cursors
        until all subscriptions are retrieved. Uses 100 subscriptions per page
        for optimal performance.

        Args:
            member_id: Optional member ID to filter subscriptions for specific member

        Returns:
            List containing all Subscription objects
        """
        per_page: int = 100
        all_subscriptions: list[Subscription] = []
        cursor: Optional[str] = None
        has_next_page = True

        while has_next_page:
            if member_id:
                # Get subscriptions for specific member
                query = """
                query GetMemberSubscriptions($memberId: ID!, $first: Int!, $after: String) {
                    member(id: $memberId) {
                        subscriptions(first: $first, after: $after) {
                            edges {
                                node {
                                    id
                                    active
                                    createdAt
                                    expiresAt
                                    trialEndAt
                                    plan {
                                        id
                                        name
                                        intervalUnit
                                        intervalCount
                                        slug
                                    }
                                    member {
                                        id
                                        email
                                        fullName
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
                }
                """
                variables = {'memberId': str(member_id), 'first': per_page, 'after': cursor}
            else:
                # Get all subscriptions
                query = """
                query GetAllSubscriptions($first: Int!, $after: String) {
                    subscriptions(first: $first, after: $after) {
                        edges {
                            node {
                                id
                                active
                                createdAt
                                expiresAt
                                trialEndAt
                                plan {
                                    id
                                    name
                                    intervalUnit
                                    intervalCount
                                    slug
                                }
                                member {
                                    id
                                    email
                                    fullName
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
                variables = {'first': per_page, 'after': cursor}

            async for attempt in stamina.retry_context(
                on=(httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException, ValueError),
                attempts=3,
                timeout=self.request_timeout_in_seconds,
            ):
                with attempt:
                    data = await self._graphql_request(query, variables)

                    if member_id:
                        # Extract subscriptions from member query
                        member_data = data.get('member', {})
                        subscriptions_data = member_data.get('subscriptions', {})
                    else:
                        # Extract subscriptions from direct query
                        subscriptions_data = data.get('subscriptions', {})

                    # Extract subscriptions from edges
                    subscriptions: list[Subscription] = []
                    if 'edges' in subscriptions_data:
                        for edge in subscriptions_data['edges']:
                            subscriptions.append(Subscription(**edge['node']))

                    # Update pagination info
                    page_info = subscriptions_data.get('pageInfo', {})
                    has_next_page = page_info.get('hasNextPage', False)
                    cursor = page_info.get('endCursor')

                    # Add subscriptions to our collection
                    all_subscriptions.extend(subscriptions)

                    # Break if no more subscriptions
                    if not subscriptions or not has_next_page:
                        has_next_page = False
                        break

            # Small delay to be respectful of API rate limits
            await asyncio.sleep(0.25)

        return all_subscriptions

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
