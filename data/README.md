# data/ — 対象成分マスタ（独立データ層）

セルフメディケーション税制の判定に使う **対象成分・製品マスタ** を独立した
データ層として配置するディレクトリです。

判定ロジックの実装（`core/matcher.py`）からデータを切り離すことで、
**コード変更なしでマスタ更新が完結する**構造になっています。

---

## ファイル

| ファイル | 用途 |
|---|---|
| `otc_master.json` | 成分カテゴリ別の対象 OTC 製品マスタ（メタデータ＋成分→製品ツリー） |

---

## `otc_master.json` のスキーマ

```jsonc
{
  "_meta": {
    "schema_version": "1.0",
    "data_version": "2026.01",          // 年次更新の識別子
    "data_year": 2026,
    "updated_at": "2026-05-19",
    "source_notes": [ ... ],            // データ出典の透明性
    "year_subscription_note": "..."     // 年次更新の有償提供方針
  },

  "active_ingredients": [               // 成分カテゴリ × 製品の入れ子構造
    {
      "name": "ロキソプロフェン",
      "category": "解熱鎮痛剤",
      "switch_otc": true,               // スイッチ OTC か（税制対象判定の根拠の一つ）
      "products": [
        "ロキソニンS",
        "ロキソニンSプラス",
        ...
      ]
    }
  ],

  "exclude_keywords": [ "キッズ", "小児用", ... ]
}
```

### 既存 `config/medicine_dict/brands.json` との互換性

既存の単純な `{"brands": [...], "exclude_keywords": [...]}` 形式から、
**全製品名をフラットに引き出した同等の brands リスト** を以下で生成できます：

```python
import json

with open("data/otc_master.json", encoding="utf-8") as f:
    master = json.load(f)

brands = [
    product
    for ingredient in master["active_ingredients"]
    for product in ingredient["products"]
]
exclude_keywords = master["exclude_keywords"]
```

`core/loader.py` などのローダー層に同等のヘルパー関数を追加することで、
既存判定ロジックを変更せず移行できます（後方互換）。

---

## 年次更新ポリシー

セルフメディケーション税制の対象品目は、毎年厚生労働省の告示で微変動します。
本ツールでは：

- **年次更新**：原則として年 1 回（1 月、確定申告シーズン前）更新
- **データバージョン**：`_meta.data_version` を `YYYY.MM` 形式で記録
- **無償**：本リポジトリ内の `data/otc_master.json` は **常に最新版を MIT で公開**
- **有償オプション**：「正本マスタ＋年次ニュースレター」を以下の価格帯で検討中
  - 個人向け：年 ¥500 程度
  - 税理士・薬局向け：年 ¥2,400 程度
  - 法人 / マスメディア利用：応相談

> ⚠️ **重要**：本マスタは公開情報を編集者がまとめたものです。確定申告時には
> 必ず最新の国税庁・厚生労働省公示と照合してください。誤判定による損害について
> 作成者は責任を負いません。

---

## カスタマイズ・追加成分の要望

業界・地域特化の判定（例：特定地域の薬局で多く取り扱われる製品、海外在住者向けの
対応など）が必要な場合は応相談です。

- 連絡先：highdefinitionaudiodriver@gmail.com
