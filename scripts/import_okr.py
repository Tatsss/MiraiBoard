"""チームみらいの公開OKR（GitHub team-mirai/okr-content）を、ダッシュボード用の JSON にまとめる。

使い方（手で実行する。自動では動かさない）:
    git clone --depth 1 https://github.com/team-mirai/okr-content /tmp/okr-content
    python3 scripts/import_okr.py /tmp/okr-content

最新の年・クォーター（例: 2026/q4）を読み、data/okr/<年>-<q>.json に書き出す。
要約（summary）・状態（status）・数値（metrics）だけを取り出し、本文の全文は写さない。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/team-mirai/okr-content"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def progress(kr: dict) -> str | None:
    parts = []
    for m in kr.get("metrics") or []:
        if m.get("t") is None:
            continue
        parts.append(f"{m.get('c')}/{m.get('t')}{m.get('u', '')}")
    return ", ".join(parts) or None


def objective(path: Path) -> dict:
    o = load(path)
    obj = o.get("objective")
    if isinstance(obj, list):
        obj = " ".join(obj)
    krs = []
    for kr in o.get("krs") or []:
        item = {"id": kr.get("id"), "summary": kr.get("summary") or kr.get("text"), "status": kr.get("status", "不明")}
        p = progress(kr)
        if p:
            item["progress"] = p
        krs.append(item)
    return {"id": o.get("id"), "label": o.get("label"), "title": o.get("copy"), "objective": obj, "krs": krs}


def main(src: str) -> None:
    base = Path(src)
    year = sorted(p for p in base.iterdir() if p.is_dir() and p.name.isdigit())[-1]
    quarter = sorted(p for p in year.iterdir() if p.is_dir() and p.name.startswith("q"))[-1]
    meta = load(quarter / "_meta.yml")
    rel = f"{year.name}/{quarter.name}"

    party = []
    for g in load(quarter / "party.yml").get("goals", []):
        party.append({"label": g.get("label"), "title": g.get("copy"), "objective": g.get("o"), "points": g.get("plain") or []})

    hqs = []
    for d in sorted((quarter / "hq").iterdir()):
        info = load(d / "_hq.yml")
        hqs.append({
            "id": info.get("id", d.name),
            "order": info.get("order", 99),
            "name": info.get("name"),
            "desc": info.get("desc"),
            "objectives": [objective(f) for f in sorted(d.glob("o*.yml"))],
            "source": f"{REPO_URL}/tree/main/{rel}/hq/{d.name}",
        })
    hqs.sort(key=lambda h: h["order"])

    offices = []
    for d in sorted((quarter / "giinshitsu").iterdir()):
        if not d.is_dir():
            continue
        info = load(d / "_office.yml")
        offices.append({
            "id": info.get("id", d.name),
            "order": info.get("order", 99),
            "name": info.get("name"),
            "roles": info.get("roles") or [],
            "objectives": [objective(f) for f in sorted(d.glob("o*.yml"))],
            "source": f"{REPO_URL}/tree/main/{rel}/giinshitsu/{d.name}",
        })
    offices.sort(key=lambda o: o["order"])

    common = load(quarter / "giinshitsu" / "_giinshitsu.yml").get("premise", {})
    out = {
        "period": meta.get("period"),
        "updated_at": str(meta.get("updated_at")),
        "source": {"name": "チームみらい OKR（公開データ）", "url": f"{REPO_URL}/tree/main/{rel}", "site": "https://okr.team-mir.ai"},
        "notes": (meta.get("premise") or {}).get("notes", []),
        "party": party,
        "hq": hqs,
        "offices": offices,
        "office_criteria": {"title": common.get("title"), "body": common.get("body")},
    }
    dest = ROOT / "data" / "okr" / f"{year.name}-{quarter.name}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{dest.relative_to(ROOT)}: 党 {len(party)}・本部 {len(hqs)}・議員室 {len(offices)}（OKR 更新日 {out['updated_at']}）")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("使い方: python3 scripts/import_okr.py <okr-content のクローン先>")
    main(sys.argv[1])
