# Claude Code 引き継ぎメモ

`HANDOFF_FOR_CODEX.md` と同じ要点です。

## 2026-05-26 Codex作業

`tools/check_setup.py` を追加しました。GUIや実CSVなしで、サイトプロファイル・旧brands辞書・構造化OTCマスタの最低限の整合性を確認できます。

確認済み:

```powershell
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile main.py tools\check_setup.py
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\check_setup.py
```

`pytest` はこの実行環境のバンドルPythonに未導入だったため未実行です。

次は `--json`、実CSV検査、旧辞書と構造化マスタの差分レポートが候補です。
