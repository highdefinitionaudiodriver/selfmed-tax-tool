# Selfmed Tax Tool (セルフメディケーション税制 明細抽出ツール)

ECサイトの購入履歴CSVから、**セルフメディケーション税制の対象となる市販薬**のみを自動抽出し、確定申告の明細書作成に必要な情報をExcel（xlsx）形式で出力するCLIツールです。

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-blue)
![Privacy](https://img.shields.io/badge/privacy-local--only-green)
![Tests](https://img.shields.io/badge/tests-30%20passed-brightgreen)

---

## 特徴

- **完全ローカル処理** — 購入履歴という個人情報を外部APIに一切送信せず、すべてローカル環境で処理
- **3段階判定** — 「対象 / 要確認 / 対象外」で自動分類。Human-in-the-loop での最終確認を前提とした安全設計
- **拡張しやすい設計** — カラムマッピングと医薬品辞書を外部JSONに分離。コードを触らずに新しいECサイトや新薬に対応可能
- **確定申告向け出力** — 国税庁の明細書フォーマットに転記しやすい項目構成（支払先 / 医薬品名 / 金額 / 購入日 / 判定）
- **要確認行のハイライト** — 除外キーワードに引っかかった商品はxlsx上で黄色表示

## 出力イメージ

```
┌──────────────┬────────────────────────┬──────────┬────────────┬────────┐
│ 支払先の名称  │ 医薬品の名称            │ 支払った  │ 購入日      │ 判定   │
│              │                        │ 金額     │            │        │
├──────────────┼────────────────────────┼──────────┼────────────┼────────┤
│ Amazon       │ ロキソニンS 12錠        │      698 │ 2025-03-15 │ 対象   │
│ Amazon       │ パブロンゴールドA 44錠  │    1,280 │ 2025-06-02 │ 対象   │
│ Amazon       │ チョコラBBプラス 60錠   │    1,580 │ 2025-11-05 │ 対象   │
│ ヘルスケア... │ アレグラFX 28錠         │    1,980 │ 2025-09-01 │ 対象   │
├──────────────┼────────────────────────┼──────────┼────────────┼────────┤
│              │                  合計  │    5,538 │            │        │
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

### 基本

```bash
python main.py --input 注文履歴.csv
```

### 年度でフィルタ

```bash
python main.py --input 注文履歴.csv --year 2025
```

### 出力先を指定

```bash
python main.py --input 注文履歴.csv --year 2025 --output 令和7年_セルメ明細.xlsx
```

### CLIオプション

| オプション | 短縮 | 必須 | 説明 |
|---|---|---|---|
| `--input` | `-i` | ○ | 入力CSVファイルのパス |
| `--site` | `-s` | | ECサイト種別（デフォルト: `amazon`） |
| `--year` | `-y` | | 対象年でフィルタ（省略時: フィルタなし） |
| `--output` | `-o` | | 出力xlsxパス（デフォルト: `selfmed_result.xlsx`） |

### 実行例

```
$ python main.py --input 注文履歴.csv --year 2025
読み込み中: 注文履歴.csv
  → 128 件の注文を読み込みました
  → 2025年の注文: 89 件
  → 対象: 12 件 / 要確認: 2 件

出力完了: selfmed_result.xlsx
合計金額: 15,240円

※ 「要確認」が 2 件あります。出力ファイルの黄色行を確認してください。
```

## Amazon CSVの取得方法

Amazonは現在、公式機能での注文履歴CSV出力を廃止しています。以下のChrome拡張機能の利用を推奨します。

- **Amazon注文履歴フィルタ** — Chrome拡張機能として提供。購入履歴をCSV形式でエクスポート可能

ダウンロードしたCSVのカラム名が本ツールのデフォルト（`注文日 / 商品名 / 商品小計 / 数量 / 販売元`）と異なる場合は、`config/site_profiles/amazon.json` を編集してください（後述）。

## ファイル構成

```
selfmed-tax-tool/
├── main.py                         # CLIエントリポイント
├── requirements.txt                # pandas, openpyxl
├── README.md                       # 本ドキュメント
├── config/
│   ├── site_profiles/
│   │   └── amazon.json             # Amazonカラムマッピング定義
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
    "あなたが追加したい新ブランド",
    ...
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

実際のAmazon CSV（拡張機能によってカラム名が異なります）に合わせて `config/site_profiles/amazon.json` を編集:

```json
{
  "encoding": "utf-8",
  "columns": {
    "order_date": "注文日",        ← 実CSVの日付カラム名に合わせる
    "product_name": "商品名",      ← 商品名カラム
    "unit_price": "商品小計",      ← 金額カラム
    "quantity": "数量",
    "seller": "販売元"
  },
  "default_seller": "Amazon",
  "date_format": "%Y-%m-%d"
}
```

### 新しいECサイトへの対応（例: 楽天）

`config/site_profiles/rakuten.json` を新規作成するだけで、楽天の購入履歴CSVにも対応できます:

```bash
python main.py --input 楽天購入履歴.csv --site rakuten
```

コードの修正は一切不要です。

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

## 免責事項

- 本ツールが出力する判定結果は **あくまで補助** です。最終的なセルフメディケーション税制対象かどうかの判断は、厚生労働省の公式対象品目リストおよび商品パッケージの「セルフメディケーション税控除対象」マークをご確認ください
- 確定申告書類の作成責任は利用者自身にあります
- 本ツールの使用によって生じたいかなる損害についても、作者は責任を負いません

## ライセンス

MIT License
