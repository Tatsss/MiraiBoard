# MiraiBoard

チームみらいを知らない人が、1から知るための台帳です。
党が何を目指し、どんな体制で、12人の国会議員がそれぞれ何に取り組んでいるのかを、**公開情報だけ**で1ページにまとめています。

- ページ: `docs/`（GitHub Pages で `main` ブランチの `/docs` を公開すると、そのまま見られます）
- 議員の顔写真は、公式サイトの画像をそのURLから表示しています（このリポジトリには保存していません）
- 党の公式なものではありません。正確な情報は、各出典で確かめてください

## ページ

| ページ | 中身 |
|---|---|
| 概要（index.html） | 数字、党の仕事の4段階を表したリング図（目標1つずつの状態つき）、「声が政策になるまで」の流れ図 |
| 政策づくりの現場（flow.html） | 部署×段階の目標の地図、12議員室の目標の地図、段階ごとの説明（担当・道具・分かっていること・GitHub の課題・見えないこと）、注意・未着手の目標 |
| 議員12人（people.html） | 写真、役職、議員室の目標の状態、国会での質疑・発言の数、一人ずつの詳細 |
| 体制と目標（org.html） | 党首と4人の執行役員と本部の図、党全体の目標、本部ごとの目標 |
| 年表（timeline.html） | 節目の時間軸、公式サイトのお知らせ全件（種類・議員で絞り込み） |
| 理念・求人・出典（more.html） | ミッション・バリュー・ビジョン、プロダクト、発信チャンネル、会議の記録、公開求人、出典の一覧 |

## 決まりごと

1. **公開情報だけ**を使う。すべての行に出典（URL か出典名）と確認日を付ける
2. 公式サイトやOKRに書かれていない肩書・役割は付けない。推測は書かない
3. 分からないことは空欄にせず「不明」、出典が見つからないものは「出典未確認」と書く
4. 見えるのは「表に出た動き」だけ。内部の作業や事務所の実務は見えない、という前提をページの冒頭に書く
5. 動画の文字起こしは、要点（誰が・何を決めた／決めなかったか）だけを `data/meetings.yaml` に足す。全文はこのリポジトリに置かない。文字起こしにない発言は補わない

## 更新のしかた

```bash
# 1. 公開OKRを取り込む（党が更新したとき）
git clone --depth 1 https://github.com/team-mirai/okr-content /tmp/okr-content
python3 scripts/import_okr.py /tmp/okr-content

# 2. 公式サイトのお知らせ一覧を取り込む
python3 scripts/import_news.py https://team-mir.ai/news/all

# 3. data/*.yaml を手で直す（議員の直近の動き、年表、会議の記録など）

# 4. ページを作り直す（site/ と data/ から docs/ を作る）
python3 scripts/build.py
```

必要なもの: Python 3.11 以上、PyYAML

## ファイル

```
data/
  party.yaml      党の概要・ミッション・体制・数字
  members.yaml    国会議員12人（公式サイトの国会議員団が正本）
  timeline.yaml   年表
  products.yaml   プロダクト
  channels.yaml   発信チャンネル
  meetings.yaml   会議の記録（文字起こしの要点）
  process.yaml    政策づくりと広聴の流れ（段階ごとの担当・道具・課題）
  jobs.yaml       公開されている求人
  okr/*.json      公開OKRの要約（scripts/import_okr.py が作る）
  news.json       公式サイトのお知らせ一覧（scripts/import_news.py が作る）
scripts/
  import_okr.py   公開OKRの取り込み
  import_news.py  お知らせ一覧の取り込み
  build.py        site/ と data/ から docs/ を作る
site/             ページの元（HTML と assets/style.css・common.js）
docs/             公開用（build.py が作る。直接は編集しない）
```
