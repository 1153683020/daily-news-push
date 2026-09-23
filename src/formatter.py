from datetime import datetime, timezone, timedelta


def format_markdown(items, title, max_bytes=4096):
    def build(current_items):
        lines = [f"## {title}", ""]
        for i, item in enumerate(current_items, 1):
            lines.append(f"{i}. [{item['title']}]({item['url']})")
            lines.append(f"   {item['summary']}")
        lines.append("")
        now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
        lines.append(f"> 自动生成于 {now} 北京时间")
        return "\n".join(lines)

    content = build(items)
    while len(content.encode("utf-8")) > max_bytes and items:
        items = items[:-1]
        content = build(items)
    return content