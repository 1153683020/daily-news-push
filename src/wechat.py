import asyncio
import os
import httpx
from .utils.logger import logger


class WeChatWebhook:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url or os.getenv("WECHAT_WEBHOOK")
        if not self.webhook_url:
            raise ValueError("WECHAT_WEBHOOK is required")

    async def send_markdown(self, content, max_retries=3):
        payload = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }

        async with httpx.AsyncClient(timeout=10) as client:
            for attempt in range(max_retries + 1):
                try:
                    resp = await client.post(self.webhook_url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    if data.get("errcode") == 0:
                        logger.info("WeChat message sent")
                        return True
                    logger.error(f"WeChat error: {data}")
                except Exception as e:
                    logger.warning(f"WeChat send failed (attempt {attempt + 1}): {e}")

                if attempt < max_retries:
                    await asyncio.sleep(1.5 * (attempt + 1))

        return False