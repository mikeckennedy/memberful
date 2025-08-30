"""Memberful API client."""

from typing import Any, Optional

import httpx
from pydantic import BaseModel


class MemberfulClientConfig(BaseModel):
    """Configuration for the Memberful client."""

    api_key: str
    base_url: str = 'https://api.memberful.com'
    timeout: float = 30.0


class MemberfulClient:
    """Client for interacting with the Memberful API."""

    def __init__(self, api_key: str, base_url: str = 'https://api.memberful.com', timeout: float = 30.0):
        """Initialize the Memberful client.

        Args:
            api_key: Your Memberful API key
            base_url: Base URL for the Memberful API
            timeout: Request timeout in seconds
        """
        self.config = MemberfulClientConfig(api_key=api_key, base_url=base_url, timeout=timeout)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure the HTTP client is initialized."""
        if not self._client:
            headers = {
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'memberful-python/0.1.0',
            }
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout,
            )
        return self._client

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make an HTTP request to the Memberful API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments passed to httpx

        Returns:
            httpx.Response object
        """
        client = await self._ensure_client()
        response = await client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response

    async def get_members(self, page: int = 1, per_page: int = 100) -> dict[str, Any]:
        """Get list of members.

        Args:
            page: Page number (default: 1)
            per_page: Number of members per page (default: 100)

        Returns:
            Dictionary containing members data
        """
        response = await self._request('GET', '/v1/members', params={'page': page, 'per_page': per_page})
        return response.json()

    async def get_member(self, member_id: int) -> dict[str, Any]:
        """Get a specific member by ID.

        Args:
            member_id: The member's ID

        Returns:
            Dictionary containing member data
        """
        response = await self._request('GET', f'/v1/members/{member_id}')
        return response.json()

    async def get_subscriptions(
        self, member_id: Optional[int] = None, page: int = 1, per_page: int = 100
    ) -> dict[str, Any]:
        """Get subscriptions, optionally for a specific member.

        Args:
            member_id: Optional member ID to filter subscriptions
            page: Page number (default: 1)
            per_page: Number of subscriptions per page (default: 100)

        Returns:
            Dictionary containing subscriptions data
        """
        params = {'page': page, 'per_page': per_page}
        if member_id:
            params['member_id'] = member_id

        response = await self._request('GET', '/v1/subscriptions', params=params)
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
