"""Tests for MemberfulClient's write operations, driven through a mocked HTTP transport."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx2 as httpx
import pytest
import stamina

from memberful.api import (
    MEMBER_FIELDS_FRAGMENT,
    PLAN_FIELDS_FRAGMENT,
    SUBSCRIPTION_FIELDS_FRAGMENT,
    MemberfulClient,
    MemberfulError,
    MemberfulGraphQLError,
    Subscription,
)
from tests.graphql_contract import build_fake_node, parse_selected_fields

_ALL_FRAGMENTS = PLAN_FIELDS_FRAGMENT + MEMBER_FIELDS_FRAGMENT + SUBSCRIPTION_FIELDS_FRAGMENT


def _fake_subscription_node(**overrides: Any) -> dict[str, Any]:
    selection = parse_selected_fields(_ALL_FRAGMENTS, target_fragment='SubscriptionFields')
    # Plan.price is an int, which the generic fake scalar isn't
    return build_fake_node(selection, overrides={'price': 2999, **overrides})


class RecordingTransport:
    """Answers every request with the same response and records what was sent."""

    def __init__(self, status_code: int = 200, body: Any = None) -> None:
        self.status_code = status_code
        self.body = body
        self.requests: list[dict[str, Any]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(json.loads(request.content))
        return httpx.Response(self.status_code, json=self.body)


def _client_for(transport: RecordingTransport) -> MemberfulClient:
    client = MemberfulClient(api_key='test_key', base_url='https://test.memberful.com')
    client._client = httpx.AsyncClient(base_url='https://test.memberful.com', transport=httpx.MockTransport(transport))
    return client


@pytest.fixture(autouse=True)
def _fast_retries() -> Iterator[None]:
    with stamina.set_testing(True, attempts=3):
        yield


class TestSetSubscriptionAutorenew:
    @pytest.mark.asyncio
    async def test_sends_the_mutation_with_string_id_and_autorenew_false(self):
        node = _fake_subscription_node(id=42, autorenew=False)
        transport = RecordingTransport(body={'data': {'subscriptionSetAutoRenew': {'subscription': node}}})

        async with _client_for(transport) as client:
            await client.set_subscription_autorenew(42, False)

        assert len(transport.requests) == 1
        sent = transport.requests[0]
        assert 'mutation SetSubscriptionAutorenew($id: ID!, $autorenew: Boolean!)' in sent['query']
        assert 'subscriptionSetAutoRenew(id: $id, autorenew: $autorenew)' in sent['query']
        assert '...SubscriptionFields' in sent['query']
        assert sent['variables'] == {'id': '42', 'autorenew': False}

    @pytest.mark.asyncio
    async def test_returns_the_subscription_memberful_reports(self):
        node = _fake_subscription_node(id=42, active=True, autorenew=False)
        transport = RecordingTransport(body={'data': {'subscriptionSetAutoRenew': {'subscription': node}}})

        async with _client_for(transport) as client:
            subscription = await client.set_subscription_autorenew(42, False)

        assert isinstance(subscription, Subscription)
        assert subscription.id == 42
        assert subscription.autorenew is False
        assert subscription.active is True

    @pytest.mark.asyncio
    async def test_returns_memberful_value_not_the_argument(self):
        # If Memberful didn't apply the change, the caller must see that rather than an echo of `autorenew`.
        node = _fake_subscription_node(id=42, autorenew=True)
        transport = RecordingTransport(body={'data': {'subscriptionSetAutoRenew': {'subscription': node}}})

        async with _client_for(transport) as client:
            subscription = await client.set_subscription_autorenew(42, False)

        assert subscription.autorenew is True

    @pytest.mark.asyncio
    async def test_graphql_errors_raise_a_typed_error_that_is_still_a_value_error(self):
        errors = [{'message': 'You do not have permission to perform this action'}]
        transport = RecordingTransport(body={'errors': errors, 'data': {'subscriptionSetAutoRenew': None}})

        async with _client_for(transport) as client:
            with pytest.raises(MemberfulGraphQLError, match='permission') as exc_info:
                await client.set_subscription_autorenew(42, False)

        assert isinstance(exc_info.value, ValueError)
        assert exc_info.value.errors == errors
        assert exc_info.value.messages == ['You do not have permission to perform this action']

    @pytest.mark.parametrize('status_code', [401, 403])
    @pytest.mark.asyncio
    async def test_http_auth_errors_raise(self, status_code: int):
        transport = RecordingTransport(status_code=status_code, body={'error': 'nope'})

        async with _client_for(transport) as client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.set_subscription_autorenew(42, False)

        assert exc_info.value.response.status_code == status_code

    @pytest.mark.asyncio
    async def test_retries_before_giving_up(self):
        transport = RecordingTransport(status_code=503, body={})

        async with _client_for(transport) as client:
            with pytest.raises(httpx.HTTPStatusError):
                await client.set_subscription_autorenew(42, False)

        assert len(transport.requests) == 3

    @pytest.mark.asyncio
    async def test_timeouts_raise(self):
        def time_out(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout('timed out', request=request)

        client = MemberfulClient(api_key='test_key', base_url='https://test.memberful.com')
        client._client = httpx.AsyncClient(
            base_url='https://test.memberful.com', transport=httpx.MockTransport(time_out)
        )

        async with client:
            with pytest.raises(httpx.TimeoutException):
                await client.set_subscription_autorenew(42, False)

    @pytest.mark.parametrize(
        'body',
        [
            {'data': {'subscriptionSetAutoRenew': {'subscription': None}}},
            {'data': {'subscriptionSetAutoRenew': None}},
            {'data': {}},
            {'data': None},
            {},
        ],
        ids=['null-subscription', 'null-payload', 'missing-payload', 'null-data', 'empty-body'],
    )
    @pytest.mark.asyncio
    async def test_missing_subscription_raises_instead_of_returning_an_empty_model(self, body: dict[str, Any]):
        transport = RecordingTransport(body=body)

        async with _client_for(transport) as client:
            with pytest.raises(MemberfulError, match='unconfirmed'):
                await client.set_subscription_autorenew(42, False)
