import datetime
import time

import redis.asyncio as redis
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from main.core.settings import AppSettings

settings = AppSettings()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Custom rate limiter middleware.

    Should add a rate limit to the application.
    Will give X-Ratelimit-Remaining, X-Ratelimit and X-Retry-After headers.
    """

    def __init__(  # noqa: D107
        self,
        app,  # noqa: ANN001
        limit: int,
        interval: int,
        redis_pool: redis.ConnectionPool,
        *args: any,
        **kwargs: any,
    ) -> None:
        super().__init__(app, *args, **kwargs)
        self.limit = limit
        self.interval = interval
        self.redis: redis.Redis = redis.Redis(connection_pool=redis_pool)

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001, ANN201, D102
        ip = request.client.host
        if not ip:
            return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

        current_time = time.time()
        if (
            current_time - float(await self.redis.get(f"{ip}_time") or 0)
            > self.interval
        ):
            await self.redis.set(f"{ip}_time", current_time)
            await self.redis.set(f"{ip}_count", 0)
            await self.redis.expire(f"{ip}_time", self.interval)
            await self.redis.expire(f"{ip}_count", self.interval)

        requests = int(await self.redis.get(f"{ip}_count") or 0)

        if requests >= self.limit:
            retry_after = self.interval - (
                current_time - float(await self.redis.get(f"{ip}_time") or 0)
            )
            return JSONResponse(
                {"detail": "Rate limit exceeded. Retry later."},
                status_code=429,
                headers={
                    "X-Retry-After": str(datetime.datetime.now(tz=datetime.timezone.utc)
                    + datetime.timedelta(seconds=retry_after)),
                    "X-Ratelimit-Remaining": str(self.limit - requests),
                    "X-Ratelimit": str(self.limit),
                    "X-Ratelimit-Interval": str(self.interval),
                },
            )

        await self.redis.incr(f"{ip}_count")

        response = await call_next(request)
        response.headers["X-Ratelimit-Remaining"] = str(self.limit - (requests + 1))
        response.headers["X-Ratelimit"] = str(self.limit)
        response.headers["X-Ratelimit-Interval"] = str(self.interval)
        await self.redis.aclose()

        return response
