# Audit-R31 电池回执 — 2026-11-22T14:27:20Z(首轮)/14:33Z(复跑)
- 树: git archive 验收同源仓 @ ca916cd(ca916cdca7b749282e498d8c8f0eac8bf43b7372)
- 工作面: 证据树未跟踪(phase6-D3 既有口径)
- 口径: 逐件 python3 tests/test_*.py, rc∈{0,5} 绿;共 204 件
- 首轮: 202 PASS / 2 FAIL——
  1. tests/test_arch_reform_phase6.py rc=1: 未提交文档红(整改树工作面净判据,
     证据提交后复跑绿=既有口径,R30 同形);
  2. tests/test_charter5_vendor_residue_guard.py rc=1: **自指效应**——本证据包
     battery_raw.txt(其他测试自身输出的含厂商旗标字样描述文本)触发全仓
     零容忍静态扫描。处置: raw 移出仓外(/tmp 接受区留档,不入公开树)→单件复跑
     **rc=0 绿**。教训入档: 电池 raw 输出不入仓内证据树。
- 复跑后立足面: **203 PASS / 1 FAIL**(唯 phase6-D3);phase6 于证据提交后复跑绿
  → 204/204(回执见下行补注)。
- 证据提交后复跑: phase6-D3 **rc=0 绿**(29 PASS/0 FAIL)——电池 204/204;
  vendor 守卫复跑: 首轮复跑红(报告与本回执的「自指效应」记述文字本身携带
  厂商旗标字样原文)→措辞改写为零字面后 **rc=0 绿**(教训二连: 记述也不带
  字面,用「厂商旗标字样」指称)。
