#!/usr/bin/env python3
"""Self-medication tax tool setup doctor.

Validates the data files that users usually edit first:
- site profile JSON files under config/site_profiles
- legacy medicine dictionary under config/medicine_dict/brands.json
- structured OTC master under data/otc_master.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SITE_PROFILES_DIR = ROOT / "config" / "site_profiles"
LEGACY_DICT = ROOT / "config" / "medicine_dict" / "brands.json"
OTC_MASTER = ROOT / "data" / "otc_master.json"
REQUIRED_PROFILE_COLUMNS = ("order_date", "product_name", "unit_price")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def check_site_profiles() -> list[str]:
    errors: list[str] = []
    if not SITE_PROFILES_DIR.is_dir():
        return [f"missing directory: {SITE_PROFILES_DIR}"]

    profiles = sorted(SITE_PROFILES_DIR.glob("*.json"))
    if not profiles:
        return [f"no site profiles found: {SITE_PROFILES_DIR}"]

    for path in profiles:
        try:
            profile = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}: invalid JSON at line {exc.lineno}: {exc.msg}")
            continue

        if path.stem.startswith("_"):
            continue

        columns = profile.get("columns")
        if not isinstance(columns, dict):
            errors.append(f"{path}: columns must be an object")
            continue

        missing = [key for key in REQUIRED_PROFILE_COLUMNS if not columns.get(key)]
        if missing:
            errors.append(f"{path}: missing required columns mapping: {', '.join(missing)}")

        encoding = profile.get("encoding", "utf-8")
        if not isinstance(encoding, str) or not encoding:
            errors.append(f"{path}: encoding must be a non-empty string")

    return errors


def check_legacy_dictionary() -> list[str]:
    errors: list[str] = []
    if not LEGACY_DICT.is_file():
        return [f"missing legacy dictionary: {LEGACY_DICT}"]

    try:
        data = load_json(LEGACY_DICT)
    except json.JSONDecodeError as exc:
        return [f"{LEGACY_DICT}: invalid JSON at line {exc.lineno}: {exc.msg}"]

    brands = data.get("brands")
    if not isinstance(brands, list) or not brands:
        errors.append(f"{LEGACY_DICT}: brands must be a non-empty array")
    elif any(not isinstance(item, str) or not item.strip() for item in brands):
        errors.append(f"{LEGACY_DICT}: brands must contain only non-empty strings")

    exclude = data.get("exclude_keywords", [])
    if not isinstance(exclude, list):
        errors.append(f"{LEGACY_DICT}: exclude_keywords must be an array when present")

    return errors


def check_otc_master() -> list[str]:
    errors: list[str] = []
    if not OTC_MASTER.is_file():
        return [f"missing OTC master: {OTC_MASTER}"]

    try:
        data = load_json(OTC_MASTER)
    except json.JSONDecodeError as exc:
        return [f"{OTC_MASTER}: invalid JSON at line {exc.lineno}: {exc.msg}"]

    meta = data.get("_meta")
    if not isinstance(meta, dict):
        errors.append(f"{OTC_MASTER}: _meta must be an object")
    else:
        for key in ("schema_version", "data_version", "updated_at", "scope"):
            if not meta.get(key):
                errors.append(f"{OTC_MASTER}: _meta.{key} is required")

    ingredients = data.get("active_ingredients")
    if not isinstance(ingredients, list) or not ingredients:
        errors.append(f"{OTC_MASTER}: active_ingredients must be a non-empty array")
        return errors

    seen_products: set[str] = set()
    for idx, ingredient in enumerate(ingredients):
        prefix = f"{OTC_MASTER}: active_ingredients[{idx}]"
        if not isinstance(ingredient, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in ("name", "category", "products"):
            if key not in ingredient:
                errors.append(f"{prefix}.{key} is required")
        products = ingredient.get("products")
        if not isinstance(products, list) or not products:
            errors.append(f"{prefix}.products must be a non-empty array")
            continue
        for product in products:
            if not isinstance(product, str) or not product.strip():
                errors.append(f"{prefix}.products contains an empty product name")
                continue
            if product in seen_products:
                errors.append(f"{OTC_MASTER}: duplicate product name: {product}")
            seen_products.add(product)

    exclude = data.get("exclude_keywords", [])
    if not isinstance(exclude, list):
        errors.append(f"{OTC_MASTER}: exclude_keywords must be an array when present")

    return errors


def main() -> int:
    checks = {
        "site profiles": check_site_profiles(),
        "legacy medicine dictionary": check_legacy_dictionary(),
        "structured OTC master": check_otc_master(),
    }

    failed = False
    for label, errors in checks.items():
        if errors:
            failed = True
            print(f"NG {label}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK {label}")

    if failed:
        print("Self-med setup check failed.", file=sys.stderr)
        return 1

    print("Self-med setup check OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
