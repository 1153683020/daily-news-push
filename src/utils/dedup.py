from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign",
    "utm_term", "utm_content", "ref", "source"
}


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    query = [(k, v) for k, v in parse_qsl(parsed.query) if k not in TRACKING_PARAMS]
    normalized = parsed._replace(query=urlencode(query), fragment="")
    return urlunparse(normalized)


def dedup_by_url(items):
    seen = set()
    result = []
    for item in items:
        url = normalize_url(item.get("url", ""))
        if url and url not in seen:
            seen.add(url)
            result.append(item)
    return result


def dedup_by_title(items):
    result = []
    seen_titles = []
    for item in items:
        title = item.get("title", "").strip()
        if not title:
            continue
        dup = False
        for seen in seen_titles:
            if title == seen or title in seen or seen in title:
                dup = True
                break
        if not dup:
            seen_titles.append(title)
            result.append(item)
    return result