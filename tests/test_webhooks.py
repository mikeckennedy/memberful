"""Tests for webhook handling functionality."""

from typing import Any

from memberful.webhooks import (
    MemberDeletedEvent,
    MemberSignupEvent,
    OrderCompletedEvent,
    SubscriptionActivatedEvent,
    SubscriptionDeletedEvent,
    SubscriptionRenewedEvent,
    parse_payload,
    validate_signature,
)


class TestWebhookFunctions:
    """Test cases for webhook functions."""

    def test_parse_webhook_payload_member_signup(self):
        """Test parsing a member signup webhook payload."""
        payload = {
            'event': 'member_signup',
            'member': {
                'id': 12345,
                'email': 'test@example.com',
                'full_name': 'Test User',
                'created_at': 1640995200,  # Unix timestamp for Jan 1, 2022
            },
        }

        event = parse_payload(payload)
        assert isinstance(event, MemberSignupEvent)
        assert event.member.id == 12345
        assert event.member.email == 'test@example.com'

    def test_parse_webhook_payload_unsupported_event(self):
        """Test that unsupported event types raise ValueError."""
        payload: dict[str, Any] = {'event': 'unsupported_event', 'data': {}}

        try:
            parse_payload(payload)
            assert False, 'Should have raised ValueError'
        except ValueError as e:
            assert 'Unsupported event type' in str(e)

    def test_validate_webhook_signature_valid(self):
        """Test webhook signature validation with valid signature."""
        payload = '{"event":"member_signup","member":{"id":123}}'
        secret_key = 'test_secret'

        # Generate expected signature
        import hashlib
        import hmac

        expected_sig = hmac.new(secret_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()

        # Test without sha256= prefix
        assert validate_signature(payload, expected_sig, secret_key) is True

        # Test with sha256= prefix
        assert validate_signature(payload, f'sha256={expected_sig}', secret_key) is True

    def test_validate_webhook_signature_invalid(self):
        """Test webhook signature validation with invalid signature."""
        payload = '{"event":"member_signup"}'
        secret_key = 'test_secret'
        invalid_signature = 'invalid_signature'

        assert validate_signature(payload, invalid_signature, secret_key) is False

    def test_parse_webhook_payload_member_deleted(self):
        """Test parsing a member deleted webhook payload."""
        payload = {
            'event': 'member.deleted',
            'member': {
                'id': 12345,
                'deleted': True,
            },
            'products': [],
            'subscriptions': [],
        }

        event = parse_payload(payload)
        assert isinstance(event, MemberDeletedEvent)
        assert event.member.id == 12345
        assert event.member.deleted is True

    def test_parse_webhook_payload_subscription_activated(self):
        """Test parsing a subscription activated webhook payload."""
        payload = {
            'event': 'subscription.activated',
            'subscription': {
                'active': True,
                'autorenew': True,
                'created_at': '2022-01-01T00:00:00Z',
                'expires_at': '2022-12-31T23:59:59Z',
                'id': 1,
                'member': {
                    'id': 12345,
                    'email': 'test@example.com',
                    'created_at': 1640995200,
                },
                'subscription_plan': {
                    'id': 1,
                    'name': 'Premium Plan',
                    'slug': 'premium',
                    'interval_count': 1,
                    'interval_unit': 'month',
                    'price_cents': 99900,
                },
                'trial_end_at': None,
                'trial_start_at': None,
            },
        }

        event = parse_payload(payload)
        assert isinstance(event, SubscriptionActivatedEvent)
        assert event.subscription.active is True
        assert event.subscription.member.id == 12345
        assert event.subscription.subscription_plan.name == 'Premium Plan'

    def test_parse_webhook_payload_subscription_deleted(self):
        """Test parsing a subscription deleted webhook payload."""
        payload = {
            'event': 'subscription.deleted',
            'subscription': {
                'active': True,
                'autorenew': True,
                'created_at': '2022-01-01T00:00:00Z',
                'expires_at': '2022-12-31T23:59:59Z',
                'id': 1,
                'member': {
                    'id': 12345,
                    'email': 'test@example.com',
                    'created_at': 1640995200,
                },
                'subscription_plan': {
                    'id': 1,
                    'name': 'Premium Plan',
                    'slug': 'premium',
                    'interval_count': 1,
                    'interval_unit': 'month',
                    'price_cents': 99900,
                },
                'trial_end_at': None,
                'trial_start_at': None,
            },
        }

        event = parse_payload(payload)
        assert isinstance(event, SubscriptionDeletedEvent)
        assert event.subscription.member.id == 12345
        assert event.subscription.subscription_plan.name == 'Premium Plan'

    def test_parse_webhook_payload_subscription_renewed(self):
        """Test parsing a subscription renewed webhook payload."""
        payload = {
            'event': 'subscription.renewed',
            'subscription': {
                'active': True,
                'autorenew': True,
                'created_at': '2022-01-01T00:00:00Z',
                'expires_at': '2023-01-01T00:00:00Z',  # Renewed expiration date
                'id': 1,
                'member': {
                    'id': 12345,
                    'email': 'test@example.com',
                    'created_at': 1640995200,
                },
                'subscription_plan': {
                    'id': 1,
                    'name': 'Premium Plan',
                    'slug': 'premium',
                    'interval_count': 1,
                    'interval_unit': 'month',
                    'price_cents': 99900,
                },
                'trial_end_at': None,
                'trial_start_at': None,
            },
            'order': {
                'created_at': '2022-01-01T00:00:00Z',
                'status': 'completed',
                'total': 9900,
                'uuid': '4DACB7B0-B728-0130-F9E8-102B343DC979',
            },
        }

        event = parse_payload(payload)
        assert isinstance(event, SubscriptionRenewedEvent)
        assert event.subscription.member.id == 12345
        assert event.subscription.subscription_plan.name == 'Premium Plan'
        assert event.order.uuid == '4DACB7B0-B728-0130-F9E8-102B343DC979'

    def test_parse_webhook_payload_order_completed_minimal_subscription_data(self):
        """Test parsing an order completed webhook with minimal subscription data."""
        # This test replicates the real-world scenario where subscription plan
        # data may be missing price and renewal_period fields
        payload = {
            'event': 'order.completed',
            'order': {
                'uuid': '4DACB7B0-B728-0130-F9E8-102B343DC979',
                'number': '4DACB7B0',
                'total': 9900,
                'status': 'completed',
                'receipt': 'receipt text',
                'member': {
                    'id': 12345,
                    'email': 'test@example.com',
                    'created_at': 1640995200,
                },
                'products': [],
                'subscriptions': [
                    {
                        'active': True,
                        'created_at': 1640995200,
                        'expires': True,
                        'expires_at': 1672531200,
                        'id': 67890,
                        'subscription': {
                            'id': 0,
                            'name': 'Sample plan',
                            'slug': '0-sample-plan',
                            'type': 'standard_plan',
                            # Note: price and renewal_period are missing as in the real error
                        },
                    }
                ],
            },
        }

        event = parse_payload(payload)
        assert isinstance(event, OrderCompletedEvent)
        assert event.order.uuid == '4DACB7B0-B728-0130-F9E8-102B343DC979'
        assert event.order.member.id == 12345
        assert len(event.order.subscriptions) == 1

        # Test that the subscription plan handles missing optional fields
        subscription_plan = event.order.subscriptions[0].subscription
        assert subscription_plan.id == 0
        assert subscription_plan.name == 'Sample plan'
        assert subscription_plan.type == 'standard_plan'
        assert subscription_plan.price is None  # Missing field handled gracefully
        assert subscription_plan.renewal_period is None  # Missing field handled gracefully
