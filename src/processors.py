from urllib.parse import urlparse
from .utils.dedup import dedup_by_url, dedup_by_title
from .utils.text import clean_text, truncate_text


class Processor:
    def __init__(self, sources_config):
        self.sources_config = sources_config or {}

    def process(self, results, category, max_items=8):
        items = []
        for r in results:
            if not isinstance(r, dict):
                continue

            title = clean_text(r.get("title", ""))
            url = r.get("url", "")
            content = clean_text(r.get("content", ""))
            score = r.get("score", 0.0)

            if not title or not url:
                continue

            source_weight = self._source_weight(url)
            final_score = score * 0.7 + source_weight * 0.3

            items.append({
                "title": title,
                "url": url,
                "summary": truncate_text(content, 100),
                "score": final_score,
                "source_weight": source_weight,
                "category": category,
            })

        items = dedup_by_url(items)
        items = dedup_by_title(items)
        items.sort(key=lambda x: x["score"], reverse=True)
        return items[:max_items]

    def _source_weight(self, url):
        domain = urlparse(url).netloc
        weights = self.sources_config.get("weights", {})
        for d, weight in weights.items():
            if d in domain:
                return weight
        return 0.5