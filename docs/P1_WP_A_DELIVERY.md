# IA-P1-WP-A DELIVERY(交付件 · v1.3 实现轮 · 状态=情形(d)停止#3:单点阻塞)

> 包: IA-P1-WP-A | 分支: `dev/p1-impl-a`(@f0a2aea 续作) | 合同: IA-P1-WP-A-AC-v1.3(FROZEN 2026-11-05)
> 本文件=合同 §五 交付件;逐项 1:1 映射登记+fixture→期望值映射+漂移维护策略。
> **状态一句话**: v1.3 授权面(A7+M11)全部落地且 69/70 本地套件绿;验收要点④被
> 1 处清单外锁(`test_p0_baseline_lock_equivalence.py` N3d 注入算术锚)阻塞——
> 情形(d)停止#3,零越权修改,一行 v1.4 增量授权建议见 §四。真实采集(要点②)
> 因 CI 门红按序未启动,留 v1.4。

## §一 交付清单(逐项 1:1: 文件→授权项→DESIGN 依据→验证锚)

| # | 文件 | A/M | 授权项 | DESIGN 依据 | 验证锚 |
|---|---|---|---|---|---|
| A1 | docs/P1_WP_A_REPORT.md | A(续笔) | 必含件 | §零(ii) | §零.11-§零.15 |
| A2 | docs/P1_WP_A_DELIVERY.md | A | 必含件 | §零(ii) | 本文件 |
| A3 | scripts/jp_market_collector.py | A | §四 L124 | L169 范围 | test_p1_wp_a T3(7测) |
| A4 | scripts/ea_market_collector.py | A | §四 L124 | L169 范围 | test_p1_wp_a T4(6测) |
| A5 | tests/test_p1_wp_a.py | A | 含代码必含 | L169 要点①③ | 23 测全绿 |
| A6 | data/daily/jp_20261105.json | A(未产) | v1.1④ | L169 要点② | v1.4(见 §四) |
| A7 | data/daily/ea_20261105.json | A(未产) | v1.1④ | L169 要点② | v1.4(见 §四) |
| M-a | config/metric_registry.json | M | v1.2③(a) | §三(a-1)/a-3 | 85→94/v2.2.0/三字段全量+9 append 尾 |
| M-b | run_weekly.py | M | v1.2③(b) | §四 L124 | 11→13 步(2 非关键尾追加);test_phase3 /13×13 |
| M-c | scripts/japan_rate_collector.py | **M 条件类未触发,零触碰** | v1.2③(c) | 复用调用优先 | A3/A4 import 复用 |
| M-d | scripts/registry_semantics.py | M | v1.2③(d) | 通道登记链 | KNOWN_SOURCES+2/KNOWN_CALENDARS+ea |
| M-e | scripts/research_provenance.py | M | v1.2③(e)+v1.3③(i) | 通道登记链 | _AUTHORIZED_COLLECTORS+2/SOURCE_FILE_RULES+{jp,ea} 窗5 |
| M-f | scripts/trading_calendar.py | M | v1.2③(f) | 通道登记链 | MARKETS+ea/is_trading_day ea 分支 |
| M-g | scripts/historical_coverage_audit.py | M | v1.3③(g) | 红-1 修复 | REGISTRY_SOURCE_CHANNEL+2 行;test_p02_w4 d2 绿 |
| M-h | tests/helpers/baseline_locks.py | M | v1.3③(h) | 红-2 修复簇① | collector_to_channel+2 行;evolution_legal 绿/additions=13 |
| M-j | tests/test_phase3.py | M | v1.3③(j) | 红-3 修复 | L216 /13×13;47 测绿 |
| M-k | tests/fixt.py | M | v1.3③(k)二选一=fixt | 红-4 修复 | +jp/ea 合成 payload;test_p01_fix6 B 循环零改动 92 测绿 |
| M-锁1 | tests/test_p03_e2eb_b3.py | M | v1.2③(a)从属锁+v1.3 增 t06 | 计数/冻结/增集锁域化 | t01=94/93/v2.2.0/t02+3字段/t06=13;28 测绿 |
| M-锁2 | tests/test_p03_final_acceptance.py | M | v1.2③(a)从属锁 | t11 计数锁域化 | t11=94/v2.2.0/93;9 测绿 |

清单外零变更(AC-05);`git status`/`git diff --name-status` 逐件可复核。

## §二 验收要点逐条映射(L169 要点①-④)

| 要点 | 状态 | 证据 |
|---|---|---|
| ① economy 与 P1-P8(v1.3=P1-P10)一致性逐条+负向拒入【测试】 | **绿** | test_p1_wp_a T1(t1a-t1f,6测): 逐条 classify 独立重编码对账+聚合 US49/CN10/HK4/JP8/EA11/GLOBAL12+负向 3 fixture None+零未归类计数+12 候选落点(复用3禁双注册+9 append 尾) |
| ② 首份 jp_/ea_ 真实档在场【数据档引用】 | **未启动(情形(d)联动)** | CI 门(要点④)红→按合同序(⑨→⑪)真实采集未启动;采集器已就绪+源 URL 定值(REPORT §零.12⑩);v1.4 授权 N3d 一行后即可执行 |
| ③ 新采集器离线测试(源失败→MISSING 不填0)【测试/CI】 | **绿** | test_p1_wp_a T3/T4(13测): 全成功/单源失败/全失败(→READ_FAIL+节缺席+exit1 不落盘)/零网络 mock 计数=0/诚实缺席键不出现(DAX·CAC40·JP_CPI_TOKYO)/候选键口径核验负向 |
| ④ offline-tests 全套件零回归【CI】 | **69/70 绿,1 红阻塞** | 本地全量 70 slots=69 可运行套件中 68 exit=0+1 红(test_p0_baseline_lock_equivalence,29通过/2失败→N3d 清单外锁+R[legal85] 提交序工件[本地提交后复跑自愈]);阻塞详情 §四 |

## §三 fixture→期望值映射(漂移维护策略之基;全 [示意·合成·值发明])

| fixture | 位置 | 期望锚(字面量) |
|---|---|---|
| fixt jp 节 | tests/fixt.py | BOJ_POLICY_RATE=0.100/prev 0.090;JGB_10Y=1.200/prev 1.180;JGB_2Y=0.500/prev 0.480;NIKKEI225 close=38000.00/high·low=null;inflation 键不出现 |
| fixt ea 节 | tests/fixt.py | ECB_DFR=2.00/ECB_MRO=3.15;BUND_10Y=2.60/prev 2.62;BUND_2Y=2.30/prev 2.35;EA_HICP_YOY=2.2/prev 2.4/change −0.2/MoM/Monthly;prices 键不出现 |
| T3 合成 raw | tests/test_p1_wp_a.py | SYN_MOF 末行 JGB 2Y=1.891/10Y=2.855 次新 1.870/2.830;FRED '.'跳过末值 0.743/prev 0.860;NIKKEI 末值 38000.25/series 3 点 |
| T4 合成 raw | tests/test_p1_wp_a.py | ECB 空值行跳过 DFR 末 2.00;MRO 3.15;HICP 2026-09→'2026-09-01' 2.2/prev 2.4;BBK 10Y 2.60/prev 2.62·2Y 2.30;meta 正例 9bis10/1bis2·反例 5bis10 |
| registry 期望 | tests/test_p1_wp_a.py+test_p03_e2eb_b3.py | 94/93/v2.2.0;聚合六值;四 JP 条目+3字段全冻结;t06 additions=JP4∪NEW9 |

漂移维护策略(沿 R057/R060 形态): ①注册表演进→计数/聚合/冻结锁按 vintage 自适应面优先(expected_registry_count/vintage_additions),非自适应字面锁(94/93/v2.2.0)随提交域化,禁语义弱化;②采集器源端形态漂移→T3/T4 raw 注入件即最小回归面,新形态加 fixture 不改产线;③fixture 值变更须同步本表+对应断言(同提交);④P1-WP-B 接线轮(normalize_jp/ea+D7 解除)承接: _SOURCE_TO_INPUT 增键/fixt 通道键进快照 sources_status 断言/金题绑定面复核,均在 WP-B 合同面。

## §四 阻塞详情与 v1.4 建议(情形(d)停止#3;供操作者,非自决)

- **N3d**(清单外): `tests/test_p0_baseline_lock_equivalence.py` `n3d_table_rows()` 注入 `range(expected_registry_count()-4)`: live=94 时 rows=90≥W4_REPORT_ROWS_FLOOR(82,冻结锚)→下限锁不咬合→check 红。R060 先例=live 81→85 时同款锚迁移一次(「缺表头」→「缺表头+4行」,该函数 docstring 自证)。**v1.4 建议: 该文件 n3d 注入算术一行域化(锚改 floor-1 或 live 自适应缺行数,R060 重锚同形态,非语义弱化)**;v1.2 轮 §零.8.1「全部强制触红项」清查对该项漏报,如实登记。
- **R[legal85]**(非阻塞): 预演 worktree 取 committed HEAD;未提交态下旧代码+新注册表世界结构性红(23/28)——本地提交后复跑自愈(代码/注册表同提交原子一致);已在 REPORT §零.15 登记验证结果。
- **要点②联动**: CI 门红未过→真实采集(白名单五域,源 URL 已定值 REPORT §零.12⑩)与 jp_/ea_ 首档落盘留 v1.4 同轮执行;`git add -f` 显式纳入形态(B3 先例)已在 §零.14 登记。

## §五 AC 自检摘要(v1.3 停止形态;逐条全文见 stdout 四段自述)

AC-01 规格抄录绿(§零.1)/AC-02 未启动(d)联动/AC-03 绿(A3/A4 离线 13 测)/AC-04 1红阻塞(N3d,§四)/AC-05 绿(A7+M11 零清单外)/AC-06 证据包随停止形态缩减(本地 CI 矩阵+复跑 log;zip 装配留 v1.4 完整形态或按操作者指令)/AC-07 四段自述=stdout。真实面(采集/推送终态)如实标注未发生。
