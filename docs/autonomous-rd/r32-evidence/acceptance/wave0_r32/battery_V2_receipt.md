# Audit-R32 离线电池回执 @ V2

- 口径: tests/test_*.py 逐件 `python3 tests/<file>`,绿 = rc ∈ {0, 5}(与 battery.sh 一致)
- 结果: files=205 pass=203 fail=2
- 逐件清单见同目录 battery_V2_summary.tsv(状态 / rc / 文件);原始日志留在仓外

- 最终代码提交 cf33de3 提交后运行;运行期间操作者的其他阶段在其他验收树内并行执行(v_stage.sh / plan_v.sh / 标准更新入口 VENTRY)。红件两件: test_arch_reform_phase6.py D3(未跟踪的上一印章证据目录,纯文档);test_audit_r31_gate.py §A1b(扫描共享临时目录时看见并行研究进程的瞬时冻结副本目录,事后无残留;同一提交树单独重跑 43/43,见 r31gate_final.txt)。
- 红件: test_arch_reform_phase6.py (rc 1; PHASE6 判定: 28 PASS / 1 FAIL (外部工件不在场项=显式 SKIP 不计判)), test_audit_r31_gate.py (rc 1; === R31 门: 42/43 ===)
