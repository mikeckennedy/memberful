"""Basic API usage examples for the memberful package."""

import asyncio

from memberful.api import MemberfulClient


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


if __name__ == '__main__':
    print('Running Memberful API client examples...')

    # Run the async client example
    asyncio.run(main())

    print('API examples completed!')
