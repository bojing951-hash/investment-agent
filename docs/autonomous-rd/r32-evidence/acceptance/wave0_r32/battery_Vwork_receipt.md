# Audit-R32 离线电池回执 @ Vwork

- 口径: tests/test_*.py 逐件 `python3 tests/<file>`,绿 = rc ∈ {0, 5}(与 battery.sh 一致)
- 结果: files=205 pass=203 fail=2
- 逐件清单见同目录 battery_Vwork_summary.tsv(状态 / rc / 文件);原始日志留在仓外

- 提交 37691b7 的修复在工作树上运行(提交发生在电池运行中途,已披露):红件 test_audit_r28_gate.py(§D6a/§D6b/§D7a)=该印章放开重放门④造成的回归;红件 test_arch_reform_phase6.py D3=未跟踪的验收证据目录(纯文档)。CI 45348011655 在该提交为红。该印章已被 cf33de3 撤回更正。
- 红件: test_arch_reform_phase6.py (rc 1; PHASE6 判定: 28 PASS / 1 FAIL (外部工件不在场项=显式 SKIP 不计判)), test_audit_r28_gate.py (rc 1;   FAIL §D7a 旧档严格面: 键未记录≠一致→crosscheck FAIL 在场且整体 拒(rc=1+blocked=code_version_mism)
