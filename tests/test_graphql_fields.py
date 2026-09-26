"""Contract tests: does the field selection each query actually sends match what
memberful.api.models requires and permits?

Why this file exists: `MemberfulClient`'s queries used to select `plan { id name intervalUnit
intervalCount slug }` for every subscription's plan - no `price`. `Plan.price` is a required
field with no default, so *any* member with a subscription that has a plan raised a
`pydantic.ValidationError` the moment the client tried to parse the response. `autorenew`,
`discordUserId`, `createdAt`/`activatedAt` and other optional-but-wanted fields were similarly
missing from the selection and silently stayed `None` forever.

These tests parse the actual, shared GraphQL fragments (`memberful.api.PLAN_FIELDS_FRAGMENT`,
`MEMBER_FIELDS_FRAGMENT`, `SUBSCRIPTION_FIELDS_FRAGMENT` - the same strings the client sends over
the wire) rather than a hand-maintained list of field names, build a fake response node with
exactly those keys, and feed it to the matching pydantic model. If a required field is ever
dropped from a fragment again, or a needed alias (like `price: priceCents`) is removed, the
fragment and the model drift apart and one of these tests fails immediately - instead of only
showing up as a crash against real subscriber data in production.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from memberful.api import (
    MEMBER_FIELDS_FRAGMENT,
    PLAN_FIELDS_FRAGMENT,
    SUBSCRIPTION_FIELDS_FRAGMENT,
)
from memberful.api.models import Member, Plan, Subscription
from tests.graphql_contract import build_fake_node, parse_selected_fields

_ALL_FRAGMENTS = PLAN_FIELDS_FRAGMENT + MEMBER_FIELDS_FRAGMENT + SUBSCRIPTION_FIELDS_FRAGMENT


class TestPlanFieldsFragment:
    """PLAN_FIELDS_FRAGMENT is used inside SUBSCRIPTION_FIELDS_FRAGMENT for every query that
    returns subscriptions (get_members, get_all_members, get_member, get_subscriptions,
    get_all_subscriptions)."""

    def test_satisfies_required_and_selected_optional_plan_fields(self):
        selection = parse_selected_fields(PLAN_FIELDS_FRAGMENT)
        node = build_fake_node(selection, overrides={'price': 2999, 'name': 'Premium'})

        plan = Plan(**node)

        # Required fields - would raise ValidationError if missing from the selection.
        assert plan.id is not None
        assert plan.name == 'Premium'
        # This is the field whose absence was the original production bug: Memberful's schema has
        # no `price` field at all, only `priceCents`, so the fragment aliases it as `price:
        # priceCents`. If that alias were ever removed, `price` would be missing from `node` and
        # this `Plan(**node)` call would raise ValidationError instead of asserting 2999 here.
        assert plan.price == 2999
        # Selected optional fields that should now actually populate.
        assert plan.slug is not None
        assert plan.interval_unit is not None
        assert plan.interval_count is not None
        assert plan.for_sale is not None

    def test_price_is_required_and_a_selection_without_it_fails_fast(self):
        """Regression guard for the original bug shape, independent of the fragment parsing
        plumbing above: Plan.price has no default, so constructing one without it must fail.

        Built from a plain dict (not keyword arguments) so the missing `price` is only caught at
        runtime by pydantic - exactly how a real, under-selected GraphQL response would arrive.
        """
        node_missing_price: dict[str, Any] = {'id': 1, 'name': 'Premium', 'slug': 'premium'}

        with pytest.raises(ValidationError):
            Plan(**node_missing_price)


class TestMemberFieldsFragment:
    """MEMBER_FIELDS_FRAGMENT is used for get_members, get_all_members and get_member. It
    intentionally does not select `subscriptions` itself (that's added at the query call site to
    avoid the fragment recursing into itself through Subscription.member); see
    test_member_query_attaches_subscriptions_from_subscription_fields_fragment below."""

    def test_satisfies_required_and_selected_optional_member_fields(self):
        selection = parse_selected_fields(MEMBER_FIELDS_FRAGMENT)
        node = build_fake_node(selection)

        member = Member(**node)

        assert member.id is not None
        assert member.email
        # Previously missing from every query: discordUserId (explicitly needed by consumers) and
        # phoneNumber.
        assert member.discord_user_id is not None
        assert member.phone_number is not None
        assert member.full_name is not None
        assert member.username is not None
        assert member.stripe_customer_id is not None
        assert member.unrestricted_access is not None
        assert member.address is not None
        assert member.address.city is not None

    def test_member_query_attaches_subscriptions_from_subscription_fields_fragment(self):
        """Mirrors what _GET_MEMBER_QUERY / _GET_MEMBERS_QUERY actually send: ...MemberFields plus
        a sibling `subscriptions { ...SubscriptionFields }` selection."""
        member_selection = parse_selected_fields(MEMBER_FIELDS_FRAGMENT)
        subscription_selection = parse_selected_fields(_ALL_FRAGMENTS, target_fragment='SubscriptionFields')

        node = build_fake_node(member_selection)
        node['subscriptions'] = [build_fake_node(subscription_selection, overrides={'price': 4999})]

        member = Member(**node)

        assert member.subscriptions is not None
        assert len(member.subscriptions) == 1
        subscription = member.subscriptions[0]
        assert subscription.plan is not None
        assert subscription.plan.price == 4999


class TestSubscriptionFieldsFragment:
    """SUBSCRIPTION_FIELDS_FRAGMENT is used for get_members/get_all_members/get_member (nested
    under a member) and get_subscriptions/get_all_subscriptions (as the top-level node)."""

    def test_satisfies_required_and_selected_optional_subscription_fields_with_priced_plan(self):
        selection = parse_selected_fields(_ALL_FRAGMENTS, target_fragment='SubscriptionFields')
        node = build_fake_node(selection, overrides={'price': 2999, 'active': True, 'autorenew': True})

        subscription = Subscription(**node)

        # Required.
        assert subscription.id is not None
        assert subscription.active is True
        # Previously always None because the query never selected them.
        assert subscription.autorenew is True
        assert subscription.created_at is not None
        assert subscription.expires_at is not None
        assert subscription.activated_at is not None
        assert subscription.trial_end_at is not None
        assert subscription.trial_start_at is not None
        # Nested plan - this is the exact shape that used to crash: a subscription with a plan
        # that has a price.
        assert subscription.plan is not None
        assert subscription.plan.price == 2999
        assert subscription.plan.name is not None
        # Nested member - newly selected so get_subscriptions()/get_all_subscriptions() results
        # carry who the subscription belongs to.
        assert subscription.member is not None
        assert subscription.member.discord_user_id is not None
