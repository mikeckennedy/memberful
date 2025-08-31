# Memberful API Reference

This document provides comprehensive documentation for the Memberful GraphQL API as implemented in our Python package. Based on the [official Memberful API documentation](https://memberful.com/help/custom-development-and-api/memberful-api/), this reference shows how to use the API through our `MemberfulClient` class.

**✅ GraphQL Native Implementation**: This client now uses native GraphQL queries with cursor-based pagination, properly aligned with Memberful's actual GraphQL schema. All field names and structures match the real API endpoints.

## Type Safety with Pydantic Models

Our API client returns fully typed Pydantic models instead of raw dictionaries, providing:

- **Type Safety**: Full IDE autocomplete and type checking
- **Runtime Validation**: Automatic data validation and parsing
- **Better Documentation**: Clear data structure definitions
- **Easier Development**: Intuitive attribute access instead of dictionary keys

All API responses are automatically parsed into strongly-typed models from `memberful.api.models`.

## GraphQL Schema Alignment

Our implementation uses the actual Memberful GraphQL schema with these key characteristics:

- **Field Names**: Uses camelCase as per GraphQL conventions (e.g., `fullName`, `stripeCustomerId`, `unrestrictedAccess`)
- **Cursor Pagination**: Implements proper GraphQL connection patterns with `edges`, `nodes`, and `pageInfo`
- **Available Fields**: Only includes fields actually available in the schema (some fields like `createdAt` on Member, `signupMethod`, and `inTrialPeriod` are not available)
- **Plan Structure**: Uses `intervalUnit` and `intervalCount` instead of `price` and `renewalPeriod`
- **Address Fields**: Uses `street` instead of separate `addressLine1`/`addressLine2` fields

## Getting Started

The Memberful API uses GraphQL and requires authentication via API key. All requests are made to a single endpoint with queries and mutations sent as POST requests.

### Client Setup

Import and initialize the client from:

```python
from memberful.api import MemberfulClient
# Optional: Import models for type hints
from memberful.api.models import Member, MembersResponse, Subscription, SubscriptionsResponse

# Initialize with your API key
client = MemberfulClient(api_key="your_api_key_here")

# Use as async context manager (recommended)
async with MemberfulClient(api_key="your_api_key_here") as client:
    members_response = await client.get_members()  # Returns MembersResponse
    members = members_response.members  # List of Member objects
```

### Configuration Options

The `MemberfulClient` class accepts these parameters:

- **`api_key`** (required): Your Memberful API key from Settings → Custom Applications
- **`base_url`**: API base URL (default: `https://youraccount.memberful.com` - replace with your actual Memberful account)
- **`timeout`**: Request timeout in seconds (default: 30.0)

## API Endpoint

All requests go to: `https://youraccount.memberful.com/api/graphql` (where "youraccount" is your actual Memberful account name)

The API is fully GraphQL-based, using cursor-based pagination and proper GraphQL field names. All queries are sent as POST requests to the GraphQL endpoint with Bearer token authentication.

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

**Returns**: `MembersResponse` - A typed Pydantic model containing:
- `members`: List of `Member` objects
- `total_count`, `total_pages`, `current_page`, `per_page`: Pagination metadata (optional)

**GraphQL Equivalent**:
```graphql
query GetMembers($first: Int!, $after: String) {
  members(first: $first, after: $after) {
    edges {
      node {
        id
        email
        fullName
        username
        stripeCustomerId
        unrestrictedAccess
        address {
          city
          country
          state
          postalCode
          street
        }
        subscriptions {
          id
          active
          createdAt
          expiresAt
          trialEndAt
          plan {
            id
            name
            intervalUnit
            intervalCount
            slug
          }
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
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
    # Get first page of members (returns MembersResponse)
    response = await client.get_members(page=1, per_page=50)
    
    # Access members with full type safety
    print(f"Found {len(response.members)} members")
    
    for member in response.members:
        print(f"Member: {member.email} (ID: {member.id})")
        print(f"Name: {member.full_name or 'No name'}")
        if member.stripe_customer_id:
            print(f"Stripe ID: {member.stripe_customer_id}")
        
        # Access nested subscription data if available
        if member.subscriptions:
            for subscription in member.subscriptions:
                plan_name = subscription.plan.name if subscription.plan else 'Unknown'
                print(f"  Subscription: {plan_name} (Active: {subscription.active})")
                if subscription.plan and subscription.plan.interval_unit:
                    print(f"    Billing: {subscription.plan.interval_count} {subscription.plan.interval_unit}")
```

### Get Individual Member

Retrieve detailed information about a specific member.

**Method**: `client.get_member(member_id)`

**Returns**: `Member` - A typed Pydantic model with complete member information

**GraphQL Equivalent**:
```graphql
query GetMember($id: ID!) {
  member(id: $id) {
    id
    email
    fullName
    username
    stripeCustomerId
    unrestrictedAccess
    address {
      city
      country
      state
      postalCode
      street
    }
    subscriptions {
      id
      active
      createdAt
      expiresAt
      trialEndAt
      plan {
        id
        name
        intervalUnit
        intervalCount
        slug
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
    # Returns Member object with full type safety
    member = await client.get_member(member_id=12345)
    
    print(f"Member: {member.full_name or 'No name'} ({member.email})")
    print(f"Username: {member.username or 'No username'}")
    if member.stripe_customer_id:
        print(f"Stripe Customer ID: {member.stripe_customer_id}")
    
    # Access address information if available
    if member.address:
        print(f"Location: {member.address.city}, {member.address.country}")
    
    # Access subscription information if available
    if member.subscriptions:
        active_subs = [s for s in member.subscriptions if s.active]
        print(f"Active subscriptions: {len(active_subs)}")
```

### Get All Members (Convenience Method)

Retrieve ALL members by automatically handling pagination. This method calls `get_members()` repeatedly until all members are retrieved.

**Method**: `client.get_all_members()`

**Parameters**: None

**Returns**:
- `list[Member]`: List containing all Member objects (not paginated response)

**Example Usage**:
```python
async with MemberfulClient(api_key="your_key") as client:
    # Get ALL members across all pages automatically (returns list[Member])
    all_members = await client.get_all_members()
    
    print(f"Total members: {len(all_members)}")
    for member in all_members:
        print(f"Member: {member.email} (ID: {member.id})")
        print(f"Name: {member.full_name or 'No name'}")
        
        # Type-safe access to all member attributes
        if member.stripe_customer_id:
            print(f"Stripe ID: {member.stripe_customer_id}")
        if member.unrestricted_access:
            print(f"Has unrestricted access: {member.unrestricted_access}")
```

**Key Features**:
- **Automatic Pagination**: Handles all pages transparently
- **Rate Limiting**: Includes small delays between requests to respect API limits
- **Type Safety**: Returns flat list of `Member` objects with full IDE support
- **High Efficiency**: Uses 100 members per page for optimal performance

**Note**: This method is ideal when you need to process all members and don't want to manually handle pagination. For large datasets, consider the paginated `get_members()` method if you need more control over memory usage or processing.

## Subscription Operations

### Get Subscriptions

Retrieve subscriptions, optionally filtered by member.

**Method**: `client.get_subscriptions(member_id=None, page=1, per_page=100)`

**Returns**: `SubscriptionsResponse` - A typed Pydantic model containing:
- `subscriptions`: List of `Subscription` objects
- `total_count`, `total_pages`, `current_page`, `per_page`: Pagination metadata (optional)

**GraphQL Equivalent**:
```graphql
query GetAllSubscriptions($first: Int!, $after: String) {
  subscriptions(first: $first, after: $after) {
    edges {
      node {
        id
        active
        createdAt
        expiresAt
        trialEndAt
        plan {
          id
          name
          intervalUnit
          intervalCount
          slug
        }
        member {
          id
          email
          fullName
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
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
    # Get all subscriptions (returns SubscriptionsResponse)
    all_subs = await client.get_subscriptions(page=1, per_page=100)
    
    # Get subscriptions for specific member
    member_subs = await client.get_subscriptions(member_id=12345)
    
    for subscription in member_subs.subscriptions:
        # Type-safe access to subscription and plan data
        if subscription.plan:
            print(f"Plan: {subscription.plan.name}")
            if subscription.plan.interval_unit and subscription.plan.interval_count:
                print(f"Billing: {subscription.plan.interval_count} {subscription.plan.interval_unit}")
            print(f"Slug: {subscription.plan.slug}")
        
        print(f"Active: {subscription.active}")
        if subscription.created_at:
            print(f"Created: {subscription.created_at}")
        
        if subscription.expires_at:
            print(f"Expires: {subscription.expires_at}")
        if subscription.trial_end_at:
            print(f"Trial ends: {subscription.trial_end_at}")
```

### Get All Subscriptions (Convenience Method)

Retrieve ALL subscriptions by automatically handling pagination. This method calls `get_subscriptions()` repeatedly until all subscriptions are retrieved.

**Method**: `client.get_all_subscriptions(member_id=None)`

**Parameters**:
- `member_id` (int, optional): Filter subscriptions for specific member (None = all members)

**Returns**:
- `list[Subscription]`: List containing all Subscription objects (not paginated response)

**Example Usage**:
```python
async with MemberfulClient(api_key="your_key") as client:
    # Get ALL subscriptions across all members (returns list[Subscription])
    all_subscriptions = await client.get_all_subscriptions()
    print(f"Total subscriptions: {len(all_subscriptions)}")
    
    # Get ALL subscriptions for a specific member
    member_subscriptions = await client.get_all_subscriptions(member_id=12345)
    print(f"Member has {len(member_subscriptions)} subscriptions")
    
    for subscription in all_subscriptions:
        # Full type safety with nested plan access
        plan_info = f"Plan: {subscription.plan.name}" if subscription.plan else "No plan"
        print(f"{plan_info} - Active: {subscription.active}")
        
        # Access all subscription attributes with autocomplete
        if subscription.trial_end_at:
            print(f"  Trial ends: {subscription.trial_end_at}")
```

**Key Features**:
- **Maintains Filtering**: Preserves optional member_id filtering from original method
- **Automatic Pagination**: Handles all pages transparently for specified filter
- **Rate Limiting**: Includes small delays between requests to respect API limits
- **Type Safety**: Returns flat list of `Subscription` objects with full IDE support
- **High Efficiency**: Uses 100 subscriptions per page for optimal performance

**Use Cases**:
- **All Subscriptions**: `get_all_subscriptions()` - Process every subscription across all members
- **Member's Subscriptions**: `get_all_subscriptions(member_id=123)` - Get complete subscription history for a specific member

**Note**: This method is ideal when you need to process all subscriptions (optionally filtered by member) and don't want to manually handle pagination. For large datasets, consider the paginated `get_subscriptions()` method if you need more control over memory usage or processing.

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
        members = response.members  # Access typed members list
        
        if not members:
            break
            
        all_members.extend(members)
        page += 1
        
        # Respect rate limits
        await asyncio.sleep(0.1)
```

## Data Types and Structures

### Pydantic Models

All API responses use strongly-typed Pydantic models. Here are the key models:

#### Member Model
```python
from memberful.api.models import Member

# Example Member object with full type safety
member = Member(
    id=12345,
    email="john@example.com",
    full_name="John Doe",
    username="johndoe",
    stripe_customer_id="cus_12345",
    unrestricted_access=False,
    # Optional nested objects
    address=Address(city="San Francisco", country="US", state="CA", postal_code="94105", street="123 Main St"),
    subscriptions=[...],  # List of Subscription objects
    custom_fields={"company": "Acme Corp"}
)

# Access with full IDE support
print(member.email)  # IDE autocomplete works
print(member.address.city if member.address else "No address")
```

#### Subscription Model
```python
from memberful.api.models import Subscription, Plan

# Example Subscription object
subscription = Subscription(
    id=67890,
    active=True,
    created_at=1756245496,
    expires_at=1758837496,
    trial_end_at=None,
    plan=Plan(
        id=1,
        name="Premium Plan",
        interval_unit="month",  # Available field
        interval_count=1,       # Available field
        slug="premium"
    )
)

# Type-safe access to all fields
if subscription.plan:
    print(f"Plan: {subscription.plan.name}")
    print(f"Billing: {subscription.plan.interval_count} {subscription.plan.interval_unit}")  # Actual available fields
```

#### Response Models
```python
from memberful.api.models import MembersResponse, SubscriptionsResponse

# Paginated responses include metadata
response = MembersResponse(
    members=[member1, member2, ...],  # List of Member objects
    total_count=150,
    current_page=1,
    per_page=100
)

# Direct access to data and pagination info
for member in response.members:
    print(member.email)
    
print(f"Page {response.current_page} of {response.total_pages}")
```

## Limitations and Future Enhancements

### Current Limitations
- **Limited Operations**: Only supports read operations (queries), no mutations yet
- **Schema Restrictions**: Some fields like `createdAt`, `signupMethod`, and `inTrialPeriod` are not available in the current GraphQL schema
- **Pagination Metadata**: Total count information is estimated based on `hasNextPage` rather than exact counts
- **No Custom Fields**: Custom field data access not yet implemented

### Planned Enhancements
- **Mutation Support**: Create, update, and delete operations
- **Advanced Filtering**: Complex query filters and sorting
- **Custom Fields API**: Access to new custom fields architecture
- **Direct GraphQL**: Raw GraphQL query support for advanced use cases
- **Bulk Operations**: Batch create/update operations
- **Schema Updates**: Support for additional fields as they become available in the API

## Available Models

All models are available from `memberful.api.models`:

### Core Models
- `Member` - Complete member information (email, fullName, username, stripeCustomerId, etc.)
- `Subscription` - Subscription details with plan relationships (active, createdAt, expiresAt, trialEndAt)
- `Plan` - Subscription plan information (name, intervalUnit, intervalCount, slug)
- `Product` - Download/product details
- `Address` - Member address information (city, country, state, postalCode, street)
- `CreditCard` - Payment method information
- `TrackingParams` - UTM tracking parameters

### Response Models
- `MembersResponse` - Paginated members list
- `SubscriptionsResponse` - Paginated subscriptions list
- `MemberResponse` - Single member wrapper
- `SubscriptionResponse` - Single subscription wrapper

### Enums
- `SignupMethod` - How the member signed up (checkout, manual, api, import)
- `RenewalPeriod` - Subscription renewal frequency (monthly, yearly, etc.)
- `IntervalUnit` - Time interval units (month, year, quarter, week, day)

All models include extra field handling and provide an `extras` property for accessing any additional data not explicitly defined in the model schema.

## Related Documentation

- **Webhooks**: See `webhooks.md` for webhook event handling
- **Examples**: Check `examples/basic_api_usage.py` for practical examples with typed models
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

### 2. Use Convenience Methods for Complete Data Sets
```python
# Recommended: Use convenience methods for getting all data
async with MemberfulClient(api_key=key) as client:
    # Get all members automatically with pagination handling (returns list[Member])
    all_members = await client.get_all_members()
    
    # Full type safety - no more dictionary access
    for member in all_members:
        print(f"{member.full_name} - {member.email}")
        if member.subscriptions:
            active_count = sum(1 for s in member.subscriptions if s.active)
            print(f"  Active subscriptions: {active_count}")
    
    # Get all subscriptions for all members (returns list[Subscription])
    all_subscriptions = await client.get_all_subscriptions()
    
    # Get all subscriptions for a specific member
    member_subscriptions = await client.get_all_subscriptions(member_id=12345)

# For manual pagination control (advanced use cases):
async def manual_pagination_example(client):
    all_members = []
    page = 1
    
    while True:
        # Returns MembersResponse with type safety
        response = await client.get_members(page=page, per_page=50)
        
        if not response.members:  # Access typed members list
            break
            
        all_members.extend(response.members)
        page += 1
        
        # Custom rate limiting with pagination metadata
        print(f"Processed page {response.current_page} of {response.total_pages}")
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
            # Returns MembersResponse, not dict
            response = await client.get_members()
            return response.members  # Extract typed Member objects
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
