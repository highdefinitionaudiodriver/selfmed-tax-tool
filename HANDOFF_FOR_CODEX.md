# Codex / Claude Code 引き継ぎメモ

## 対象

- リポジトリ: `selfmed-tax-tool`
- 作業元: `C:\Users\highd\Documents\Github\selfmed-tax-tool`
- 同期先: `G:\マイドライブ\claudecode\selfmed-tax-tool`

## 2026-05-26 Codex作業ログ

### セットアップ診断CLIを追加

ユーザーや `tax-toolkit` 連携時に、CSVサイトプロファイルと医薬品マスタが壊れていないかをGUIなしで確認できる `tools/check_setup.py` を追加しました。

確認内容:

- `config/site_profiles/*.json`
  - JSON構文
  - `columns.order_date`, `columns.product_name`, `columns.unit_price`
  - `encoding`
- `config/medicine_dict/brands.json`
  - `brands` が空でないこと
  - `exclude_keywords` の型
- `data/otc_master.json`
  - `_meta.schema_version`, `_meta.data_version`, `_meta.updated_at`, `_meta.scope`
  - `active_ingredients[].name/category/products`
  - 製品名重複

README のテスト節に以下を追記しました。

```bash
python tools/check_setup.py
```

## 検証

```powershell
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile main.py tools\check_setup.py
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\check_setup.py
```

`pytest` はこの実行環境のバンドルPythonに未導入だったため未実行です（`No module named pytest`）。既存テストを回す場合は、`pip install pytest pandas openpyxl` 済みのPython環境で `python -m pytest tests` を実行してください。

## 次にやるとよいこと

1. `tools/check_setup.py --json` を追加し、`tax-toolkit` から機械的に診断結果を読めるようにする。
2. `--sample-csv <path> --site <key>` を追加し、実CSVとサイトプロファイルの整合性まで確認する。
3. `data/otc_master.json` と `config/medicine_dict/brands.json` の差分レポートを出す。
