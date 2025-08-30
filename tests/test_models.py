"""Tests for Pydantic models."""

import json

import pytest

from memberful.models import (
    Address,
    CreditCard,
    DownloadCreatedEvent,
    Member,
    MemberSignupEvent,
    Product,
    SubscriptionPlan,
    SubscriptionPlanCreatedEvent,
    SubscriptionUpdatedEvent,
    TrackingParams,
)


class TestMemberModels:
    """Test member-related models."""

    def test_address_model(self):
        """Test Address model with partial data."""
        address_data = {
            'street': '123 Main St',
            'city': 'New York',
            'state': 'NY',
            'postal_code': '10001',
            'country': 'US',
        }
        address = Address(**address_data)
        assert address.street == '123 Main St'
        assert address.city == 'New York'

    def test_address_model_with_nulls(self):
        """Test Address model handles null values."""
        address_data = {
            'street': None,
            'city': 'New York',
            'state': None,
        }
        address = Address(**address_data)
        assert address.street is None
        assert address.city == 'New York'
        assert address.state is None
        assert address.postal_code is None  # Not provided, should default to None

    def test_credit_card_model(self):
        """Test CreditCard model."""
        cc_data = {'exp_month': 12, 'exp_year': 2025}
        cc = CreditCard(**cc_data)
        assert cc.exp_month == 12
        assert cc.exp_year == 2025
        assert cc.last_four is None

    def test_tracking_params_model(self):
        """Test TrackingParams model."""
        tracking_data = {
            'utm_source': 'google',
            'utm_medium': 'cpc',
            'utm_campaign': 'spring_sale',
        }
        tracking = TrackingParams(**tracking_data)
        assert tracking.utm_source == 'google'
        assert tracking.utm_term is None

    def test_member_model_complete(self):
        """Test Member model with complete data."""
        member_data = {
            'id': 123,
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'full_name': 'John Doe',
            'username': 'johndoe',
            'created_at': 1640995200,
            'signup_method': 'checkout',
            'unrestricted_access': False,
            'address': {
                'street': '123 Main St',
                'city': 'New York',
                'state': 'NY',
            },
            'credit_card': {'exp_month': 12, 'exp_year': 2025},
            'tracking_params': {'utm_source': 'google'},
        }
        member = Member(**member_data)
        assert member.id == 123
        assert member.email == 'test@example.com'
        assert member.address.street == '123 Main St'
        assert member.credit_card.exp_month == 12

    def test_member_model_minimal(self):
        """Test Member model with minimal required data."""
        member_data = {'id': 123, 'email': 'test@example.com', 'created_at': 1640995200}
        member = Member(**member_data)
        assert member.id == 123
        assert member.email == 'test@example.com'
        assert member.first_name is None
        assert member.address is None
        assert member.unrestricted_access is False  # Should use default


class TestSubscriptionModels:
    """Test subscription-related models."""

    def test_subscription_plan_model(self):
        """Test SubscriptionPlan model."""
        plan_data = {
            'id': 1,
            'price': 1000,
            'name': 'Monthly Plan',
            'slug': 'monthly-plan',
            'renewal_period': 'monthly',
            'interval_unit': 'month',
            'interval_count': 1,
            'for_sale': True,
        }
        plan = SubscriptionPlan(**plan_data)
        assert plan.id == 1
        assert plan.price == 1000
        assert plan.renewal_period == 'monthly'
        assert plan.for_sale is True

    def test_product_model(self):
        """Test Product model."""
        product_data = {
            'id': 1,
            'name': 'Sample Download',
            'price': 500,
            'slug': 'sample-download',
            'for_sale': True,
        }
        product = Product(**product_data)
        assert product.id == 1
        assert product.name == 'Sample Download'
        assert product.for_sale is True


class TestWebhookEvents:
    """Test webhook event models."""

    def test_member_signup_event(self):
        """Test MemberSignupEvent parsing."""
        event_data = {
            'event': 'member_signup',
            'member': {
                'id': 123,
                'email': 'test@example.com',
                'created_at': 1640995200,
                'first_name': 'John',
                'unrestricted_access': False,
            },
        }
        event = MemberSignupEvent(**event_data)
        assert event.event == 'member_signup'
        assert event.member.id == 123
        assert event.member.email == 'test@example.com'

    def test_subscription_plan_created_event(self):
        """Test SubscriptionPlanCreatedEvent parsing."""
        event_data = {
            'event': 'subscription_plan.created',
            'subscription': {
                'id': 1,
                'price': 1000,
                'name': 'Monthly Plan',
                'slug': 'monthly-plan',
                'renewal_period': 'monthly',
                'interval_unit': 'month',
                'interval_count': 1,
                'for_sale': True,
            },
        }
        event = SubscriptionPlanCreatedEvent(**event_data)
        assert event.event == 'subscription_plan.created'
        assert event.subscription.name == 'Monthly Plan'

    def test_download_created_event(self):
        """Test DownloadCreatedEvent parsing."""
        event_data = {
            'event': 'download.created',
            'product': {
                'id': 1,
                'name': 'Sample Download',
                'price': 500,
                'slug': 'sample-download',
                'for_sale': True,
            },
        }
        event = DownloadCreatedEvent(**event_data)
        assert event.event == 'download.created'
        assert event.product.name == 'Sample Download'

    def test_subscription_updated_with_changes(self):
        """Test SubscriptionUpdatedEvent with changes section."""
        event_data = {
            'event': 'subscription.updated',
            'member': {
                'id': 123,
                'email': 'test@example.com',
                'created_at': 1640995200,
            },
            'products': [],
            'subscriptions': [],
            'changed': {
                'plan_id': [42, 43],
                'expires_at': ['2023-01-01T00:00:00Z', '2023-02-01T00:00:00Z'],
                'autorenew': [False, True],
            },
        }
        event = SubscriptionUpdatedEvent(**event_data)
        assert event.event == 'subscription.updated'
        assert event.changed.plan_id == [42, 43]
        assert event.changed.autorenew == [False, True]

    def test_event_validation_fails_with_wrong_type(self):
        """Test that event validation fails with wrong event type."""
        with pytest.raises(ValueError):
            MemberSignupEvent(event='wrong_event', member={'id': 1, 'email': 'test@example.com', 'created_at': 123})


class TestJsonCompatibility:
    """Test parsing real JSON examples from the documentation."""

    def test_parse_member_signup_json(self):
        """Test parsing the member_signup JSON from documentation."""
        json_data = """
        {
          "event": "member_signup",
          "member": {
            "address": {
              "street": "Street",
              "city": "City",
              "state": "State",
              "postal_code": "Postal code",
              "country": "City"
            },
            "created_at": 1756245496,
            "credit_card": {
              "exp_month": 1,
              "exp_year": 2040
            },
            "custom_field": "Custom field value",
            "discord_user_id": "000000000000000000",
            "email": "john.doe@example.com",
            "first_name": "John",
            "full_name": "John Doe",
            "id": 0,
            "last_name": "Doe",
            "phone_number": "555-12345",
            "signup_method": "checkout",
            "stripe_customer_id": "cus_00000",
            "tracking_params": {
              "utm_term": "shoes",
              "utm_campaign": "summer_sale",
              "utm_medium": "social",
              "utm_source": "instagram",
              "utm_content": "textlink"
            },
            "unrestricted_access": false,
            "username": "john_doe"
          }
        }
        """
        data = json.loads(json_data)
        event = MemberSignupEvent(**data)

        assert event.event == 'member_signup'
        assert event.member.email == 'john.doe@example.com'
        assert event.member.address.street == 'Street'
        assert event.member.tracking_params.utm_source == 'instagram'
        assert event.member.credit_card.exp_year == 2040

    def test_parse_subscription_plan_created_json(self):
        """Test parsing subscription_plan.created JSON from documentation."""
        json_data = """
        {
          "event": "subscription_plan.created",
          "subscription": {
            "id": 0,
            "price": 1000,
            "name": "Sample plan",
            "slug": "0-sample-plan",
            "renewal_period": "monthly",
            "interval_unit": "month",
            "interval_count": 1,
            "for_sale": true
          }
        }
        """
        data = json.loads(json_data)
        event = SubscriptionPlanCreatedEvent(**data)

        assert event.event == 'subscription_plan.created'
        assert event.subscription.name == 'Sample plan'
        assert event.subscription.price == 1000
        assert event.subscription.renewal_period == 'monthly'
