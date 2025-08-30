"""Basic usage examples for the memberful package."""

import json

from memberful import (
    MemberfulClient,
    MemberSignupEvent,
    SubscriptionCreatedEvent,
    parse_webhook_payload,
    validate_webhook_signature,
)


async def main():
    """Example usage of the Memberful client."""
    # Initialize the client with your API key
    api_key = 'your_memberful_api_key_here'

    async with MemberfulClient(api_key=api_key) as client:
        # Get list of members
        members = await client.get_members(page=1, per_page=10)
        print(f'Found {len(members.get("members", []))} members')

        # Get a specific member (replace with actual member ID)
        # member = await client.get_member(member_id=12345)
        # print(f"Member: {member}")

        # Get subscriptions
        subscriptions = await client.get_subscriptions(page=1, per_page=10)
        print(f'Found {len(subscriptions.get("subscriptions", []))} subscriptions')


def handle_member_signup(event: MemberSignupEvent):
    """Handle new member signup events."""
    print(f'New member signed up: {event.member.email}')
    # Add your custom logic here


def handle_subscription_created(event: SubscriptionCreatedEvent):
    """Handle subscription created events."""
    print(f'New subscription created for member: {event.subscription.member_id}')
    # Add your custom logic here


def webhook_example():
    """Example webhook handling setup using the functional approach."""
    # In your web framework (Flask, FastAPI, etc.), process webhooks like this:

    def process_webhook(payload: str, signature: str, secret_key: str):
        """Process an incoming webhook payload."""
        # 1. Validate the signature
        if not validate_webhook_signature(payload, signature, secret_key):
            raise ValueError('Invalid webhook signature')

        # 2. Parse the payload into a strongly-typed event
        event_data = json.loads(payload)
        webhook_event = parse_webhook_payload(event_data)

        # 3. Route to appropriate handler using match statement
        match webhook_event:
            case MemberSignupEvent():
                handle_member_signup(webhook_event)
            case SubscriptionCreatedEvent():
                handle_subscription_created(webhook_event)
            case _:
                print(f'Unhandled event type: {webhook_event.event}')

        return webhook_event

    # Example usage:
    # payload = request.get_data(as_text=True)
    # signature = request.headers.get('X-Memberful-Webhook-Signature')
    # event = process_webhook(payload, signature, 'your_webhook_secret_key')
    # print(f"Processed webhook event: {event.event}")

    print('Webhook processing example setup complete!')


if __name__ == '__main__':
    print('Running Memberful client examples...')

    # Run the async client example
    # asyncio.run(main())

    # Show webhook handler setup
    webhook_example()

    print('Examples completed!')
