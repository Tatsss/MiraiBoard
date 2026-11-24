"""チームみらい公式サイトの「お知らせ一覧」を、ダッシュボード用の JSON にまとめる。

使い方（手で実行する）:
    python3 scripts/import_news.py https://team-mir.ai/news/all
    # またはダウンロード済みの HTML を渡す
    python3 scripts/import_news.py news.html

日付・見出し・リンクだけを取り出し、見出しから「どの議員か」「どの委員会か」「種類」を読み取って data/news.json に書く。
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCE_URL = "https://team-mir.ai/news/all"
COMMITTEE = re.compile(r"(衆議院|参議院)\s*([^\sにて]*?(?:委員会|本会議|審査会|調査会))")


def kind_of(title: str) -> str:
    if re.search(r"(委員会|本会議|審査会|調査会)(にて|で)", title):
        return "国会"
    if "会見" in title:
        return "会見"
    if title.startswith("YouTube") or "YouTube" in title[:12] or "配信" in title:
        return "動画・配信"
    if title.startswith("note") or "note「" in title:
        return "note"
    return "お知らせ"


def main(arg: str) -> None:
    text = urllib.request.urlopen(arg).read().decode("utf-8") if arg.startswith("http") else Path(arg).read_text(encoding="utf-8")
    members = yaml.safe_load((ROOT / "data" / "members.yaml").read_text(encoding="utf-8"))["members"]
    names = {m["name"]: m["id"] for m in members}
    items = []
    for url, body in re.findall(r'<a [^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', text):
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body))).strip()
        m = re.match(r"(20\d\d)\.(\d\d)\.(\d\d)\s*(.+)", t)
        if not m:
            continue
        title = m.group(4).strip()
        who = [mid for name, mid in names.items() if name in title]
        c = COMMITTEE.search(title)
        items.append({
            "date": f"{m.group(1)}-{m.group(2)}-{m.group(3)}",
            "title": title,
            "url": url,
            "kind": kind_of(title),
            "members": who,
            "committee": f"{c.group(1)} {c.group(2)}" if c else None,
        })
    out = {"source": {"name": "チームみらい公式サイト お知らせ一覧", "url": SOURCE_URL, "checked": str(date.today())}, "items": items}
    dest = ROOT / "data" / "news.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    kinds = {}
    for i in items:
        kinds[i["kind"]] = kinds.get(i["kind"], 0) + 1
    print(f"{dest.relative_to(ROOT)}: {len(items)}件 {kinds}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("使い方: python3 scripts/import_news.py <URL または HTML ファイル>")
    main(sys.argv[1])
