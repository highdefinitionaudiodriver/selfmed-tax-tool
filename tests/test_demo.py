"""--demo（同梱サンプル即実行）の検証。叩けば即結果が出ることを保証する。"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_fixture_exists():
    assert (ROOT / "tests" / "fixtures" / "amazon_sample.csv").is_file()


def test_demo_produces_xlsx(tmp_path):
    out = tmp_path / "demo.xlsx"
    result = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), "--demo", "-o", str(out)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stderr
    assert out.is_file()
    assert out.stat().st_size > 0
