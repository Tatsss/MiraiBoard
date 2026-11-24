"""data/ の台帳と site/ のページから、公開用の docs/ を作る。

使い方:
    python3 scripts/build.py

- site/ のページと assets を docs/ にそのまま写す
- data/*.yaml・data/*.json をまとめて docs/assets/data.js（window.MB）に書き出す
GitHub Pages で docs/ を公開すれば、そのまま見られる。ファイルを直接開いても動く。
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA, SITE, DOCS = ROOT / "data", ROOT / "site", ROOT / "docs"


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
        "news": json.loads((DATA / "news.json").read_text(encoding="utf-8")),
    }
    bundle["updated"] = max(str(v.get("updated", "")) for v in bundle.values() if isinstance(v, dict))

    if DOCS.exists():
        shutil.rmtree(DOCS)
    shutil.copytree(SITE, DOCS)
    (DOCS / "assets" / "data.js").write_text(
        "window.MB = " + json.dumps(bundle, ensure_ascii=False, default=str) + ";\n", encoding="utf-8"
    )
    pages = sorted(p.name for p in DOCS.glob("*.html"))
    print(f"docs/ を書き出しました: {', '.join(pages)}（最終更新 {bundle['updated']}）")


if __name__ == "__main__":
    main()
