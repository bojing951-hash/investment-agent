# Audit-R32 离线电池回执 @ Zwork

- 口径: tests/test_*.py 逐件 `python3 tests/<file>`,绿 = rc ∈ {0, 5}(与 battery.sh 一致)
- 结果: files=205 pass=204 fail=1
- 逐件清单见同目录 battery_Zwork_summary.tsv(状态 / rc / 文件);原始日志留在仓外

- 提交 facc9a8 提交后运行(裁决后交付状态面修复;该印章下的再交付已被 cf33de3 取代)。唯一红件 = test_arch_reform_phase6.py 的 D3(未跟踪的上一印章验收证据目录,纯文档);证据目录移出后该件单独重跑 29/0(phase6_postcommit_Z.txt)。
- 红件: test_arch_reform_phase6.py (rc 1; PHASE6 判定: 28 PASS / 1 FAIL (外部工件不在场项=显式 SKIP 不计判))
