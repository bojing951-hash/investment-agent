# Audit-R32 离线电池回执 @ C

- 口径: tests/test_*.py 逐件 `python3 tests/<file>`,绿 = rc ∈ {0, 5}(与 battery.sh 一致)
- 结果: files=205 pass=205 fail=0
- 逐件清单见同目录 battery_C_summary.tsv(状态 / rc / 文件);原始日志留在仓外

- 更正提交 12edab8 提交后运行(干净工作树,无并行引擎进程)。
