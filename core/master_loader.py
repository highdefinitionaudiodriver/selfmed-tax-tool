"""対象成分マスタ (`data/otc_master.json`) のローダー。

`config/medicine_dict/brands.json` の単純な形式と互換性を持たせるため、
新しい構造化マスタを読み込み、既存の `matcher.apply_judgement()` が期待する
`{"brands": [...], "exclude_keywords": [...]}` 形式へ変換するヘルパー。

利用例:
    from pathlib import Path
    from core.master_loader import load_master_as_legacy_dict
    from core.matcher import apply_judgement

    medicine_dict = load_master_as_legacy_dict(Path("data/otc_master.json"))
    df = apply_judgement(df, medicine_dict)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_master(master_path: Path) -> dict[str, Any]:
    """構造化マスタ JSON を生のまま読み込む。

    Args:
        master_path: `data/otc_master.json` などのパス。

    Returns:
        マスタ全体（`_meta`, `active_ingredients`, `exclude_keywords` を含む）。
    """
    with open(master_path, encoding="utf-8") as f:
        return json.load(f)


def flatten_brands(master: dict[str, Any]) -> list[str]:
    """成分カテゴリ → 製品ツリーから、フラットな製品名リストを生成する。

    Args:
        master: `load_master()` の戻り値。

    Returns:
        全製品名の一次元リスト（重複除去・出現順保持）。
    """
    seen: set[str] = set()
    out: list[str] = []
    for ingredient in master.get("active_ingredients", []):
        for product in ingredient.get("products", []):
            if product not in seen:
                seen.add(product)
                out.append(product)
    return out


def load_master_as_legacy_dict(master_path: Path) -> dict[str, Any]:
    """構造化マスタを既存形式 (`brands.json` 互換) に変換して返す。

    既存の `core.matcher.apply_judgement()` をそのまま使えるようにするための
    後方互換アダプタ。

    Args:
        master_path: `data/otc_master.json` のパス。

    Returns:
        `{"brands": [...], "exclude_keywords": [...]}` 形式の辞書。
    """
    master = load_master(master_path)
    return {
        "brands": flatten_brands(master),
        "exclude_keywords": master.get("exclude_keywords", []),
    }


def find_default_master() -> Path | None:
    """プロジェクトルートから `data/otc_master.json` を自動探索する。

    Returns:
        見つかればその Path、見つからなければ None。
    """
    # core/master_loader.py から見て親ディレクトリの data/otc_master.json を期待
    candidate = Path(__file__).resolve().parent.parent / "data" / "otc_master.json"
    if candidate.is_file():
        return candidate
    return None


def get_meta(master: dict[str, Any]) -> dict[str, Any]:
    """マスタのメタ情報（バージョン・更新日・出典）を返す。"""
    return master.get("_meta", {})


def ingredient_for_product(master: dict[str, Any], product_name: str) -> dict[str, Any] | None:
    """製品名から該当する成分カテゴリのエントリを返す。

    判定後の集計・レポート生成で「どの成分カテゴリで合計いくら」を出すために使える。

    Args:
        master: `load_master()` の戻り値。
        product_name: 完全一致で検索する製品名。

    Returns:
        該当する成分エントリ（`name`, `category`, `switch_otc`, `products` 等）。
        見つからなければ None。
    """
    for ingredient in master.get("active_ingredients", []):
        if product_name in ingredient.get("products", []):
            return ingredient
    return None
