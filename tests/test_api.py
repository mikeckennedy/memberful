"""Tests for the Memberful API client."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from memberful.api import (
    MEMBER_FIELDS_FRAGMENT,
    PLAN_FIELDS_FRAGMENT,
    SUBSCRIPTION_FIELDS_FRAGMENT,
    MemberfulClient,
)
from memberful.api.models import Member, MembersResponse, SubscriptionsResponse
from tests.graphql_contract import build_fake_node, parse_selected_fields

_ALL_FRAGMENTS = PLAN_FIELDS_FRAGMENT + MEMBER_FIELDS_FRAGMENT + SUBSCRIPTION_FIELDS_FRAGMENT


class _FakeHttpResponse:
    """Stands in for httpx2's Response: just enough of the interface _graphql_request uses."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def _fake_member_node(**overrides: Any) -> dict[str, Any]:
    selection = parse_selected_fields(MEMBER_FIELDS_FRAGMENT)
    return build_fake_node(selection, overrides=overrides)


def _fake_subscription_node(**overrides: Any) -> dict[str, Any]:
    selection = parse_selected_fields(_ALL_FRAGMENTS, target_fragment='SubscriptionFields')
    return build_fake_node(selection, overrides=overrides)


def _page_info(has_next: bool, end_cursor: str) -> dict[str, Any]:
    return {
        'hasNextPage': has_next,
        'hasPreviousPage': False,
        'startCursor': end_cursor,
        'endCursor': end_cursor,
    }


class TestMemberfulClientLifecycle:
    """The plumbing around the underlying httpx2 client: construction, the async context
    manager, and close()."""

    def test_client_initialization(self):
        client = MemberfulClient(api_key='test_key')
        assert client is not None
        assert client.config.api_key == 'test_key'
        assert client.config.base_url == 'https://youraccount.memberful.com'
        assert client._client is None

    @pytest.mark.asyncio
    async def test_context_manager_opens_and_closes_the_http_client(self):
        async with MemberfulClient(api_key='test_key') as client:
            assert client._client is not None
        assert client._client is None

    @pytest.mark.asyncio
    async def test_ensure_client_is_idempotent(self):
        client = MemberfulClient(api_key='test_key')
        first = await client._ensure_client()
        second = await client._ensure_client()
        assert first is second
        await client.close()

    @pytest.mark.asyncio
    async def test_close_is_safe_to_call_twice(self):
        client = MemberfulClient(api_key='test_key')
        await client._ensure_client()
        await client.close()
        await client.close()
        assert client._client is None


class TestGraphqlRequest:
    """_graphql_request and _request talk to the (here, faked) httpx2 client directly."""

    @pytest.mark.asyncio
    async def test_graphql_request_returns_data_on_success(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        http_client = await client._ensure_client()
        monkeypatch.setattr(http_client, 'post', AsyncMock(return_value=_FakeHttpResponse({'data': {'ok': True}})))

        result = await client._graphql_request('query { ok }')

        assert result == {'ok': True}
        await client.close()

    @pytest.mark.asyncio
    async def test_graphql_request_raises_on_graphql_errors(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        http_client = await client._ensure_client()
        monkeypatch.setattr(
            http_client, 'post', AsyncMock(return_value=_FakeHttpResponse({'errors': [{'message': 'boom'}]}))
        )

        with pytest.raises(ValueError, match='GraphQL errors: boom'):
            await client._graphql_request('query { ok }')

        await client.close()

    @pytest.mark.asyncio
    async def test_graphql_request_sends_variables_when_given(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        http_client = await client._ensure_client()
        post = AsyncMock(return_value=_FakeHttpResponse({'data': {}}))
        monkeypatch.setattr(http_client, 'post', post)

        await client._graphql_request('query { ok }', {'first': 10})

        post.assert_awaited_once()
        _, kwargs = post.call_args
        assert kwargs['json']['variables'] == {'first': 10}
        await client.close()

    @pytest.mark.asyncio
    async def test_request_delegates_to_the_http_client(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        http_client = await client._ensure_client()
        request = AsyncMock(return_value=_FakeHttpResponse({}))
        monkeypatch.setattr(http_client, 'request', request)

        response = await client._request('GET', '/ping')

        assert response is not None
        request.assert_awaited_once()
        await client.close()


class TestGetMembers:
    @pytest.mark.asyncio
    async def test_returns_members_with_a_priced_plan_and_pagination_metadata(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        node = _fake_member_node()
        node['subscriptions'] = [_fake_subscription_node(price=2999)]
        graphql_request = AsyncMock(
            return_value={
                'members': {
                    'edges': [{'node': node, 'cursor': 'c1'}],
                    'pageInfo': _page_info(False, 'c1'),
                }
            }
        )
        monkeypatch.setattr(client, '_graphql_request', graphql_request)

        response = await client.get_members(page=1, per_page=10)

        assert isinstance(response, MembersResponse)
        assert len(response.members) == 1
        subscriptions = response.members[0].subscriptions
        assert subscriptions is not None
        plan = subscriptions[0].plan
        assert plan is not None
        assert plan.price == 2999
        assert response.current_page == 1
        assert response.per_page == 10


class TestGetAllMembers:
    @pytest.mark.asyncio
    async def test_paginates_across_cursors_and_normalizes_null_subscriptions(self, monkeypatch):
        monkeypatch.setattr('memberful.api.asyncio.sleep', AsyncMock())
        client = MemberfulClient(api_key='test_key')

        node1 = _fake_member_node()
        node1['subscriptions'] = [_fake_subscription_node(price=1)]
        page1 = {'members': {'edges': [{'node': node1, 'cursor': 'c1'}], 'pageInfo': _page_info(True, 'c1')}}

        node2 = _fake_member_node()
        node2['subscriptions'] = None
        page2 = {'members': {'edges': [{'node': node2, 'cursor': 'c2'}], 'pageInfo': _page_info(False, 'c2')}}

        graphql_request = AsyncMock(side_effect=[page1, page2])
        monkeypatch.setattr(client, '_graphql_request', graphql_request)

        members = await client.get_all_members()

        assert len(members) == 2
        assert graphql_request.call_count == 2
        assert graphql_request.call_args_list[0].args[1] == {'first': 100, 'after': None}
        assert graphql_request.call_args_list[1].args[1] == {'first': 100, 'after': 'c1'}
        assert members[1].subscriptions == []


class TestGetMember:
    @pytest.mark.asyncio
    async def test_returns_the_member(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        node = _fake_member_node()
        monkeypatch.setattr(client, '_graphql_request', AsyncMock(return_value={'member': node}))

        member = await client.get_member(6651517)

        assert isinstance(member, Member)
        assert member.id == node['id']
        assert member.discord_user_id is not None

    @pytest.mark.asyncio
    async def test_raises_when_the_member_is_not_found(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        monkeypatch.setattr(client, '_graphql_request', AsyncMock(return_value={'member': None}))

        with pytest.raises(ValueError, match='not found'):
            await client.get_member(999)


class TestGetSubscriptions:
    @pytest.mark.asyncio
    async def test_all_subscriptions_branch(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        node = _fake_subscription_node(price=1999)
        graphql_request = AsyncMock(
            return_value={
                'subscriptions': {'edges': [{'node': node, 'cursor': 'c1'}], 'pageInfo': _page_info(False, 'c1')}
            }
        )
        monkeypatch.setattr(client, '_graphql_request', graphql_request)

        response = await client.get_subscriptions()

        assert isinstance(response, SubscriptionsResponse)
        assert len(response.subscriptions) == 1
        query = graphql_request.call_args.args[0]
        assert 'GetAllSubscriptions' in query

    @pytest.mark.asyncio
    async def test_member_scoped_branch(self, monkeypatch):
        client = MemberfulClient(api_key='test_key')
        node = _fake_subscription_node(price=1999)
        graphql_request = AsyncMock(
            return_value={
                'member': {
                    'subscriptions': {'edges': [{'node': node, 'cursor': 'c1'}], 'pageInfo': _page_info(False, 'c1')}
                }
            }
        )
        monkeypatch.setattr(client, '_graphql_request', graphql_request)

        response = await client.get_subscriptions(member_id=6651517)

        assert len(response.subscriptions) == 1
        query, variables = graphql_request.call_args.args
        assert 'GetMemberSubscriptions' in query
        assert variables['memberId'] == '6651517'


class TestGetAllSubscriptions:
    @pytest.mark.asyncio
    async def test_all_subscriptions_paginates_across_cursors(self, monkeypatch):
        monkeypatch.setattr('memberful.api.asyncio.sleep', AsyncMock())
        client = MemberfulClient(api_key='test_key')
        page1 = {
            'subscriptions': {
                'edges': [{'node': _fake_subscription_node(price=1), 'cursor': 'c1'}],
                'pageInfo': _page_info(True, 'c1'),
            }
        }
        page2 = {
            'subscriptions': {
                'edges': [{'node': _fake_subscription_node(price=2), 'cursor': 'c2'}],
                'pageInfo': _page_info(False, 'c2'),
            }
        }
        monkeypatch.setattr(client, '_graphql_request', AsyncMock(side_effect=[page1, page2]))

        subscriptions = await client.get_all_subscriptions()

        assert len(subscriptions) == 2
        first_plan = subscriptions[0].plan
        second_plan = subscriptions[1].plan
        assert first_plan is not None and first_plan.price == 1
        assert second_plan is not None and second_plan.price == 2

    @pytest.mark.asyncio
    async def test_member_scoped_paginates_and_uses_the_member_query(self, monkeypatch):
        monkeypatch.setattr('memberful.api.asyncio.sleep', AsyncMock())
        client = MemberfulClient(api_key='test_key')
        page = {
            'member': {
                'subscriptions': {
                    'edges': [{'node': _fake_subscription_node(price=1), 'cursor': 'c1'}],
                    'pageInfo': _page_info(False, 'c1'),
                }
            }
        }
        graphql_request = AsyncMock(return_value=page)
        monkeypatch.setattr(client, '_graphql_request', graphql_request)

        subscriptions = await client.get_all_subscriptions(member_id=123)

        assert len(subscriptions) == 1
        query = graphql_request.call_args.args[0]
        assert 'GetMemberSubscriptions' in query

    @pytest.mark.asyncio
    async def test_stops_when_a_page_comes_back_empty(self, monkeypatch):
        """hasNextPage=True but zero edges must still terminate the loop, not spin forever."""
        monkeypatch.setattr('memberful.api.asyncio.sleep', AsyncMock())
        client = MemberfulClient(api_key='test_key')
        empty_page = {'subscriptions': {'edges': [], 'pageInfo': _page_info(True, 'c1')}}
        monkeypatch.setattr(client, '_graphql_request', AsyncMock(return_value=empty_page))

        subscriptions = await client.get_all_subscriptions()

        assert subscriptions == []
