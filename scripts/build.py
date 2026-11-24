"""data/ の台帳から、1画面で見られるページ docs/index.html を作る。

使い方:
    python3 scripts/build.py

docs/ は GitHub Pages でそのまま公開できる。データはページに埋め込むので、ファイルを直接開いても見られる。
"""

from __future__ import annotations

import html
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

STATUS_CLASS = {"達成": "done", "順調": "ok", "注意": "warn", "未着手": "todo"}


def y(name: str) -> dict:
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8")) or {}


def e(s: object) -> str:
    return html.escape("" if s is None else str(s))


def link(url: str | None, text: str | None = None) -> str:
    if not url:
        return e(text or "")
    return f'<a href="{e(url)}" target="_blank" rel="noopener">{e(text or url)}</a>'


def src(s: dict | None) -> str:
    if not s:
        return '<span class="src missing">出典未確認</span>'
    checked = f"（{e(s.get('checked'))} 確認）" if s.get("checked") else ""
    return f'<span class="src">出典: {link(s.get("url"), s.get("name"))}{checked}</span>'


def status(s: str) -> str:
    return f'<span class="st {STATUS_CLASS.get(s, "unk")}">{e(s)}</span>'


def objectives(objs: list[dict]) -> str:
    out = []
    for o in objs:
        krs = "".join(
            f'<li>{status(k["status"])} {e(k["summary"])}'
            + (f' <span class="prog">{e(k["progress"])}</span>' if k.get("progress") else "")
            + "</li>"
            for k in o.get("krs", [])
        )
        out.append(
            f'<div class="obj"><div class="obj-h"><span class="lbl">{e(o.get("label"))}</span>{e(o.get("title"))}</div>'
            + (f'<p class="obj-d">{e(o.get("objective"))}</p>' if o.get("objective") else "")
            + f"<ul class=\"krs\">{krs}</ul></div>"
        )
    return "".join(out)


def build() -> str:
    party = y("party.yaml")
    members = y("members.yaml")
    timeline = y("timeline.yaml")
    products = y("products.yaml")
    channels = y("channels.yaml")
    meetings = y("meetings.yaml")
    okr_file = sorted((DATA / "okr").glob("*.json"))[-1]
    okr = json.loads(okr_file.read_text(encoding="utf-8"))
    offices = {o["id"]: o for o in okr["offices"]}
    okr_src = {"name": f"{okr['source']['name']} {okr['period']}（更新日 {okr['updated_at']}）", "url": okr["source"]["url"]}

    updated = max(str(d.get("updated", "")) for d in (party, members, timeline, products, channels, meetings))

    # --- 党の概要 ---
    nums = "".join(f'<div class="num"><div class="v">{e(n["value"])}</div><div class="l">{e(n["label"])}</div></div>' for n in party["numbers"]["items"])
    vision = "".join(f'<li><b>{e(v["title"])}</b> — {e(v["point"])}</li>' for v in party["vision"])
    values = "".join(f'<li><b>{e(v["title"])}</b> — {e(v["point"])}</li>' for v in party["values"])
    cycle = "".join(f'<tr><td><b>{e(r["step"])}</b></td><td>{e(r["officer"])}</td><td>{e(r["scope"])}</td></tr>' for r in party["cycle"]["roles"])
    hq_list = "".join(f'<tr><td><b>{e(h["name"])}</b></td><td>{e(h.get("desc") or "—")}</td></tr>' for h in okr["hq"])
    goals = "".join(
        f'<div class="goal"><div class="goal-h"><span class="lbl">{e(g["label"])}</span>{e(g["title"])}</div><p>{e(g["objective"])}</p>'
        + "<ul>" + "".join(f"<li>{e(p)}</li>" for p in g["points"]) + "</ul></div>"
        for g in okr["party"]
    )

    # --- 議員 ---
    cards = []
    nav_members = []
    for m in members["members"]:
        off = offices.get(m["id"], {})
        ch = " ".join(link(c["url"], c["kind"]) for c in m["channels"]) or "不明"
        recent = "".join(
            f'<li><span class="date">{e(r["date"])}</span> {link(r["url"], r["title"])} <span class="kind">{e(r["kind"])}</span></li>' for r in m["recent"]
        ) or "<li>直近の公開活動は未確認</li>"
        srcs = " ".join(src(s) for s in m["sources"])
        unknown = "、".join(m.get("unknown") or []) or "—"
        roles = "／".join(m["party_roles"])
        nav_members.append(f'<a href="#m-{e(m["id"])}">{e(m["name"])}</a>')
        cards.append(f"""
<article class="card member" id="m-{e(m['id'])}">
  <header>
    <div class="nm">{e(m['name'])}<span class="kana">{e(m['kana'])}</span></div>
    <div class="meta">{e(m['house'])}・{e(m['district'])}</div>
    <div class="roles">{e(roles)}</div>
  </header>
  <p class="catch">「{e(m['catchphrase'])}」</p>
  <details><summary>本人のことば・経歴（公式プロフィール）</summary><p>{e(m['statement'])}</p><p class="prof">{e(m['profile'])}</p></details>
  <h4>この議員室の目標と進み具合（OKR {e(okr['period'])}）</h4>
  {objectives(off.get('objectives', [])) or '<p>OKRの記載なし</p>'}
  <h4>直近の動き</h4><ul class="recent">{recent}</ul>
  <h4>発信チャンネル</h4><p class="ch">{ch}</p>
  <p class="unknown">分からないこと: {e(unknown)}</p>
  <footer>{srcs} {src({'name': 'OKR（議員室）', 'url': off.get('source')}) if off else ''}</footer>
</article>""")

    # --- 本部の目標 ---
    hq_cards = "".join(
        f'<article class="card"><header><div class="nm">{e(h["name"])}</div><div class="meta">{e(h.get("desc") or "")}</div></header>{objectives(h["objectives"])}<footer>{src({"name": "OKR（本部）", "url": h["source"]})}</footer></article>'
        for h in okr["hq"]
    )

    # --- 年表・プロダクト・チャンネル・会議 ---
    tl = "".join(
        f'<tr><td class="date">{e(t["date"])}</td><td>{e(t["event"])}'
        + (f'<div class="note">{e(t["note"])}</div>' if t.get("note") else "")
        + f'</td><td>{src(t.get("source"))}</td></tr>'
        for t in timeline["events"]
    )
    pr = "".join(
        f'<tr><td><b>{link(p["url"], p["name"])}</b></td><td>{e(p["what"])}</td><td>{e(p["status"])}</td><td>{link("https://github.com/" + p["repo"], p["repo"]) if p.get("repo") else "—"}</td><td>{src(p.get("source"))}</td></tr>'
        for p in products["products"]
    )
    chs = "".join(
        f'<tr><td>{e(c["kind"])}</td><td>{link(c["url"], c["name"])}</td><td>{e(c.get("what") or "")}</td><td>{src(c.get("source"))}</td></tr>'
        for c in channels["channels"]
    )
    mt = "".join(
        f'<tr><td class="date">{e(x.get("date"))}</td><td>{link(x.get("url"), x.get("title"))}</td><td>{e(x.get("summary"))}</td></tr>' for x in meetings.get("meetings") or []
    ) or '<tr><td colspan="3">まだありません。文字起こしを受け取ったら、要点を追加します。</td></tr>'

    return TEMPLATE.format(
        updated=e(updated),
        summary=e(party["summary"]), summary_src=src(party["summary_source"]),
        nums=nums, nums_src=src(party["numbers"]["source"]), nums_asof=e(party["numbers"]["as_of"]),
        mission="<br>".join(e(x) for x in party["mission"]), vision=vision, values=values, mvv_src=src(party["mvv_source"]),
        cycle_summary=e(party["cycle"]["summary"]), cycle=cycle, cycle_src=src(party["cycle"]["source"]),
        hq_list=hq_list, policy=e(party["member_role_policy"]["summary"]), policy_src=src(party["member_role_policy"]["source"]),
        goals=goals, okr_src=src(okr_src),
        nav_members=" ".join(nav_members), members="".join(cards), members_note=e(members.get("note", "")),
        hq_cards=hq_cards, timeline=tl, products=pr, products_note=e(products.get("note", "")), channels=chs,
        meetings=mt, meetings_how=e(meetings.get("how_to", "")),
    )


TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MiraiBoard — チームみらいを1から知る</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#f6f8f7;--card:#fff;--ink:#1f2a2e;--sub:#5b6b70;--line:#dbe4e1;--accent:#0f9d7a;--tint:#e8f6f1;
--done:#13854f;--ok:#1d6fd1;--warn:#c76b00;--todo:#7a7f85}}
@media (prefers-color-scheme:dark){{:root{{--bg:#12171a;--card:#1b2226;--ink:#e6ecee;--sub:#9fb0b5;--line:#2c373c;--accent:#3cc9a2;--tint:#1d2f2a;
--done:#43c27f;--ok:#5ea2ff;--warn:#f0a040;--todo:#9aa1a7}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.75 "Noto Sans JP",system-ui,sans-serif}}
a{{color:var(--accent)}}
header.top{{padding:28px 16px 8px;max-width:1100px;margin:0 auto}}
header.top h1{{margin:0;font-size:26px}}
header.top p{{margin:4px 0;color:var(--sub)}}
.warn-box{{max-width:1100px;margin:12px auto;padding:12px 16px;border-left:4px solid var(--warn);background:var(--card);border-radius:6px}}
nav.toc{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}}
nav.toc div{{max-width:1100px;margin:0 auto;padding:8px 16px;display:flex;gap:14px;flex-wrap:wrap;font-size:14px}}
main{{max-width:1100px;margin:0 auto;padding:0 16px 48px}}
section{{margin-top:36px}}
h2{{font-size:20px;border-bottom:2px solid var(--accent);padding-bottom:4px}}
h4{{margin:14px 0 4px;font-size:14px;color:var(--sub)}}
.nums{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px}}
.num{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px}}
.num .v{{font-size:20px;font-weight:700}} .num .l{{font-size:12px;color:var(--sub)}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:8px;overflow:hidden}}
td,th{{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top;font-size:14px}}
.table-wrap{{overflow-x:auto}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}}
.card header{{border-bottom:1px solid var(--line);padding-bottom:8px;margin-bottom:8px}}
.nm{{font-size:18px;font-weight:700}} .kana{{font-size:12px;color:var(--sub);margin-left:8px;font-weight:400}}
.meta{{font-size:13px;color:var(--sub)}} .roles{{font-size:13px;font-weight:500;color:var(--accent)}}
.catch{{font-weight:500}}
details summary{{cursor:pointer;color:var(--sub);font-size:13px}}
.prof{{font-size:13px;color:var(--sub)}}
.obj{{margin:8px 0;padding:8px 10px;background:var(--tint);border-radius:6px}}
.obj-h,.goal-h{{font-weight:700}} .obj-d{{margin:2px 0;font-size:13px;color:var(--sub)}}
.lbl{{display:inline-block;font-size:11px;background:var(--accent);color:#fff;border-radius:4px;padding:0 6px;margin-right:6px}}
ul{{padding-left:20px;margin:4px 0}} .krs li,.recent li{{font-size:13px;margin:3px 0}}
.st{{display:inline-block;font-size:11px;border-radius:999px;padding:0 8px;color:#fff;margin-right:4px}}
.st.done{{background:var(--done)}} .st.ok{{background:var(--ok)}} .st.warn{{background:var(--warn)}} .st.todo{{background:var(--todo)}} .st.unk{{background:var(--todo)}}
.prog{{font-size:12px;color:var(--sub)}}
.date{{white-space:nowrap;color:var(--sub);font-size:13px}} .kind{{font-size:11px;color:var(--sub)}}
.ch a{{margin-right:8px}} .unknown{{font-size:12px;color:var(--sub)}}
.src{{font-size:12px;color:var(--sub)}} .src.missing{{color:var(--warn)}}
.card footer{{margin-top:8px;border-top:1px dashed var(--line);padding-top:6px;display:flex;flex-direction:column;gap:2px}}
.goal{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin-bottom:10px}}
.goal p{{margin:4px 0;color:var(--sub);font-size:14px}}
.note{{font-size:12px;color:var(--sub)}}
.legend .st{{margin-right:2px}}
</style>
</head>
<body>
<header class="top">
  <h1>MiraiBoard</h1>
  <p>チームみらいを知らない人が、1から知るための台帳。何を目指し、誰が何に取り組んでいるのかを、公開情報だけで1ページにまとめています。</p>
  <p>最終更新: {updated}</p>
</header>
<div class="warn-box"><b>この台帳について</b><br>
・公開情報だけで作っています。すべての項目に出典を付け、分からないことは「不明」と書いています。<br>
・見えるのは「表に出た動き」だけです。政策づくりの内部の作業や、議員事務所の日々の実務は、ほとんど見えません。この台帳の姿と、現場の実態は同じではありません。<br>
・党の公式なものではありません。正確な情報は、各出典で確かめてください。</div>
<nav class="toc"><div>
<a href="#overview">概要</a><a href="#mvv">ミッション・価値観</a><a href="#structure">体制</a><a href="#goals">党の目標</a><a href="#members">議員12人</a><a href="#hq">本部の目標</a><a href="#timeline">年表</a><a href="#products">プロダクト</a><a href="#channels">発信</a><a href="#meetings">会議の記録</a>
</div></nav>
<main>
<section id="overview"><h2>ひと目でわかるチームみらい</h2>
<p>{summary}</p>{summary_src}
<h4>数字で見る（{nums_asof} 時点）</h4><div class="nums">{nums}</div>{nums_src}
</section>

<section id="mvv"><h2>ミッション・ビジョン・価値観</h2>
<p><b>ミッション</b><br>{mission}</p>
<h4>ビジョン</h4><ul>{vision}</ul>
<h4>価値観（5つのバリュー）</h4><ul>{values}</ul>{mvv_src}
</section>

<section id="structure"><h2>体制</h2>
<p>{cycle_summary}</p>
<div class="table-wrap"><table><tr><th>サイクル</th><th>執行役員</th><th>担当する本部</th></tr>{cycle}</table></div>{cycle_src}
<h4>本部と委員会</h4>
<div class="table-wrap"><table>{hq_list}</table></div>{okr_src}
<h4>党が議員に期待する役割</h4><p>{policy}</p>{policy_src}
</section>

<section id="goals"><h2>党全体の目標（OKR）</h2>
{goals}{okr_src}
</section>

<section id="members"><h2>国会議員 12人</h2>
<p class="note">{members_note}</p>
<p class="legend">OKRの状態: <span class="st done">達成</span><span class="st ok">順調</span><span class="st warn">注意</span><span class="st todo">未着手</span></p>
<p>{nav_members}</p>
<div class="grid">{members}</div>
</section>

<section id="hq"><h2>本部ごとの目標と進み具合</h2>
<div class="grid">{hq_cards}</div>
</section>

<section id="timeline"><h2>年表</h2>
<div class="table-wrap"><table><tr><th>日付</th><th>出来事</th><th>出典</th></tr>{timeline}</table></div>
</section>

<section id="products"><h2>党が作っているプロダクト</h2>
<p class="note">{products_note}</p>
<div class="table-wrap"><table><tr><th>名前</th><th>何をするものか</th><th>状態</th><th>リポジトリ</th><th>出典</th></tr>{products}</table></div>
</section>

<section id="channels"><h2>発信チャンネル</h2>
<div class="table-wrap"><table><tr><th>種類</th><th>名前</th><th>中身</th><th>出典</th></tr>{channels}</table></div>
</section>

<section id="meetings"><h2>会議の記録（まる見えチャンネルなど）</h2>
<p class="note">{meetings_how}</p>
<div class="table-wrap"><table><tr><th>日付</th><th>会議</th><th>決まったこと・決まらなかったこと</th></tr>{meetings}</table></div>
</section>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    out = ROOT / "docs" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"{out.relative_to(ROOT)} を書き出しました")
