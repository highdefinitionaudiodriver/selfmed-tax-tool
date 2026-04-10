"""医薬品判定モジュール。

商品名を対象品目辞書と照合し、セルフメディケーション税制対象かを判定する。
判定結果は「対象」「要確認」「対象外」の3段階。
"""

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd


def load_medicine_dict(dict_path: Path) -> dict:
    """医薬品辞書JSONを読み込む。"""
    with open(dict_path, encoding="utf-8") as f:
        return json.load(f)


def normalize_text(text: str) -> str:
    """テキストを正規化する。

    - NFKC正規化（全角英数→半角、半角カナ→全角カナ）
    - 連続スペースを1つに統一
    - 前後の空白を除去
    - 小文字化（英字部分）
    """
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.lower()
    return text


def judge_product(product_name: str, brands: list[str], exclude_keywords: list[str]) -> str:
    """商品名を判定する。

    Args:
        product_name: 商品名（元テキスト）。
        brands: 対象ブランド名のリスト。
        exclude_keywords: 除外キーワードのリスト。

    Returns:
        "対象", "要確認", or "対象外"
    """
    normalized = normalize_text(product_name)
    normalized_brands = [normalize_text(b) for b in brands]
    normalized_excludes = [normalize_text(e) for e in exclude_keywords]

    # ブランド名との照合
    matched_brand = False
    for brand in normalized_brands:
        if brand in normalized:
            matched_brand = True
            break

    if not matched_brand:
        return "対象外"

    # 除外キーワードのチェック
    for exclude in normalized_excludes:
        if exclude in normalized:
            return "要確認"

    return "対象"


def apply_judgement(df: pd.DataFrame, medicine_dict: dict) -> pd.DataFrame:
    """DataFrameの全商品に対して判定を適用する。

    Args:
        df: 統一フォーマットのDataFrame（product_name列が必要）。
        medicine_dict: brands, exclude_keywords を含む辞書。

    Returns:
        「判定」列が追加され、「対象外」が除外されたDataFrame。
    """
    brands = medicine_dict["brands"]
    exclude_keywords = medicine_dict.get("exclude_keywords", [])

    df = df.copy()
    df["判定"] = df["product_name"].apply(
        lambda name: judge_product(name, brands, exclude_keywords)
    )

    # 「対象外」を除外
    df = df[df["判定"] != "対象外"].reset_index(drop=True)
    return df
