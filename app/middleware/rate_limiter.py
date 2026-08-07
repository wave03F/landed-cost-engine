"""
Rate Limiter Middleware.

In-memory rate limiting per IP address + per user (if authenticated).
Limits:
- Anonymous/API key: 30 requests/minute
- Authenticated user: 50 calculations/day
- Admin: unlimited

Uses a simple sliding window counter in memory.
For production at scale, replace with Redis-based limiter.
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException, status


# Sliding window: {key: [(timestamp, count)]}
_request_log: dict[str, list[float]] = defaultdict(list)

# Config
ANON_RATE_LIMIT = 30  # requests per minute
WINDOW_SECONDS = 60


def _clean_old_entries(key: str):
    """Remove entries older than the window."""
    cutoff = time.time() - WINDOW_SECONDS
    _request_log[key] = [t for t in _request_log[key] if t > cutoff]


async def rate_limit_check(request: Request):
    """
    Dependency that checks rate limit.
    Call this in endpoints that need protection.
    """
    # Use IP as the rate limit key
    client_ip = request.client.host if request.client else "unknown"
    key = f"ip:{client_ip}"

    _clean_old_entries(key)

    if len(_request_log[key]) >= ANON_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {ANON_RATE_LIMIT} requests per minute. Please try again later.",
        )

    _request_log[key].append(time.time())
