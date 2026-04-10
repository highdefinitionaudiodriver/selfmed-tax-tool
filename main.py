"""セルフメディケーション税制 対象医薬品抽出ツール。

ECサイトの購入履歴CSVから、セルフメディケーション税制の対象となる
市販薬を抽出し、確定申告の明細書作成に必要な情報をxlsx形式で出力する。

使い方:
    python main.py --input 注文履歴.csv
    python main.py --input 注文履歴.csv --year 2025 --output 結果.xlsx
"""

import argparse
import sys
from pathlib import Path

# プロジェクトルートを基準にパスを解決
PROJECT_ROOT = Path(__file__).resolve().parent

sys.path.insert(0, str(PROJECT_ROOT))

from core.loader import load_site_profile, load_csv, filter_by_year
from core.matcher import load_medicine_dict, apply_judgement
from core.exporter import export_xlsx

SITE_PROFILES_DIR = PROJECT_ROOT / "config" / "site_profiles"


def list_available_sites() -> list[tuple[str, str]]:
    """利用可能なサイトプロファイル一覧を (site_key, display_name) で返す。

    ファイル名が `_` で始まるもの（テンプレート等）は除外する。
    """
    sites = []
    for path in sorted(SITE_PROFILES_DIR.glob("*.json")):
        if path.stem.startswith("_"):
            continue
        try:
            profile = load_site_profile(path)
            display_name = profile.get("display_name", path.stem)
        except Exception:
            display_name = path.stem
        sites.append((path.stem, display_name))
    return sites


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="セルフメディケーション税制 対象医薬品抽出ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="例: python main.py --input 注文履歴.csv --site rakuten --year 2025",
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        help="入力CSVファイルのパス",
    )
    parser.add_argument(
        "--site", "-s",
        default="amazon",
        help="ECサイト種別（デフォルト: amazon）",
    )
    parser.add_argument(
        "--year", "-y",
        type=int,
        default=None,
        help="対象年でフィルタ（省略時: フィルタなし）",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("selfmed_result.xlsx"),
        help="出力xlsxファイルのパス（デフォルト: selfmed_result.xlsx）",
    )
    parser.add_argument(
        "--list-sites",
        action="store_true",
        help="対応しているECサイト一覧を表示して終了",
    )
    return parser


def main(args: list[str] | None = None) -> int:
    parser = build_parser()
    opts = parser.parse_args(args)

    # --- サイト一覧表示 ---
    if opts.list_sites:
        print("対応ECサイト一覧:")
        for site_key, display_name in list_available_sites():
            print(f"  {site_key:<20} {display_name}")
        return 0

    # --- 入力ファイル必須チェック ---
    if opts.input is None:
        parser.error("--input は必須です（--list-sites 以外の場合）")

    # --- 入力ファイルの存在チェック ---
    if not opts.input.exists():
        print(f"エラー: 入力ファイルが見つかりません: {opts.input}", file=sys.stderr)
        return 1

    # --- サイトプロファイルの読み込み ---
    profile_path = SITE_PROFILES_DIR / f"{opts.site}.json"
    if not profile_path.exists():
        print(f"エラー: サイトプロファイルが見つかりません: {profile_path}", file=sys.stderr)
        print("  対応サイト一覧は `python main.py --list-sites` で確認できます。", file=sys.stderr)
        return 1

    profile = load_site_profile(profile_path)

    # --- 医薬品辞書の読み込み ---
    dict_path = PROJECT_ROOT / "config" / "medicine_dict" / "brands.json"
    medicine_dict = load_medicine_dict(dict_path)

    # --- CSV読み込み・正規化 ---
    print(f"読み込み中: {opts.input}")
    df = load_csv(opts.input, profile)
    print(f"  → {len(df)} 件の注文を読み込みました")

    # --- 年度フィルタ ---
    if opts.year:
        df = filter_by_year(df, opts.year)
        print(f"  → {opts.year}年の注文: {len(df)} 件")

    # --- 医薬品判定 ---
    df = apply_judgement(df, medicine_dict)
    target_count = len(df[df["判定"] == "対象"])
    review_count = len(df[df["判定"] == "要確認"])
    print(f"  → 対象: {target_count} 件 / 要確認: {review_count} 件")

    # --- 結果チェック ---
    if len(df) == 0:
        print("対象となる医薬品は見つかりませんでした。")
        return 0

    # --- xlsx出力 ---
    output_path = export_xlsx(df, opts.output)
    total_amount = int(df["unit_price"].sum())
    print(f"\n出力完了: {output_path}")
    print(f"合計金額: {total_amount:,}円")
    if review_count > 0:
        print(f"\n※ 「要確認」が {review_count} 件あります。出力ファイルの黄色行を確認してください。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
