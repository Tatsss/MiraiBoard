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


def okr_changes(cur: dict, okr_file: Path) -> dict:
    """同じ期の、ひとつ前の取り込み（data/okr/history/）と比べて、状態か進み具合が変わった KR を並べる。"""
    hist = sorted((DATA / "okr" / "history").glob(f"{okr_file.stem}_*.json"))
    hist = [h for h in hist if h.stem.split("_", 1)[1] < str(cur["updated_at"])]
    if not hist:
        return {"from": None, "to": cur["updated_at"], "items": []}
    prev = json.loads(hist[-1].read_text(encoding="utf-8"))
    items = []
    for kid, k in cur["kr_index"].items():
        p = prev["kr_index"].get(kid)
        if p is None:
            items.append({"id": kid, "new": True, "to_status": k.get("status"), "to_progress": k.get("progress")})
        elif (p.get("status"), p.get("progress")) != (k.get("status"), k.get("progress")):
            items.append({"id": kid, "from_status": p.get("status"), "from_progress": p.get("progress"),
                          "to_status": k.get("status"), "to_progress": k.get("progress")})
    return {"from": prev["updated_at"], "to": cur["updated_at"], "items": items}


def main() -> None:
    okr_file = sorted((DATA / "okr").glob("*.json"))[-1]
    bundle = {
        "party": y("party.yaml"),
        "process": y("process.yaml"),
        "members": y("members.yaml"),
        "timeline": y("timeline.yaml"),
        "products": y("products.yaml"),
        "channels": y("channels.yaml"),
        "repos": y("repos.yaml"),
        "jobs": y("jobs.yaml"),
        "meetings": y("meetings.yaml"),
        "guide": y("guide.yaml"),
        "okr": json.loads(okr_file.read_text(encoding="utf-8")),
        "news": json.loads((DATA / "news.json").read_text(encoding="utf-8")),
    }
    bundle["okr_changes"] = okr_changes(bundle["okr"], okr_file)
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
