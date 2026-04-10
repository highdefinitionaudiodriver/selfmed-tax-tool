"""CSV読み込み・正規化モジュール。

サイトプロファイル（JSONマッピング定義）に基づき、
各ECサイトのCSVを統一フォーマットのDataFrameに変換する。
"""

import json
from pathlib import Path

import pandas as pd


# 内部統一カラム名
UNIFIED_COLUMNS = ["order_date", "product_name", "unit_price", "quantity", "seller"]


def load_site_profile(profile_path: Path) -> dict:
    """サイトプロファイルJSONを読み込む。"""
    with open(profile_path, encoding="utf-8") as f:
        return json.load(f)


def load_csv(csv_path: Path, profile: dict) -> pd.DataFrame:
    """CSVを読み込み、サイトプロファイルに基づいて統一フォーマットに変換する。

    Args:
        csv_path: 入力CSVファイルのパス。
        profile: サイトプロファイル辞書。

    Returns:
        統一カラム名のDataFrame。
    """
    encoding = profile.get("encoding", "utf-8")
    column_mapping = profile["columns"]
    default_seller = profile.get("default_seller", "不明")
    date_format = profile.get("date_format", "%Y-%m-%d")

    # CSV読み込み
    df = pd.read_csv(csv_path, encoding=encoding)

    # カラム名の逆引きマップ（日本語 → 内部名）
    reverse_map = {v: k for k, v in column_mapping.items()}

    # 存在するカラムのみリネーム
    rename_dict = {orig: internal for orig, internal in reverse_map.items() if orig in df.columns}
    df = df.rename(columns=rename_dict)

    # sellerカラムが無い場合はデフォルト値で補完
    if "seller" not in df.columns:
        df["seller"] = default_seller

    # 必須カラムの存在チェック
    required = ["order_date", "product_name", "unit_price"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        available = list(df.columns)
        raise ValueError(
            f"必須カラムが見つかりません: {missing}。"
            f"CSVのカラム: {available}。"
            f"site_profileのマッピングを確認してください。"
        )

    # quantityが無い場合はデフォルト1
    if "quantity" not in df.columns:
        df["quantity"] = 1

    # 型変換
    df["order_date"] = pd.to_datetime(df["order_date"], format=date_format, errors="coerce")
    df["unit_price"] = pd.to_numeric(
        df["unit_price"].astype(str).str.replace(",", "").str.replace("￥", "").str.strip(),
        errors="coerce",
    )
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)

    # 必要なカラムだけ残す
    df = df[UNIFIED_COLUMNS].copy()

    # パースに失敗した行を除外
    df = df.dropna(subset=["order_date", "product_name", "unit_price"])

    df = df.reset_index(drop=True)
    return df


def filter_by_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """指定年の注文のみにフィルタする。"""
    return df[df["order_date"].dt.year == year].reset_index(drop=True)
