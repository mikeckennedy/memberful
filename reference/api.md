# Memberful API Reference

This document provides comprehensive documentation for the Memberful GraphQL API as implemented in our Python package. Based on the [official Memberful API documentation](https://memberful.com/help/custom-development-and-api/memberful-api/), this reference shows how to use the API through our `MemberfulClient` class.

## Getting Started

The Memberful API uses GraphQL and requires authentication via API key. All requests are made to a single endpoint with queries and mutations sent as POST requests.

### Client Setup

Import and initialize the client from:

```python
from memberful.api import MemberfulClient

# Initialize with your API key
client = MemberfulClient(api_key="your_api_key_here")

# Use as async context manager (recommended)
async with MemberfulClient(api_key="your_api_key_here") as client:
    members = await client.get_members()
```

### Configuration Options

The `MemberfulClient` class accepts these parameters:

- **`api_key`** (required): Your Memberful API key from Settings → Custom Applications
- **`base_url`**: API base URL (default: `https://api.memberful.com`)
- **`timeout`**: Request timeout in seconds (default: 30.0)

## API Endpoint

All requests go to: `https://ACCOUNT-URL.memberful.com/api/graphql`

**Note**: The current implementation uses a REST-like interface (`https://api.memberful.com`) but Memberful's actual API is GraphQL-based. Future versions may align more closely with the GraphQL endpoint pattern.

## Authentication

Authentication is handled automatically by the client using Bearer token authentication:

```
Authorization: Bearer <your-api-key>
```

API keys are generated from your Memberful dashboard under **Settings → Custom Applications**.

## Member Operations

### Get Members List

Retrieve a paginated list of all members.

**Method**: `client.get_members(page=1, per_page=100)`

**GraphQL Equivalent**:
```graphql
query {
  members(first: 100, after: "cursor") {
    edges {
      node {
        id
        fullName
        email
        createdAt
        subscriptions {
          edges {
            node {
              id
              plan {
                id
                name
              }
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

**Parameters**:
- `page` (int): Page number, starting from 1
- `per_page` (int): Number of members per page (max 100)

**Example Usage**:
```python
async with MemberfulClient(api_key="your_key") as client:
    # Get first page of members
    response = await client.get_members(page=1, per_page=50)
    members = response.get("members", [])
    
    for member in members:
        print(f"Member: {member['email']} (ID: {member['id']})")
```

### Get Individual Member

Retrieve detailed information about a specific member.

**Method**: `client.get_member(member_id)`

**GraphQL Equivalent**:
```graphql
query {
  member(id: 123) {
    id
    fullName
    email
    createdAt
    subscriptions {
      edges {
        node {
          id
          active
          expiresAt
          plan {
            id
            name
            price
          }
        }
      }
    }
  }
}
```

**Parameters**:
- `member_id` (int): The unique ID of the member

**Example Usage**:
```python
async with MemberfulClient(api_key="your_key") as client:
    member = await client.get_member(member_id=12345)
    print(f"Member: {member['full_name']} ({member['email']})")
    print(f"Joined: {member['created_at']}")
```

## Subscription Operations

### Get Subscriptions

Retrieve subscriptions, optionally filtered by member.

**Method**: `client.get_subscriptions(member_id=None, page=1, per_page=100)`

**GraphQL Equivalent**:
```graphql
query {
  subscriptions(first: 100, after: "cursor") {
    edges {
      node {
        id
        active
        createdAt
        expiresAt
        member {
          id
          fullName
          email
        }
        plan {
          id
          name
          price
          renewalPeriod
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

**Parameters**:
- `member_id` (int, optional): Filter subscriptions for specific member
- `page` (int): Page number, starting from 1
- `per_page` (int): Number of subscriptions per page (max 100)

**Example Usage**:
```python
async with MemberfulClient(api_key="your_key") as client:
    # Get all subscriptions
    all_subs = await client.get_subscriptions(page=1, per_page=100)
    
    # Get subscriptions for specific member
    member_subs = await client.get_subscriptions(member_id=12345)
    
    for subscription in member_subs.get("subscriptions", []):
        plan = subscription.get("plan", {})
        print(f"Plan: {plan.get('name')} - ${plan.get('price', 0)/100}")
```

## Error Handling

The Memberful API always returns HTTP 200, with errors included in the response body:

### Authentication Errors
```json
{
  "errors": [
    {
      "message": "Invalid authentication token."
    }
  ]
}
```

### Request Errors
```json
{
  "errors": [
    {
      "message": "Field 'member' is missing required arguments: id",
      "locations": [{"line": 2, "column": 3}],
      "fields": ["query", "member"]
    }
  ]
}
```

### Client Error Handling

The client automatically raises `httpx.HTTPStatusError` for HTTP errors:

```python
from httpx import HTTPStatusError

try:
    async with MemberfulClient(api_key="invalid_key") as client:
        members = await client.get_members()
except HTTPStatusError as e:
    print(f"HTTP Error: {e.response.status_code}")
    print(f"Response: {e.response.text}")
```

## GraphQL Query Patterns

While our client provides convenience methods, you can understand the underlying GraphQL patterns:

### Basic Query Structure
```graphql
query {
  member(id: 123) {
    id
    fullName
    email
  }
}
```

### Mutation Structure
```graphql
mutation {
  memberCreate(email: "user@example.com", fullName: "John Doe") {
    member {
      id
      username
    }
  }
}
```

### Pagination Pattern
```graphql
query {
  members(first: 10, after: "cursor_string") {
    edges {
      node {
        id
        email
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

## Advanced Usage

### Custom Request Timeout
```python
client = MemberfulClient(
    api_key="your_key",
    timeout=60.0  # 60 seconds
)
```

### Manual Client Management
```python
client = MemberfulClient(api_key="your_key")

try:
    members = await client.get_members()
    # Process members...
finally:
    await client.close()  # Clean up resources
```

### Batch Operations
```python
async with MemberfulClient(api_key="your_key") as client:
    # Process multiple pages
    all_members = []
    page = 1
    
    while True:
        response = await client.get_members(page=page, per_page=100)
        members = response.get("members", [])
        
        if not members:
            break
            
        all_members.extend(members)
        page += 1
        
        # Respect rate limits
        await asyncio.sleep(0.1)
```

## Data Types and Structures

### Member Object
```python
{
    "id": 12345,
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": 1756245496,
    "stripe_customer_id": "cus_12345",
    "subscriptions": [...],
    "custom_fields": {...}
}
```

### Subscription Object
```python
{
    "id": 67890,
    "active": True,
    "created_at": 1756245496,
    "expires_at": 1758837496,
    "plan": {
        "id": 1,
        "name": "Premium Plan",
        "price": 2999,  # Price in cents
        "renewal_period": "monthly"
    }
}
```

## Limitations and Future Enhancements

### Current Limitations
- **REST-like Interface**: Current client uses REST-style endpoints rather than native GraphQL
- **Limited Operations**: Only supports read operations (queries), no mutations yet
- **No Custom Fields**: Custom field data access not yet implemented
- **Basic Pagination**: Simple page-based pagination instead of cursor-based

### Planned Enhancements
- **GraphQL Native**: Direct GraphQL query support with full flexibility
- **Mutation Support**: Create, update, and delete operations
- **Advanced Filtering**: Complex query filters and sorting
- **Custom Fields API**: Access to new custom fields architecture
- **Cursor Pagination**: More efficient cursor-based pagination
- **Bulk Operations**: Batch create/update operations

## Related Documentation

- **Webhooks**: See `webhooks.md` for webhook event handling
- **Examples**: Check `examples/basic_usage.py` for practical examples
- **Official API**: [Memberful API Documentation](https://memberful.com/help/custom-development-and-api/memberful-api/)
- **GraphQL**: [GraphQL API Explorer](https://memberful.com/help/custom-development-and-api/memberful-api/#using-the-graphql-api-explorer)

## Best Practices

### 1. Use Async Context Managers
```python
# Recommended
async with MemberfulClient(api_key=key) as client:
    data = await client.get_members()

# Avoid
client = MemberfulClient(api_key=key)
data = await client.get_members()
# client.close() forgotten!
```

### 2. Handle Pagination Properly
```python
async def get_all_members(client):
    all_members = []
    page = 1
    
    while True:
        response = await client.get_members(page=page)
        members = response.get("members", [])
        
        if not members:
            break
            
        all_members.extend(members)
        page += 1
        
        # Rate limiting
        if page % 10 == 0:
            await asyncio.sleep(1)
    
    return all_members
```

### 3. Error Handling
```python
from httpx import HTTPStatusError, ConnectError

async def safe_api_call():
    try:
        async with MemberfulClient(api_key=key) as client:
            return await client.get_members()
    except HTTPStatusError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API key")
        elif e.response.status_code == 429:
            raise ValueError("Rate limit exceeded")
        raise
    except ConnectError:
        raise ValueError("Connection failed - check internet connection")
```

### 4. Environment-Based Configuration
```python
import os

api_key = os.environ.get("MEMBERFUL_API_KEY")
if not api_key:
    raise ValueError("MEMBERFUL_API_KEY environment variable required")

client = MemberfulClient(api_key=api_key)
```

## Rate Limiting

Memberful implements rate limiting on their API. Best practices:

- **Batch requests** when possible
- **Add delays** between requests in loops
- **Implement backoff** for rate limit errors
- **Cache results** when appropriate

```python
import asyncio
from httpx import HTTPStatusError

async def with_rate_limiting(client, operation):
    """Execute API operation with automatic rate limit handling."""
    max_retries = 3
    backoff = 1
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff)
                    backoff *= 2  # Exponential backoff
                    continue
            raise
```
