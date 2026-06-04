"""同梱サイトプロファイル(JSON)の整合性テストと loader の追加検証.

13 サイト分のプロファイルが壊れる/必須マッピングが欠けると、その EC サイトの
CSV 取り込みが実行時に失敗する。設定ドリフトを CI で検出できるよう、全プロファ
イルが規約に適合することを検証する。
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.loader import load_site_profile, load_csv, filter_by_year, UNIFIED_COLUMNS

PROFILE_DIR = PROJECT_ROOT / "config" / "site_profiles"

# loader が CSV から最低限マッピングできる必要のある内部カラム名
REQUIRED_INTERNAL = {"order_date", "product_name", "unit_price"}

# _template.json は雛形なので実プロファイルから除外
PROFILE_PATHS = sorted(p for p in PROFILE_DIR.glob("*.json") if p.name != "_template.json")
PROFILE_IDS = [p.stem for p in PROFILE_PATHS]


def test_profiles_exist():
    assert PROFILE_PATHS, "サイトプロファイルが1つも見つかりません"


@pytest.mark.parametrize("profile_path", PROFILE_PATHS, ids=PROFILE_IDS)
class TestEachProfile:
    def test_is_valid_json(self, profile_path):
        profile = load_site_profile(profile_path)
        assert isinstance(profile, dict)

    def test_has_columns_mapping(self, profile_path):
        profile = load_site_profile(profile_path)
        assert isinstance(profile.get("columns"), dict) and profile["columns"]

    def test_maps_required_internal_columns(self, profile_path):
        profile = load_site_profile(profile_path)
        keys = set(profile["columns"].keys())
        missing = REQUIRED_INTERNAL - keys
        assert not missing, f"{profile_path.name} に必須マッピング欠落: {missing}"

    def test_optional_fields_are_strings(self, profile_path):
        profile = load_site_profile(profile_path)
        for field in ("encoding", "date_format", "default_seller", "display_name"):
            if field in profile:
                assert isinstance(profile[field], str)


class TestLoadCsvWithProfile:
    PROFILE = {
        "encoding": "utf-8",
        "columns": {
            "order_date": "注文日",
            "product_name": "商品名",
            "unit_price": "金額",
            "quantity": "数量",
        },
        "default_seller": "テスト店",
        "date_format": "%Y-%m-%d",
    }

    def _write_csv(self, tmp_path, content):
        p = tmp_path / "orders.csv"
        p.write_text(content, encoding="utf-8")
        return p

    def test_maps_and_computes_paid_amount(self, tmp_path):
        csv = self._write_csv(
            tmp_path,
            "注文日,商品名,金額,数量\n2025-01-10,ロキソニンS,698,2\n",
        )
        df = load_csv(csv, self.PROFILE)
        assert list(df.columns) == UNIFIED_COLUMNS
        assert df.loc[0, "paid_amount"] == 698 * 2
        assert df.loc[0, "seller"] == "テスト店"  # seller 列が無いのでデフォルト補完

    def test_strips_currency_symbols_and_commas(self, tmp_path):
        csv = self._write_csv(
            tmp_path,
            "注文日,商品名,金額,数量\n2025-02-01,パブロンゴールドA,\"￥1,280\",1\n",
        )
        df = load_csv(csv, self.PROFILE)
        assert df.loc[0, "unit_price"] == 1280

    def test_missing_required_column_raises(self, tmp_path):
        # 金額(unit_price)カラムが存在しない
        csv = self._write_csv(tmp_path, "注文日,商品名\n2025-01-10,ロキソニンS\n")
        with pytest.raises(ValueError):
            load_csv(csv, self.PROFILE)

    def test_unparseable_rows_dropped(self, tmp_path):
        csv = self._write_csv(
            tmp_path,
            "注文日,商品名,金額,数量\nbad-date,商品X,500,1\n2025-03-03,商品Y,600,1\n",
        )
        df = load_csv(csv, self.PROFILE)
        # 日付パース失敗行は除外される
        assert len(df) == 1
        assert df.loc[0, "product_name"] == "商品Y"


class TestFilterByYear:
    def test_filters_to_year(self):
        df = pd.DataFrame(
            {
                "order_date": pd.to_datetime(["2024-12-31", "2025-01-01", "2025-12-31", "2026-01-01"]),
                "product_name": ["a", "b", "c", "d"],
            }
        )
        result = filter_by_year(df, 2025)
        assert list(result["product_name"]) == ["b", "c"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
