# Audit-R32 离线电池回执 @ V2clean

- 口径: tests/test_*.py 逐件 `python3 tests/<file>`,绿 = rc ∈ {0, 5}(与 battery.sh 一致)
- 结果: files=205 pass=205 fail=0
- 逐件清单见同目录 battery_V2clean_summary.tsv(状态 / rc / 文件);原始日志留在仓外

- 最终代码提交 cf33de3 提交后、上一印章证据目录已移出工作树且无任何并行引擎进程时运行(干净工作树)。
