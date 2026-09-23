import asyncio
import random
from .logger import logger


async def async_retry(func, max_retries=2, base_delay=1.0):
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exc = e
            if attempt == max_retries:
                break
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}")
            await asyncio.sleep(delay)
    raise last_exc