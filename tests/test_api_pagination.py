"""Cursor pagination tests for MemberfulClient, run against a fake GraphQL server on httpx2.MockTransport.

The fake server holds three cursor pages and answers each request by its `after` variable, so these
tests exercise the real request path (_graphql_request, retries, response parsing) end to end.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any, Optional
from unittest.mock import AsyncMock

import httpx2 as httpx
import pytest
import stamina

from memberful.api import MEMBER_FIELDS_FRAGMENT, PLAN_FIELDS_FRAGMENT, SUBSCRIPTION_FIELDS_FRAGMENT, MemberfulClient
from tests.graphql_contract import build_fake_node, parse_selected_fields

_ALL_FRAGMENTS = PLAN_FIELDS_FRAGMENT + MEMBER_FIELDS_FRAGMENT + SUBSCRIPTION_FIELDS_FRAGMENT

# after-cursor -> (ids on that page, endCursor, hasNextPage)
_PAGES: dict[Optional[str], tuple[list[int], str, bool]] = {
    None: ([1, 2], 'cursor1', True),
    'cursor1': ([3, 4], 'cursor2', True),
    'cursor2': ([5], 'cursor3', False),
}


def _member_node(member_id: int) -> dict[str, Any]:
    node = build_fake_node(parse_selected_fields(MEMBER_FIELDS_FRAGMENT), overrides={'id': member_id})
    node['subscriptions'] = []
    return node


def _subscription_node(subscription_id: int) -> dict[str, Any]:
    selection = parse_selected_fields(_ALL_FRAGMENTS, target_fragment='SubscriptionFields')
    return build_fake_node(selection, overrides={'id': subscription_id, 'price': 999})


class FakeMemberful:
    """Serves _PAGES for the members, subscriptions and member-scoped subscriptions queries."""

    def __init__(self, fail_first_request_for: Optional[set[Optional[str]]] = None) -> None:
        self.requests: list[dict[str, Any]] = []
        self._fail_first_request_for = set(fail_first_request_for or ())

    def __call__(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        variables: dict[str, Any] = body.get('variables', {})
        self.requests.append(variables)

        after = variables.get('after')
        if after in self._fail_first_request_for:
            self._fail_first_request_for.discard(after)
            return httpx.Response(500, json={'error': 'try again'})

        ids, end_cursor, has_next = _PAGES[after]
        page_info = {'hasNextPage': has_next, 'hasPreviousPage': after is not None, 'startCursor': None}
        page_info['endCursor'] = end_cursor

        query: str = body['query']
        if 'query GetMembers' in query:
            edges = [{'node': _member_node(i), 'cursor': f'm{i}'} for i in ids]
            data: dict[str, Any] = {'members': {'edges': edges, 'pageInfo': page_info}}
        else:
            edges = [{'node': _subscription_node(i), 'cursor': f's{i}'} for i in ids]
            connection = {'edges': edges, 'pageInfo': page_info}
            is_member_scoped = 'query GetMemberSubscriptions' in query
            data = {'member': {'subscriptions': connection}} if is_member_scoped else {'subscriptions': connection}

        return httpx.Response(200, json={'data': data})

    @property
    def cursors_sent(self) -> list[Optional[str]]:
        return [v.get('after') for v in self.requests]


@pytest.fixture(autouse=True)
def _fast_retries_and_no_sleep(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr('memberful.api.asyncio.sleep', AsyncMock())
    with stamina.set_testing(True, attempts=3):
        yield


def _client_for(server: FakeMemberful) -> MemberfulClient:
    client = MemberfulClient(api_key='test_key', base_url='https://test.memberful.com')
    client._client = httpx.AsyncClient(base_url='https://test.memberful.com', transport=httpx.MockTransport(server))
    return client


class TestGetMembersCursors:
    @pytest.mark.asyncio
    async def test_first_page_reports_cursor_and_no_invented_totals(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            response = await client.get_members(per_page=2)

        assert [m.id for m in response.members] == [1, 2]
        assert response.end_cursor == 'cursor1'
        assert response.has_next_page is True
        assert response.total_count is None
        assert response.total_pages is None
        assert response.current_page is None

    @pytest.mark.asyncio
    async def test_after_returns_the_next_page_not_the_first(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            response = await client.get_members(per_page=2, after='cursor1')

        assert [m.id for m in response.members] == [3, 4]
        assert server.cursors_sent == ['cursor1']

    @pytest.mark.asyncio
    async def test_deprecated_page_with_a_cursor_returns_that_page(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            with pytest.warns(DeprecationWarning, match='`page` is deprecated'):
                response = await client.get_members(page=2, per_page=2, after='cursor1')

        assert [m.id for m in response.members] == [3, 4]
        assert response.current_page == 2

    @pytest.mark.asyncio
    async def test_deprecated_page_above_one_without_a_cursor_raises_before_any_request(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            with pytest.warns(DeprecationWarning), pytest.raises(ValueError, match='requires a cursor'):
                await client.get_members(page=2, per_page=2)

        assert server.requests == []

    @pytest.mark.asyncio
    async def test_deprecated_page_one_still_works(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            with pytest.warns(DeprecationWarning):
                response = await client.get_members(page=1, per_page=2)

        assert [m.id for m in response.members] == [1, 2]
        assert response.current_page == 1


class TestIterAndGetAllMembers:
    @pytest.mark.asyncio
    async def test_get_all_members_returns_every_member_in_order_once(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            members = await client.get_all_members()

        assert [m.id for m in members] == [1, 2, 3, 4, 5]
        assert server.cursors_sent == [None, 'cursor1', 'cursor2']

    @pytest.mark.asyncio
    async def test_iter_members_is_lazy(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            pages = client.iter_members(per_page=2)
            assert server.requests == []

            first = await pages.__anext__()
            assert [m.id for m in first.members] == [1, 2]
            assert len(server.requests) == 1

            second = await pages.__anext__()
            assert [m.id for m in second.members] == [3, 4]
            assert len(server.requests) == 2
            await pages.aclose()

    @pytest.mark.asyncio
    async def test_iter_members_resumes_from_a_cursor(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            ids = [m.id async for page in client.iter_members(after='cursor1') for m in page.members]

        assert ids == [3, 4, 5]

    @pytest.mark.asyncio
    async def test_a_retried_request_resends_the_same_cursor(self):
        server = FakeMemberful(fail_first_request_for={'cursor1'})
        async with _client_for(server) as client:
            members = await client.get_all_members()

        assert [m.id for m in members] == [1, 2, 3, 4, 5]
        assert server.cursors_sent == [None, 'cursor1', 'cursor1', 'cursor2']

    @pytest.mark.asyncio
    async def test_pauses_between_pages_but_not_after_the_last(self, monkeypatch: pytest.MonkeyPatch):
        sleep = AsyncMock()
        monkeypatch.setattr('memberful.api.asyncio.sleep', sleep)
        async with _client_for(FakeMemberful()) as client:
            await client.get_all_members()

        assert sleep.await_count == 2
        sleep.assert_awaited_with(0.25)


class TestSubscriptionCursors:
    @pytest.mark.asyncio
    async def test_after_returns_the_next_page(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            response = await client.get_subscriptions(per_page=2, after='cursor1')

        assert [s.id for s in response.subscriptions] == [3, 4]
        assert response.end_cursor == 'cursor2'
        assert response.has_next_page is True
        assert response.total_count is None

    @pytest.mark.asyncio
    async def test_deprecated_page_above_one_without_a_cursor_raises(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            with pytest.warns(DeprecationWarning), pytest.raises(ValueError, match='requires a cursor'):
                await client.get_subscriptions(page=3)

        assert server.requests == []

    @pytest.mark.asyncio
    async def test_get_all_subscriptions_returns_every_subscription_in_order_once(self):
        server = FakeMemberful(fail_first_request_for={'cursor2'})
        async with _client_for(server) as client:
            subscriptions = await client.get_all_subscriptions()

        assert [s.id for s in subscriptions] == [1, 2, 3, 4, 5]
        assert server.cursors_sent == [None, 'cursor1', 'cursor2', 'cursor2']

    @pytest.mark.asyncio
    async def test_member_scoped_iteration_follows_cursors(self):
        server = FakeMemberful()
        async with _client_for(server) as client:
            pages = [page async for page in client.iter_subscriptions(member_id=42, per_page=2)]

        assert [[s.id for s in page.subscriptions] for page in pages] == [[1, 2], [3, 4], [5]]
        assert all(request['memberId'] == '42' for request in server.requests)
        assert server.cursors_sent == [None, 'cursor1', 'cursor2']
