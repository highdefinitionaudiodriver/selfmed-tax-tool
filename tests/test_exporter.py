"""exporter.py のユニットテスト。"""

import sys
from pathlib import Path

import pandas as pd
import pytest
from openpyxl import load_workbook

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.exporter import export_xlsx


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "seller": ["Amazon", "Amazon", "ヘルスケアストア"],
        "product_name": ["ロキソニンS 12錠", "パブロンゴールドA キッズ", "アレグラFX 28錠"],
        "unit_price": [698, 1280, 1980],
        "order_date": pd.to_datetime(["2025-03-15", "2025-06-02", "2025-09-01"]),
        "quantity": [1, 1, 1],
        "判定": ["対象", "要確認", "対象"],
    })


@pytest.fixture
def output_path(tmp_path):
    return tmp_path / "test_output.xlsx"


class TestExportXlsx:
    def test_creates_file(self, sample_df, output_path):
        result = export_xlsx(sample_df, output_path)
        assert result.exists()

    def test_sheet_name(self, sample_df, output_path):
        export_xlsx(sample_df, output_path)
        wb = load_workbook(output_path)
        assert wb.sheetnames == ["セルフメディケーション明細"]

    def test_header_row(self, sample_df, output_path):
        export_xlsx(sample_df, output_path)
        wb = load_workbook(output_path)
        ws = wb.active
        headers = [ws.cell(row=1, column=c).value for c in range(1, 6)]
        assert headers == ["支払先の名称", "医薬品の名称", "支払った金額", "購入日", "判定"]

    def test_data_rows(self, sample_df, output_path):
        export_xlsx(sample_df, output_path)
        wb = load_workbook(output_path)
        ws = wb.active
        # 3行のデータ
        assert ws.cell(row=2, column=2).value == "ロキソニンS 12錠"
        assert ws.cell(row=3, column=2).value == "パブロンゴールドA キッズ"
        assert ws.cell(row=4, column=2).value == "アレグラFX 28錠"

    def test_total_row(self, sample_df, output_path):
        export_xlsx(sample_df, output_path)
        wb = load_workbook(output_path)
        ws = wb.active
        # 合計行: row=5 (ヘッダ1 + データ3 + 合計1)
        assert ws.cell(row=5, column=2).value == "合計"
        assert ws.cell(row=5, column=3).value == 698 + 1280 + 1980

    def test_review_row_highlighted(self, sample_df, output_path):
        export_xlsx(sample_df, output_path)
        wb = load_workbook(output_path)
        ws = wb.active
        # 「要確認」行 (row=3) が黄色ハイライト
        fill_color = ws.cell(row=3, column=1).fill.start_color.rgb
        assert fill_color == "00FFF2CC"

    def test_empty_dataframe(self, output_path):
        empty_df = pd.DataFrame(columns=[
            "seller", "product_name", "unit_price", "order_date", "quantity", "判定"
        ])
        export_xlsx(empty_df, output_path)
        wb = load_workbook(output_path)
        ws = wb.active
        # ヘッダ + 合計行のみ
        assert ws.cell(row=2, column=2).value == "合計"
        assert ws.cell(row=2, column=3).value == 0
