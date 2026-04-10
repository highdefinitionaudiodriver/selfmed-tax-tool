"""loader.py のユニットテスト。"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.loader import load_site_profile, load_csv, filter_by_year

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PROFILE_PATH = PROJECT_ROOT / "config" / "site_profiles" / "amazon.json"


@pytest.fixture
def profile():
    return load_site_profile(PROFILE_PATH)


@pytest.fixture
def sample_df(profile):
    return load_csv(FIXTURES / "amazon_sample.csv", profile)


class TestLoadSiteProfile:
    def test_loads_valid_json(self, profile):
        assert "columns" in profile
        assert "encoding" in profile

    def test_column_mapping_keys(self, profile):
        expected_keys = {"order_date", "product_name", "unit_price", "quantity", "seller"}
        assert set(profile["columns"].keys()) == expected_keys


class TestLoadCsv:
    def test_returns_dataframe(self, sample_df):
        assert isinstance(sample_df, pd.DataFrame)

    def test_has_unified_columns(self, sample_df):
        expected = {"order_date", "product_name", "unit_price", "quantity", "seller"}
        assert set(sample_df.columns) == expected

    def test_row_count(self, sample_df):
        assert len(sample_df) == 6

    def test_date_parsed(self, sample_df):
        assert pd.api.types.is_datetime64_any_dtype(sample_df["order_date"])

    def test_price_with_comma_parsed(self, sample_df):
        # "1,280" が 1280 として読まれること
        pabron_row = sample_df[sample_df["product_name"].str.contains("パブロン")]
        assert pabron_row.iloc[0]["unit_price"] == 1280

    def test_price_numeric(self, sample_df):
        assert pd.api.types.is_numeric_dtype(sample_df["unit_price"])

    def test_quantity_is_int(self, sample_df):
        assert sample_df["quantity"].dtype in [int, "int64", "int32"]

    def test_missing_required_column_raises(self, profile):
        """必須カラムが無いCSVはエラー。"""
        bad_csv = FIXTURES / "bad_columns.csv"
        bad_csv.write_text("日付,名前,価格\n2025-01-01,テスト,100\n", encoding="utf-8")
        with pytest.raises(ValueError, match="必須カラムが見つかりません"):
            load_csv(bad_csv, profile)
        bad_csv.unlink()


class TestFilterByYear:
    def test_filters_correctly(self, sample_df):
        df_2025 = filter_by_year(sample_df, 2025)
        assert len(df_2025) == 6

    def test_no_results_for_other_year(self, sample_df):
        df_2024 = filter_by_year(sample_df, 2024)
        assert len(df_2024) == 0
