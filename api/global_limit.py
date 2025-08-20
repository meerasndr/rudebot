# global_limit.py
import time
import asyncio
from dataclasses import dataclass

@dataclass
class Bucket:
    tokens: float
    last: float

class GlobalTokenBucket:
    """
    Global limiter: shared, in-process token bucket.
    rate_per_sec: average refill rate (tokens/second)
    burst: max tokens (bucket capacity)
    """
    def __init__(self, rate_per_sec: float, burst: int):
        self.rate = rate_per_sec
        self.capacity = burst
        self.bucket = Bucket(tokens=burst, last=time.time())
        self._lock = asyncio.Lock()

    async def allow(self) -> float | None:
        """
        Returns None if allowed, or retry-after seconds (float) if limited.
        """
        async with self._lock:
            now = time.time()
            elapsed = now - self.bucket.last
            # refill
            self.bucket.tokens = min(
                self.capacity, self.bucket.tokens + elapsed * self.rate
            )
            self.bucket.last = now

            if self.bucket.tokens >= 1:
                self.bucket.tokens -= 1
                return None

            # compute retry-after = time until 1 token accrues
            deficit = 1 - self.bucket.tokens
            retry_after = deficit / self.rate
            return max(0.5, retry_after)

# 25 calls/minute => ~0.4167 tokens/sec, burst 25
global_bucket = GlobalTokenBucket(rate_per_sec=25/60.0, burst=25)
