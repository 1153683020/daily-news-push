import asyncio
import os
import httpx
from .utils.logger import logger


class WeChatWebhook:
    def __init__(self, webhook_url=None):
        # 优先读取传入参数，其次读取环境变量（GitHub Secrets）
        config_value = webhook_url or os.getenv("WECHAT_WEBHOOK")
        if not config_value:
            raise ValueError("WECHAT_WEBHOOK is required")

        # 兼容逻辑：判断是完整地址还是纯 Key
        if config_value.startswith("http://") or config_value.startswith("https://"):
            # 是完整地址，直接使用
            self.webhook_url = config_value
        else:
            # 是纯 Key，自动拼接企业微信基础地址
            base_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="
            self.webhook_url = f"{base_url}{config_value}"

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
