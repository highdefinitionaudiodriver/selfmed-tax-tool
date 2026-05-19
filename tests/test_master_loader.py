"""data/otc_master.json と core.master_loader のテスト。

新しい構造化マスタが既存判定ロジックと整合することを検証する。
"""

from __future__ import annotations

import pandas as pd
import pytest

from core.master_loader import (
    find_default_master,
    flatten_brands,
    get_meta,
    ingredient_for_product,
    load_master,
    load_master_as_legacy_dict,
)
from core.matcher import apply_judgement


def test_default_master_exists():
    """プロジェクトルートに data/otc_master.json が存在する"""
    p = find_default_master()
    assert p is not None
    assert p.is_file()


def test_master_has_required_fields():
    """マスタが期待するキーを全て持つ"""
    master = load_master(find_default_master())
    assert "_meta" in master
    assert "active_ingredients" in master
    assert "exclude_keywords" in master
    assert isinstance(master["active_ingredients"], list)
    assert len(master["active_ingredients"]) > 0


def test_meta_has_versioning():
    """年次更新で売るための meta フィールドが揃っている"""
    master = load_master(find_default_master())
    meta = get_meta(master)
    assert "schema_version" in meta
    assert "data_version" in meta
    assert "data_year" in meta
    assert "updated_at" in meta


def test_flatten_brands_no_duplicates():
    """成分ツリーから flatten した brands に重複がない"""
    master = load_master(find_default_master())
    brands = flatten_brands(master)
    assert len(brands) == len(set(brands))


def test_legacy_format_compatible():
    """既存 brands.json 形式と互換性のある辞書を返す"""
    legacy = load_master_as_legacy_dict(find_default_master())
    assert "brands" in legacy
    assert "exclude_keywords" in legacy
    assert isinstance(legacy["brands"], list)
    assert isinstance(legacy["exclude_keywords"], list)


def test_apply_judgement_with_new_master():
    """新マスタを既存 apply_judgement に渡しても動作する"""
    medicine_dict = load_master_as_legacy_dict(find_default_master())
    df = pd.DataFrame({
        "product_name": ["ロキソニンS 12錠", "ガスター10", "シャンプー", "ロキソニンS ルナ"],
    })
    result = apply_judgement(df, medicine_dict)
    # 「対象外」のシャンプーは除外され、それ以外の 3 行が残る
    assert len(result) == 3
    # 通常の医薬品は「対象」
    assert result.loc[result["product_name"] == "ロキソニンS 12錠", "判定"].iloc[0] == "対象"
    assert result.loc[result["product_name"] == "ガスター10", "判定"].iloc[0] == "対象"
    # 「ルナ」を含むものは exclude_keyword により「要確認」
    assert result.loc[result["product_name"] == "ロキソニンS ルナ", "判定"].iloc[0] == "要確認"


def test_ingredient_for_product_lookup():
    """製品名から成分カテゴリを引ける（集計レポート用）"""
    master = load_master(find_default_master())
    ing = ingredient_for_product(master, "ロキソニンS")
    assert ing is not None
    assert ing["name"] == "ロキソプロフェン"
    assert ing["category"] == "解熱鎮痛剤"

    # 存在しない製品
    assert ingredient_for_product(master, "存在しない医薬品X") is None
