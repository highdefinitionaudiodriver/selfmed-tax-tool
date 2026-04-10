# Selfmed Tax Tool (セルフメディケーション税制 明細抽出ツール)

国内の主要通販サイトから出力した購入履歴CSVを読み込み、**セルフメディケーション税制の対象となる市販薬**のみを自動抽出して、確定申告の明細書作成に必要な情報をExcel（xlsx）形式で出力するCLIツールです。

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-blue)
![Privacy](https://img.shields.io/badge/privacy-local--only-green)
![Tests](https://img.shields.io/badge/tests-30%20passed-brightgreen)
![Sites](https://img.shields.io/badge/sites-13%20supported-orange)

---

## 特徴

- **完全ローカル処理** — 購入履歴という個人情報を外部APIに一切送信せず、すべてローカル環境で処理
- **国内主要13サイトに対応** — Amazon・楽天・Yahoo!・LOHACO・ヨドバシなどの総合通販から、マツキヨ・ウエルシアなど大手ドラッグストアECまで標準同梱
- **3段階判定** — 「対象 / 要確認 / 対象外」で自動分類。Human-in-the-loop での最終確認を前提とした安全設計
- **拡張しやすい設計** — カラムマッピングと医薬品辞書を外部JSONに分離。コードを触らずに新しいECサイトや新薬に対応可能
- **確定申告向け出力** — 国税庁の明細書フォーマットに転記しやすい項目構成（支払先 / 医薬品名 / 金額 / 購入日 / 判定）
- **要確認行のハイライト** — 除外キーワードに引っかかった商品はxlsx上で黄色表示

## 対応通販サイト

標準で以下の13サイトのプロファイルを同梱しています。`--site` オプションで切り替えて使用します。

### 総合通販系

| サイトキー | 表示名 | 備考 |
|---|---|---|
| `amazon` | Amazon.co.jp | Chrome拡張「Amazon注文履歴フィルタ」等でのCSV出力を想定 |
| `rakuten` | 楽天市場 | 注文履歴の「注文履歴ダウンロード」機能を想定 |
| `yahoo_shopping` | Yahoo!ショッピング | 購入履歴CSV（旧PayPayモール含む） |
| `lohaco` | LOHACO (ASKUL) | OTC医薬品の取り扱いが非常に多い |
| `aupay_market` | au PAY マーケット | 旧Wowma |
| `yodobashi` | ヨドバシ.com | 医薬品カテゴリ取扱あり |
| `qoo10` | Qoo10 | |

### ドラッグストアEC系

| サイトキー | 表示名 | 備考 |
|---|---|---|
| `matsukiyo` | マツモトキヨシ | マツキヨオンラインストア |
| `welcia` | ウエルシア | ウエルシアドットコム |
| `sundrug` | サンドラッグ | サンドラッグe-shop |
| `tsuruha` | ツルハドラッグ | ツルハグループe-shop |
| `kokokara` | ココカラファイン | ココカラクラブ |
| `sugi` | スギ薬局 | スギ薬局オンラインショップ |

> **重要**: 各サイトのCSVカラム名は一般的な命名を前提としたデフォルト値です。実際にダウンロードしたCSVのヘッダー行と異なる場合は、`config/site_profiles/<サイトキー>.json` の `columns` セクションを編集してください（[カスタマイズ](#カスタマイズ)参照）。

対応サイト一覧は以下のコマンドでも確認できます:

```bash
python main.py --list-sites
```

## 出力イメージ

```
┌──────────────┬────────────────────────┬──────────┬────────────┬────────┐
│ 支払先の名称  │ 医薬品の名称            │ 支払った  │ 購入日      │ 判定   │
│              │                        │ 金額     │            │        │
├──────────────┼────────────────────────┼──────────┼────────────┼────────┤
│ Amazon       │ ロキソニンS 12錠        │      698 │ 2025-03-15 │ 対象   │
│ 楽天市場      │ パブロンゴールドA 44錠  │    1,280 │ 2025-06-02 │ 対象   │
│ LOHACO       │ アレグラFX 28錠         │    1,980 │ 2025-09-01 │ 対象   │
│ マツモトキヨシ│ バファリンEXルナ 20錠   │      980 │ 2025-11-10 │ 要確認 │
│ Amazon       │ チョコラBBプラス 60錠   │    1,580 │ 2025-11-05 │ 対象   │
├──────────────┼────────────────────────┼──────────┼────────────┼────────┤
│              │                  合計  │    6,518 │            │        │
└──────────────┴────────────────────────┴──────────┴────────────┴────────┘
```

## セットアップ

### 前提

- Python 3.10 以上
- pip

### インストール手順

```bash
# リポジトリをクローン（または zip をダウンロードして展開）
cd selfmed-tax-tool

# 依存ライブラリのインストール
pip install -r requirements.txt
```

依存は `pandas` と `openpyxl` の2つだけ。どちらも外部API通信を必要としません。

## 使い方

### 基本（Amazonの場合）

```bash
python main.py --input amazon_history.csv
```

`--site` を省略するとデフォルトで `amazon` が使われます。

### サイトを指定

```bash
# 楽天市場
python main.py --input rakuten_history.csv --site rakuten

# Yahoo!ショッピング
python main.py --input yahoo_history.csv --site yahoo_shopping

# LOHACO
python main.py --input lohaco_history.csv --site lohaco

# マツモトキヨシ
python main.py --input matsukiyo_history.csv --site matsukiyo
```

### 年度でフィルタ

```bash
python main.py --input 注文履歴.csv --site rakuten --year 2025
```

### 出力先を指定

```bash
python main.py --input 注文履歴.csv --year 2025 --output 令和7年_セルメ明細.xlsx
```

### 対応サイト一覧を表示

```bash
python main.py --list-sites
```

### 複数サイトを合算したい場合

複数サイトを一度の実行で合算する機能は搭載していませんが、以下のワークフローで対応できます:

```bash
# サイトごとに個別に出力
python main.py --input amazon_2025.csv --site amazon --year 2025 --output out_amazon.xlsx
python main.py --input rakuten_2025.csv --site rakuten --year 2025 --output out_rakuten.xlsx
python main.py --input lohaco_2025.csv --site lohaco --year 2025 --output out_lohaco.xlsx

# Excel上で3ファイルをコピー＆ペーストして統合
```

将来的にマージ機能を追加する予定です。

### CLIオプション

| オプション | 短縮 | 必須 | 説明 |
|---|---|---|---|
| `--input` | `-i` | ○ | 入力CSVファイルのパス |
| `--site` | `-s` | | ECサイト種別（デフォルト: `amazon`） |
| `--year` | `-y` | | 対象年でフィルタ（省略時: フィルタなし） |
| `--output` | `-o` | | 出力xlsxパス（デフォルト: `selfmed_result.xlsx`） |
| `--list-sites` | | | 対応サイト一覧を表示して終了 |

### 実行例

```
$ python main.py --input rakuten_2025.csv --site rakuten --year 2025
読み込み中: rakuten_2025.csv
  → 128 件の注文を読み込みました
  → 2025年の注文: 89 件
  → 対象: 12 件 / 要確認: 2 件

出力完了: selfmed_result.xlsx
合計金額: 15,240円

※ 「要確認」が 2 件あります。出力ファイルの黄色行を確認してください。
```

## 各サイトのCSV取得方法

### Amazon.co.jp

Amazonは現在、公式機能での注文履歴CSV出力を廃止しています。以下のChrome拡張機能の利用を推奨します。

- **Amazon注文履歴フィルタ** — Chrome拡張として提供。購入履歴をCSV形式でエクスポート可能

### 楽天市場

「購入履歴」ページに注文履歴ダウンロード機能があります。年度を指定してCSVを取得してください。

### Yahoo!ショッピング / PayPayモール

「注文履歴」から該当期間の購入履歴をCSVでエクスポートできます（PayPayモールは2022年にYahoo!ショッピングと統合されたため、同じサイトプロファイルで対応可能です）。

### LOHACO

会員ページの注文履歴からCSVエクスポート可能。OTC医薬品の取り扱いが多いため、セルフメディケーション税制の明細作成に特に有用です。

### ドラッグストア系EC

マツキヨ・ウエルシア等のドラッグストアECは、サイトによってはCSV出力機能が提供されていない場合があります。その場合は、注文履歴画面から手動でCSVを作成する（または表をコピーしてExcel → CSVとして保存する）といった運用が必要です。

> **補足**: いずれのサイトも、ダウンロードしたCSVのカラム名が本ツールのデフォルト定義と異なる場合は、`config/site_profiles/<サイトキー>.json` を編集してください。

## ファイル構成

```
selfmed-tax-tool/
├── main.py                         # CLIエントリポイント
├── requirements.txt                # pandas, openpyxl
├── README.md                       # 本ドキュメント
├── config/
│   ├── site_profiles/
│   │   ├── _template.json          # 新規サイト追加用テンプレート
│   │   ├── amazon.json             # Amazon.co.jp
│   │   ├── rakuten.json            # 楽天市場
│   │   ├── yahoo_shopping.json     # Yahoo!ショッピング
│   │   ├── lohaco.json             # LOHACO
│   │   ├── aupay_market.json       # au PAY マーケット
│   │   ├── yodobashi.json          # ヨドバシ.com
│   │   ├── qoo10.json              # Qoo10
│   │   ├── matsukiyo.json          # マツモトキヨシ
│   │   ├── welcia.json             # ウエルシア
│   │   ├── sundrug.json            # サンドラッグ
│   │   ├── tsuruha.json            # ツルハドラッグ
│   │   ├── kokokara.json           # ココカラファイン
│   │   └── sugi.json               # スギ薬局
│   └── medicine_dict/
│       └── brands.json             # 対象ブランド辞書 + 除外キーワード
├── core/
│   ├── __init__.py
│   ├── loader.py                   # CSV読み込み・正規化
│   ├── matcher.py                  # 3段階判定ロジック
│   └── exporter.py                 # xlsx出力（書式付き）
└── tests/
    ├── test_loader.py              # 12 tests
    ├── test_matcher.py             # 11 tests
    ├── test_exporter.py            # 7 tests
    └── fixtures/
        └── amazon_sample.csv       # テスト用サンプルCSV
```

## カスタマイズ

### 対象医薬品ブランドの追加・除外キーワードの編集

`config/medicine_dict/brands.json` を編集することで、コードに一切触れずに辞書を更新できます:

```json
{
  "brands": [
    "ロキソニンS",
    "パブロンゴールドA",
    "あなたが追加したい新ブランド"
  ],
  "exclude_keywords": [
    "ルナ",
    "キッズ",
    "ジュニア",
    "除外したい新キーワード"
  ]
}
```

- **brands** に含まれるブランド名が商品名に部分一致すれば「対象」
- ただし **exclude_keywords** のいずれかが同時に含まれる場合は「要確認」に降格
- どちらにも該当しない商品は「対象外」として出力から除外

### CSVカラム名のマッピング変更

各サイトの実際のCSVに合わせて `config/site_profiles/<サイトキー>.json` を編集します。例えば楽天市場:

```json
{
  "_comment": "楽天市場の購入履歴CSV用プロファイル",
  "display_name": "楽天市場",
  "encoding": "utf-8",
  "columns": {
    "order_date": "注文日",
    "product_name": "商品名",
    "unit_price": "商品価格",
    "quantity": "数量",
    "seller": "店舗名"
  },
  "default_seller": "楽天市場",
  "date_format": "%Y-%m-%d"
}
```

**設定項目の説明**:

| キー | 説明 |
|---|---|
| `_comment` | 任意のコメント（プログラムは無視） |
| `display_name` | `--list-sites` で表示される名称 |
| `encoding` | CSVの文字エンコーディング（`utf-8` / `shift_jis` / `cp932` 等） |
| `columns.order_date` | 注文日カラムの**実際のヘッダー名** |
| `columns.product_name` | 商品名カラムの実際のヘッダー名 |
| `columns.unit_price` | 金額カラムの実際のヘッダー名 |
| `columns.quantity` | 数量カラムの実際のヘッダー名（任意） |
| `columns.seller` | 販売元カラムの実際のヘッダー名（任意。無ければ行ごと削除） |
| `default_seller` | `seller` カラムが無い場合の支払先名 |
| `date_format` | 日付のフォーマット文字列（`%Y/%m/%d` 等） |

### 新しいECサイトへの対応

`config/site_profiles/_template.json` をコピーして新しいサイト名で保存し、`columns` を実際のCSVヘッダーに合わせるだけです:

```bash
cp config/site_profiles/_template.json config/site_profiles/mysite.json
# mysite.json を編集...
python main.py --input mysite_history.csv --site mysite
```

Pythonコードの変更は一切不要です。

## 判定ロジック

```
1. 商品名を正規化（NFKC正規化: 全角英数→半角、スペース統一、小文字化）
2. brands内の各ブランド名と部分一致をチェック
   ├─ マッチ → exclude_keywordsをチェック
   │   ├─ 除外ワードあり → 「要確認」
   │   └─ 除外ワードなし → 「対象」
   └─ マッチせず → 「対象外」（出力から除外）
```

「要確認」と判定された行はxlsx出力で **黄色（#FFF2CC）** にハイライトされます。必ず目視確認の上、実際の商品がセルフメディケーション税制対象かを最終判断してください。

## セキュリティとプライバシー

本ツールは個人のプライバシーに関わる購入履歴を扱うため、以下の方針で設計されています:

| 項目 | 方針 |
|---|---|
| 外部API通信 | **一切なし** — LLMへのデータ送信や外部サーバーへの問い合わせは行いません |
| データ保存 | 入力CSVと出力xlsxは**すべてローカルファイルシステム**にのみ存在 |
| 依存ライブラリ | `pandas` / `openpyxl` のみ。どちらも純粋なデータ処理ライブラリ |
| ネットワーク | ツール実行中、ネットワーク通信は発生しません |

オフライン環境でも完全に動作します。

## テスト

```bash
# 全テスト実行
python -m pytest tests/ -v

# モジュール単位で実行
python -m pytest tests/test_loader.py -v
python -m pytest tests/test_matcher.py -v
python -m pytest tests/test_exporter.py -v
```

現在 **30テスト** がパスしています（loader: 12 / matcher: 11 / exporter: 7）。

## テクノロジースタック

- **Python 3.10+** — メイン言語
- **pandas** — CSV読み込み・データ加工
- **openpyxl** — xlsx出力・書式設定（セル色・列幅・数値フォーマット）
- **argparse** — CLIインターフェース（標準ライブラリ）
- **unicodedata** — NFKC正規化による商品名の揺らぎ吸収（標準ライブラリ）
- **pytest** — ユニットテスト

## ロードマップ

- [x] Amazon対応
- [x] 楽天・Yahoo!・LOHACO等 総合通販サイト対応
- [x] マツキヨ・ウエルシア等 ドラッグストアEC対応
- [x] `--list-sites` オプション
- [ ] 複数サイトCSVの一括マージ機能
- [ ] 厚労省公式品目リストの自動取り込みスクリプト
- [ ] GUI版（tkinter or PySide6）

## 免責事項

- 本ツールが出力する判定結果は **あくまで補助** です。最終的なセルフメディケーション税制対象かどうかの判断は、厚生労働省の公式対象品目リストおよび商品パッケージの「セルフメディケーション税控除対象」マークをご確認ください
- 各サイトのCSV仕様は予告なく変更される可能性があります。デフォルトプロファイルが実際のCSVと合わない場合は `config/site_profiles/` 配下のJSONを編集してください
- 確定申告書類の作成責任は利用者自身にあります
- 本ツールの使用によって生じたいかなる損害についても、作者は責任を負いません

## ライセンス

MIT License
