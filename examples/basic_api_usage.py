"""Basic API usage examples for the memberful package."""

import asyncio
import json

from memberful.api import MemberfulClient


async def main():
    """Example usage of the Memberful client."""
    # Initialize the client with your API key and account URL
    settings: dict[str, str] = json.load(open('./settings.json'))
    api_key = settings['api_key']

    # IMPORTANT: Replace 'youraccount' with your actual Memberful account name
    # Your Memberful URL is typically https://youraccount.memberful.com
    base_url = settings.get('base_url', 'https://youraccount.memberful.com')

    async with MemberfulClient(api_key=api_key, base_url=base_url) as client:
        # Get all members (convenience method that handles pagination automatically)
        all_members = await client.get_all_members()
        print(f'Found {len(all_members)} members')

        # Access member data with full type safety
        for member in all_members:
            print(f'Member: {member.email} (ID: {member.id}, Name: {member.full_name})')

        # Get a specific member (replace with actual member ID)
        # member = await client.get_member(member_id=12345)
        # print(f"Member: {member.full_name} ({member.email})")

        # Get all subscriptions (convenience method that handles pagination automatically)
        all_subscriptions = await client.get_all_subscriptions()
        print(f'Found {len(all_subscriptions)} subscriptions')

        # Access subscription data with full type safety
        for subscription in all_subscriptions:
            plan_name = subscription.plan.name if subscription.plan else 'Unknown'
            print(f'Subscription: {subscription.id} - Plan: {plan_name} (Active: {subscription.active})')


if __name__ == '__main__':
    print('Running Memberful API client examples...')

    # Run the async client example
    asyncio.run(main())

    print('API examples completed!')
