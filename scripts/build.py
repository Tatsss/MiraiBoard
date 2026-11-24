"""data/ の台帳から、1画面で見られるページ docs/index.html を作る。

使い方:
    python3 scripts/build.py

データ（data/*.yaml と data/okr/*.json）をページに埋め込み、表示は docs/ 内の JavaScript が行う。
GitHub Pages で docs/ を公開すれば、そのまま見られる。ファイルを直接開いても動く。
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "scripts" / "template.html"


def y(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8")) or {}


def main() -> None:
    okr_file = sorted((DATA / "okr").glob("*.json"))[-1]
    bundle = {
        "party": y("party.yaml"),
        "process": y("process.yaml"),
        "members": y("members.yaml"),
        "timeline": y("timeline.yaml"),
        "products": y("products.yaml"),
        "channels": y("channels.yaml"),
        "jobs": y("jobs.yaml"),
        "meetings": y("meetings.yaml"),
        "okr": json.loads(okr_file.read_text(encoding="utf-8")),
    }
    updated = max(str(v.get("updated", "")) for v in bundle.values() if isinstance(v, dict))
    bundle["updated"] = updated
    data = json.dumps(bundle, ensure_ascii=False, default=str).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", data).replace("__UPDATED__", updated)
    out = ROOT / "docs" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"{out.relative_to(ROOT)} を書き出しました（最終更新 {updated}）")


if __name__ == "__main__":
    main()
