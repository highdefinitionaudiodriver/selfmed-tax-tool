"""matcher.py のユニットテスト。"""

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.matcher import normalize_text, judge_product, apply_judgement, load_medicine_dict

DICT_PATH = PROJECT_ROOT / "config" / "medicine_dict" / "brands.json"

BRANDS = ["ロキソニンS", "パブロンゴールドA", "アレグラFX", "バファリンEX"]
EXCLUDES = ["ルナ", "キッズ", "ジュニア"]


class TestNormalizeText:
    def test_fullwidth_to_halfwidth(self):
        assert normalize_text("ＡＢＣ１２３") == "abc123"

    def test_spaces_unified(self):
        assert normalize_text("ロキソニン  S　12錠") == "ロキソニン s 12錠"

    def test_strip(self):
        assert normalize_text("  テスト  ") == "テスト"


class TestJudgeProduct:
    def test_exact_match(self):
        assert judge_product("ロキソニンS 12錠", BRANDS, EXCLUDES) == "対象"

    def test_brand_with_extra_text(self):
        assert judge_product("【まとめ買い】パブロンゴールドA 44錠 x2", BRANDS, EXCLUDES) == "対象"

    def test_no_match(self):
        assert judge_product("プログラミング入門書", BRANDS, EXCLUDES) == "対象外"

    def test_exclude_keyword_triggers_review(self):
        assert judge_product("バファリンEXルナ 20錠", BRANDS, EXCLUDES) == "要確認"

    def test_exclude_keyword_kids(self):
        assert judge_product("パブロンゴールドA キッズ", BRANDS, EXCLUDES) == "要確認"

    def test_fullwidth_brand_match(self):
        # 全角英数でも正規化によりマッチする
        assert judge_product("アレグラＦＸ 28錠", BRANDS, EXCLUDES) == "対象"


class TestApplyJudgement:
    def test_filters_out_non_target(self):
        df = pd.DataFrame({
            "product_name": [
                "ロキソニンS 12錠",
                "プログラミング入門書",
                "パブロンゴールドA キッズ",
                "USB-Cケーブル",
            ],
            "order_date": pd.to_datetime(["2025-01-01"] * 4),
            "unit_price": [698, 2500, 1280, 899],
            "quantity": [1, 1, 1, 1],
            "seller": ["Amazon"] * 4,
        })
        medicine_dict = {"brands": BRANDS, "exclude_keywords": EXCLUDES}
        result = apply_judgement(df, medicine_dict)

        # 「対象外」は除外されるので、2行（対象 + 要確認）のみ残る
        assert len(result) == 2
        assert list(result["判定"]) == ["対象", "要確認"]

    def test_loads_real_dict(self):
        medicine_dict = load_medicine_dict(DICT_PATH)
        assert "brands" in medicine_dict
        assert len(medicine_dict["brands"]) > 0
