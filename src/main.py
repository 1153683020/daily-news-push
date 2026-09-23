import asyncio
import yaml
from datetime import datetime, timezone, timedelta

from .tavily_client import TavilyClient
from .processors import Processor
from .formatter import format_markdown
from .wechat import WeChatWebhook
from .utils.logger import logger


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def main():
    settings = load_yaml("config/settings.yaml")
    queries = load_yaml("config/queries.yaml")
    sources = load_yaml("config/sources.yaml")

    tavily = TavilyClient()
    processor = Processor(sources)
    wechat = WeChatWebhook()

    async def fetch(query_config, category):
        query = query_config["query"]
        include_domains = query_config.get("include_domains", [])

        search_kwargs = {
            "search_depth": settings.get("search_depth", "basic"),
            "topic": "news",
            "days": settings.get("days", 1),
            "max_results": settings.get("max_results", 8),
        }
        if include_domains:
            search_kwargs["include_domains"] = include_domains

        try:
            resp = await asyncio.wait_for(
                tavily.search(query, **search_kwargs),
                timeout=settings.get("timeout_seconds", 20),
            )
            results = resp.get("results", [])
            for r in results:
                r["_category"] = category
            return results
        except Exception as e:
            logger.error(f"Fetch failed for {category}: {e}")
            return []

    tasks = []
    for q in queries.get("domestic", []):
        tasks.append(fetch(q, "domestic"))
    for q in queries.get("international", []):
        tasks.append(fetch(q, "international"))

    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    raw_domestic = []
    raw_international = []
    for res in all_results:
        if isinstance(res, Exception):
            continue
        for item in res:
            if item.get("_category") == "domestic":
                raw_domestic.append(item)
            else:
                raw_international.append(item)

    domestic = processor.process(
        raw_domestic, "domestic",
        max_items=settings.get("max_items", 8)
    )
    international = processor.process(
        raw_international, "international",
        max_items=settings.get("max_items", 8)
    )

    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    domestic_md = format_markdown(domestic, f"国内热点 | {today}")
    international_md = format_markdown(international, f"国际热点 | {today}")

    logger.info(f"Tavily calls used: {tavily.call_count}")

    if domestic:
        await wechat.send_markdown(domestic_md)
        await asyncio.sleep(1.5)

    if international:
        await wechat.send_markdown(international_md)

    if not domestic and not international:
        await wechat.send_markdown(
            f"## 每日新闻推送 | {today}\n\n今日暂无获取到热点。"
        )


if __name__ == "__main__":
    asyncio.run(main())