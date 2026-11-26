# Audit-R32 离线电池回执 @ fix_committed_8f9055d

- 口径: tests/test_*.py 逐件 `python3 tests/<file>`,绿 = rc ∈ {0, 5}(与 battery.sh 一致)
- 结果: files=205 pass=204 fail=1
- 逐件清单见同目录 battery_fix_committed_8f9055d_summary.tsv(状态 / rc / 文件);原始日志留在仓外

- 提交 8f9055d 提交后运行(该印章已被后续提交取代);唯一红件 = test_arch_reform_phase6.py 的 D3「整改树工作面净」检查,其列举的是未跟踪的验收证据目录(docs/autonomous-rd/r32-evidence/acceptance/*,纯文档),与代码无关。
- 红件: test_arch_reform_phase6.py (rc 1; PHASE6 判定: 28 PASS / 1 FAIL (外部工件不在场项=显式 SKIP 不计判))
