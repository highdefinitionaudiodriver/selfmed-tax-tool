# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- README に「これは何？（30秒で）」「想定ユースケース・価格帯」セクションを追加
- SECURITY.md を追加（脆弱性報告フロー）
- 商用利用・カスタマイズ依頼の連絡先を README 末尾に明記
- **data/otc_master.json** — 対象成分マスタを独立データ層として切り出し
  - 成分カテゴリ（20 種）× 製品（56 製品）の入れ子構造
  - `_meta.data_version` で年次更新識別（年次更新版を有償提供する基盤）
  - `switch_otc` フラグ、カテゴリ、出典メモなどメタデータ充実
- **core/master_loader.py** — 新マスタを既存 brands.json 形式に変換するアダプタ
  - `load_master_as_legacy_dict()` で後方互換維持（matcher.py の変更不要）
  - `ingredient_for_product()` で製品 → 成分カテゴリ逆引き（レポート集計用）
- tests/test_master_loader.py（7 件）追加 — 38 件全て通過

## [0.1.0]

### Added
- 初版リリース
