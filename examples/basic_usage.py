"""Basic usage examples for the memberful package."""

from memberful import MemberfulClient, WebhookEventType, WebhookHandler


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


def webhook_example():
    """Example webhook handling setup."""
    # Initialize webhook handler with your secret key
    webhook_handler = WebhookHandler(secret_key='your_webhook_secret_key')

    # Register event handlers using decorators
    @webhook_handler.on(WebhookEventType.MEMBER_CREATED)
    def handle_new_member(data):
        print(f'New member created: {data.get("email", "Unknown")}')
        # Add your custom logic here

    @webhook_handler.on(WebhookEventType.SUBSCRIPTION_CREATED)
    def handle_new_subscription(data):
        print(f'New subscription created for member: {data.get("member_id", "Unknown")}')
        # Add your custom logic here

    # In your web framework (Flask, FastAPI, etc.), process webhooks like this:
    # payload = request.get_data(as_text=True)
    # signature = request.headers.get('X-Memberful-Webhook-Signature')
    # webhook_payload = webhook_handler.process_webhook(payload, signature)
    # print(f"Processed webhook event: {webhook_payload.event}")


if __name__ == '__main__':
    print('Running Memberful client examples...')

    # Run the async client example
    # asyncio.run(main())

    # Show webhook handler setup
    webhook_example()

    print('Examples completed!')
