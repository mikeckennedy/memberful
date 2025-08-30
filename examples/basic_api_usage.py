"""Basic API usage examples for the memberful package."""

import asyncio

from memberful.api import MemberfulClient


async def main():
    """Example usage of the Memberful client."""
    # Initialize the client with your API key
    api_key = 'your_memberful_api_key_here'

    async with MemberfulClient(api_key=api_key) as client:
        # Get list of members (now returns typed MembersResponse)
        members_response = await client.get_members(page=1, per_page=10)
        print(f'Found {len(members_response.members)} members')

        # Access member data with full type safety
        for member in members_response.members:
            print(f'Member: {member.email} (ID: {member.id}, Name: {member.full_name})')

        # Get a specific member (replace with actual member ID)
        # member = await client.get_member(member_id=12345)
        # print(f"Member: {member.full_name} ({member.email})")

        # Get subscriptions (now returns typed SubscriptionsResponse)
        subscriptions_response = await client.get_subscriptions(page=1, per_page=10)
        print(f'Found {len(subscriptions_response.subscriptions)} subscriptions')

        # Access subscription data with full type safety
        for subscription in subscriptions_response.subscriptions:
            plan_name = subscription.plan.name if subscription.plan else 'Unknown'
            print(f'Subscription: {subscription.id} - Plan: {plan_name} (Active: {subscription.active})')


if __name__ == '__main__':
    print('Running Memberful API client examples...')

    # Run the async client example
    asyncio.run(main())

    print('API examples completed!')
