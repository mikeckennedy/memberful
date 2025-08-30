#!/usr/bin/env python3
"""Test script to send sample webhook payloads to the FastAPI webhook handler.

This script demonstrates how to send different webhook event types to
the FastAPI app running locally. It's useful for testing and development.
"""

import asyncio
import json

import httpx

# Sample webhook payloads for testing
SAMPLE_PAYLOADS = {
    'member_signup': {
        'event': 'member_signup',
        'member': {
            'id': 12345,
            'email': 'jane.doe@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'created_at': 1640995200,
            'signup_method': 'checkout',
            'tracking_params': {'utm_source': 'twitter', 'utm_campaign': 'winter_sale'},
            'unrestricted_access': False,
        },
    },
    'subscription_created': {
        'event': 'subscription.created',
        'member': {
            'id': 12345,
            'email': 'customer@example.com',
            'first_name': 'Jane',
            'created_at': 1640995200,
            'unrestricted_access': False,
        },
        'subscriptions': [
            {
                'id': 67890,
                'active': True,
                'created_at': 1640995200,
                'expires': True,
                'expires_at': 1672531200,
                'in_trial_period': False,
                'subscription': {
                    'id': 42,
                    'name': 'Premium Plan',
                    'price': 2999,
                    'slug': 'premium',
                    'renewal_period': 'monthly',
                    'interval_unit': 'month',
                    'interval_count': 1,
                    'for_sale': True,
                },
            }
        ],
        'products': [],
    },
    'order_completed': {
        'event': 'order.completed',
        'order': {
            'uuid': 'order-uuid-123',
            'number': 'ORD-2024-001',
            'total': 4999,
            'status': 'completed',
            'receipt': 'receipt-url-here',
            'created_at': 1640995200,
            'member': {
                'id': 12345,
                'email': 'customer@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'created_at': 1640995200,
                'unrestricted_access': False,
            },
            'products': [
                {
                    'id': 101,
                    'name': 'Advanced Course',
                    'price': 4999,
                    'slug': 'advanced-course',
                    'for_sale': True,
                }
            ],
            'subscriptions': [],
        },
    },
    'subscription_plan_created': {
        'event': 'subscription_plan.created',
        'subscription': {
            'id': 42,
            'price': 2999,
            'name': 'Premium Plan',
            'slug': 'premium-plan',
            'renewal_period': 'monthly',
            'interval_unit': 'month',
            'interval_count': 1,
            'for_sale': True,
        },
    },
    'download_created': {
        'event': 'download.created',
        'product': {
            'id': 201,
            'name': 'Ebook: Python Mastery',
            'price': 1999,
            'slug': 'python-mastery-ebook',
            'for_sale': True,
        },
    },
}


async def send_webhook(webhook_url: str, payload: dict, event_name: str) -> tuple[bool, dict]:
    """Send a webhook payload to the FastAPI server.

    Args:
        webhook_url: URL of the webhook endpoint
        payload: The webhook payload to send
        event_name: Name of the event for logging

    Returns:
        Tuple of (success, response_data)
    """
    print(f'🚀 Sending {event_name} webhook...')

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10.0,
            )

            if response.status_code == 200:
                result = response.json()
                print(f'✅ {event_name}: {result["message"]}')
                return True, result
            else:
                print(f'❌ {event_name}: HTTP {response.status_code}')
                print(f'   Error: {response.text}')
                return False, {}

    except httpx.RequestError as e:
        print(f'❌ {event_name}: Request failed - {e}')
        return False, {}
    except Exception as e:
        print(f'❌ {event_name}: Unexpected error - {e}')
        return False, {}


async def test_all_webhooks(base_url: str = 'http://localhost:8000'):
    """Test all webhook event types.

    Args:
        base_url: Base URL of the FastAPI server
    """
    webhook_url = f'{base_url}/webhook'

    print('🔗 Testing Memberful FastAPI Webhook Handler')
    print('=' * 50)
    print(f'Target URL: {webhook_url}')
    print()

    # Test health check first
    try:
        async with httpx.AsyncClient() as client:
            health_response = await client.get(f'{base_url}/health')
            if health_response.status_code == 200:
                print('✅ Server health check passed')
            else:
                print('❌ Server health check failed')
                return
    except httpx.RequestError:
        print('❌ Cannot connect to server. Is it running on localhost:8000?')
        print('   Start the server with: python main.py')
        return

    print()
    print('📡 Testing webhook events...')
    print('-' * 30)

    # Send each webhook type
    success_count = 0
    total_count = len(SAMPLE_PAYLOADS)

    for event_name, payload in SAMPLE_PAYLOADS.items():
        success, _ = await send_webhook(webhook_url, payload, event_name)
        if success:
            success_count += 1

        # Small delay between requests
        await asyncio.sleep(0.5)

    print()
    print('📊 Test Results')
    print('-' * 20)
    print(f'✅ Successful: {success_count}')
    print(f'❌ Failed: {total_count - success_count}')
    print(f'📈 Success rate: {success_count / total_count * 100:.1f}%')

    if success_count == total_count:
        print('\n🎉 All webhook tests passed!')
    else:
        print('\n⚠️  Some webhook tests failed. Check server logs for details.')


async def test_single_webhook(event_name: str, base_url: str = 'http://localhost:8000'):
    """Test a single webhook event type.

    Args:
        event_name: Name of the event to test
        base_url: Base URL of the FastAPI server
    """
    if event_name not in SAMPLE_PAYLOADS:
        print(f'❌ Unknown event type: {event_name}')
        print(f'Available events: {", ".join(SAMPLE_PAYLOADS.keys())}')
        return

    webhook_url = f'{base_url}/webhook'
    payload = SAMPLE_PAYLOADS[event_name]

    print(f'🚀 Testing single webhook: {event_name}')
    print(f'Target URL: {webhook_url}')
    print()

    success, result = await send_webhook(webhook_url, payload, event_name)

    if success:
        print('\n✅ Test completed successfully!')
        print(f'Response: {json.dumps(result, indent=2)}')
    else:
        print('\n❌ Test failed!')


async def main():
    """Main test function."""
    import sys

    if len(sys.argv) > 1:
        # Test specific event type
        event_name = sys.argv[1]
        await test_single_webhook(event_name)
    else:
        # Test all event types
        await test_all_webhooks()


if __name__ == '__main__':
    print('🧪 Memberful Webhook Tester')
    print('==========================')
    print()

    # Show usage information
    import sys

    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print('Usage:')
        print('  python test_webhook.py                    # Test all webhook types')
        print('  python test_webhook.py <event_name>       # Test specific event')
        print()
        print('Available events:')
        for event_name in SAMPLE_PAYLOADS:
            print(f'  - {event_name}')
        print()
        print('Examples:')
        print('  python test_webhook.py member_signup')
        print('  python test_webhook.py subscription_created')
        exit(0)

    asyncio.run(main())
