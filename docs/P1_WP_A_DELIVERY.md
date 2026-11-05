# IA-P1-WP-A DELIVERY(交付件 · v1.4 实现轮 · 状态=终态交付)

> 包: IA-P1-WP-A | 分支: `dev/p1-impl-a`(@65cf32f 续作→v1.4 终笔) | 合同: IA-P1-WP-A-AC-v1.4(FROZEN 2026-11-05 23:0x HKT)
> 本文件=合同 §五 交付件;逐项 1:1 映射登记+fixture→期望值映射+漂移维护策略。
> **状态一句话**: v1.3 授权面(A7+M11)落地后遗留的单点 N3d 已按 v1.4③(l) 一行域化
> (floor−1=81,R060 重锚同型二迁,双咬合语义逐字保持);要点② 真实采集执行完毕
> (jp_ 首档 4 系列/ea_ 首档 1 系列+READ_FAIL 如实);本地 CI **70 槽=69 exit=0+
> 1 SKIPPED 全绿**;证据 zip 八类装配;终笔推送。

## §一 交付清单(逐项 1:1: 文件→授权项→DESIGN 依据→验证锚)

| # | 文件 | A/M | 授权项 | DESIGN 依据 | 验证锚 |
|---|---|---|---|---|---|
| A1 | docs/P1_WP_A_REPORT.md | A(续笔) | 必含件 | §零(ii) | §零.11-§零.16 |
| A2 | docs/P1_WP_A_DELIVERY.md | A | 必含件 | §零(ii) | 本文件 |
| A3 | scripts/jp_market_collector.py | A | §四 L124 | L169 范围 | test_p1_wp_a T3(7测)+首档 4 系列 |
| A4 | scripts/ea_market_collector.py | A | §四 L124 | L169 范围 | test_p1_wp_a T4(6测)+首档 1 系列 |
| A5 | tests/test_p1_wp_a.py | A | 含代码必含 | L169 要点①③ | 23 测全绿(CI 70 槽含) |
| A6 | data/daily/jp_20261105.json | A(已产) | v1.1④ | L169 要点② | 4 系列: JGB_10Y=2.855@2026-11-04/JGB_2Y=1.891@2026-11-04/BOJ_POLICY_RATE=1.043@2026-09-01/NIKKEI225=61077.9@2026-11-05;inflation 键不出现(JP_CPI_TOKYO=MISSING) |
| A7 | data/daily/ea_20261105.json | A(已产) | v1.1④ | L169 要点② | 1 系列: ECB_MRO=2.65@2026-09-16;DFR/HICP/BUND×2=READ_FAIL(504/reset)如实;DAX/CAC40=MISSING;bund/inflation/prices 键不出现 |
| M-a | config/metric_registry.json | M | v1.2③(a) | §三(a-1)/a-3 | 85→94/v2.2.0/三字段全量+9 append 尾 |
| M-b | run_weekly.py | M | v1.2③(b) | §四 L124 | 11→13 步(2 非关键尾追加);test_phase3 /13×13 |
| M-c | scripts/japan_rate_collector.py | **M 条件类未触发,零触碰** | v1.2③(c) | 复用调用优先 | A3/A4 import 复用 |
| M-d | scripts/registry_semantics.py | M | v1.2③(d) | 通道登记链 | KNOWN_SOURCES+2/KNOWN_CALENDARS+ea |
| M-e | scripts/research_provenance.py | M | v1.2③(e)+v1.3③(i) | 通道登记链 | _AUTHORIZED_COLLECTORS+2/SOURCE_FILE_RULES+{jp,ea} 窗5 |
| M-f | scripts/trading_calendar.py | M | v1.2③(f) | 通道登记链 | MARKETS+ea/is_trading_day ea 分支 |
| M-g | scripts/historical_coverage_audit.py | M | v1.3③(g) | 红-1 修复 | REGISTRY_SOURCE_CHANNEL+2 行;test_p02_w4 d2 绿 |
| M-h | tests/helpers/baseline_locks.py | M | v1.3③(h) | 红-2 修复簇① | collector_to_channel+2 行;evolution_legal 绿/additions=13 |
| M-j | tests/test_phase3.py | M | v1.3③(j) | 红-3 修复 | L216 /13×13;CI exit=0 |
| M-k | tests/fixt.py | M | v1.3③(k)二选一=fixt | 红-4 修复 | +jp/ea 合成 payload;test_p01_fix6 CI exit=0 |
| M-锁1 | tests/test_p03_e2eb_b3.py | M | v1.2③(a)从属锁+v1.3 增 t06 | 计数/冻结/增集锁域化 | t01=94/93/v2.2.0/t02+3字段/t06=13;CI exit=0 |
| M-锁2 | tests/test_p03_final_acceptance.py | M | v1.2③(a)从属锁 | t11 计数锁域化 | t11=94/v2.2.0/93;CI exit=0 |
| **M-l** | **tests/test_p0_baseline_lock_equivalence.py** | **M(v1.4 新增)** | **v1.4③(l) 单点** | N3d 注入算术一行域化(v1.4 处置章;R060 重锚先例) | **仅 n3d_table_rows() 内 3 处行内(docstring 注记/注入行 `range(bl.W4_REPORT_ROWS_FLOOR-1)`/check 描述同步);其余断言零触碰;等价套件 31通过/0失败;CI exit=0** |

清单外零变更(AC-05);`git status`/`git diff --name-status 018d913..HEAD` 逐件可复核(018d913..65cf32f 段=v1.3 已提交面;65cf32f..终笔段=v1.4 增量=M-l+A6/A7+双文档续笔)。

## §二 验收要点逐条映射(L169 要点①-④)

| 要点 | 状态 | 证据 |
|---|---|---|
| ① economy 与 P1-P8(v1.3=P1-P10)一致性逐条+负向拒入【测试】 | **绿** | test_p1_wp_a T1(t1a-t1f,6测): 逐条 classify 独立重编码对账+聚合 US49/CN10/HK4/JP8/EA11/GLOBAL12+负向 3 fixture None+零未归类计数+12 候选落点(复用3禁双注册+9 append 尾) |
| ② 首份 jp_/ea_ 真实档在场【数据档引用】 | **绿(如实形态)** | `data/daily/jp_20261105.json`(4 系列,3 源 EXACT)+`data/daily/ea_20261105.json`(1 系列 ECB_MRO;ECB FM 轮换性 504+BBK reset→4 源 READ_FAIL 如实,缺席节键不出现;DAX/CAC40/JP_CPI_TOKYO 诚实缺席照 §零.12⑩ 预登记);锚定对比既有 25 件哈希零变化;采集 log×3 入证据包⑥ |
| ③ 新采集器离线测试(源失败→MISSING 不填0)【测试/CI】 | **绿** | test_p1_wp_a T3/T4(13测): 全成功/单源失败/全失败(→READ_FAIL+节缺席+exit1 不落盘)/零网络 mock 计数=0/诚实缺席键不出现/候选键口径核验负向 |
| ④ offline-tests 全套件零回归【CI】 | **绿** | 本地全量镜像(workflow 同构): **70 slots=69 exit=0+1 SKIPPED(test_glm_live)+FAILFLAG=0**;唯一历史红 N3d 经 v1.4③(l) 域化后等价套件 31通过/0失败;summary=证据包④ |

## §三 fixture→期望值映射(漂移维护策略之基;全 [示意·合成·值发明])

| fixture | 位置 | 期望锚(字面量) |
|---|---|---|
| fixt jp 节 | tests/fixt.py | BOJ_POLICY_RATE=0.100/prev 0.090;JGB_10Y=1.200/prev 1.180;JGB_2Y=0.500/prev 0.480;NIKKEI225 close=38000.00/high·low=null;inflation 键不出现 |
| fixt ea 节 | tests/fixt.py | ECB_DFR=2.00/ECB_MRO=3.15;BUND_10Y=2.60/prev 2.62;BUND_2Y=2.30/prev 2.35;EA_HICP_YOY=2.2/prev 2.4/change −0.2/MoM/Monthly;prices 键不出现 |
| T3 合成 raw | tests/test_p1_wp_a.py | SYN_MOF 末行 JGB 2Y=1.891/10Y=2.855 次新 1.870/2.830;FRED '.'跳过末值 0.743/prev 0.860;NIKKEI 末值 38000.25/series 3 点 |
| T4 合成 raw | tests/test_p1_wp_a.py | ECB 空值行跳过 DFR 末 2.00;MRO 3.15;HICP 2026-09→'2026-09-01' 2.2/prev 2.4;BBK 10Y 2.60/prev 2.62·2Y 2.30;meta 正例 9bis10/1bis2·反例 5bis10 |
| registry 期望 | tests/test_p1_wp_a.py+test_p03_e2eb_b3.py | 94/93/v2.2.0;聚合六值;四 JP 条目+3字段全冻结;t06 additions=JP4∪NEW9 |
| N3d 锚(v1.4) | tests/test_p0_baseline_lock_equivalence.py n3d_table_rows() | 注入行数=floor−1=81(锚定 bl.W4_REPORT_ROWS_FLOOR=82 冻结常量);T2 精确锁 81≠1+live 与下限锁 not(81≥82) 双咬合;live 演进零耦合 |

漂移维护策略(沿 R057/R060 形态): ①注册表演进→计数/聚合/冻结锁按 vintage 自适应面优先(expected_registry_count/vintage_additions),非自适应字面锁(94/93/v2.2.0)随提交域化,禁语义弱化;N3d 锚=冻结常量 floor−1,live 再扩容不再迁移;②采集器源端形态漂移→T3/T4 raw 注入件即最小回归面,新形态加 fixture 不改产线;③fixture 值变更须同步本表+对应断言(同提交);④P1-WP-B 接线轮(normalize_jp/ea+D7 解除)承接: _SOURCE_TO_INPUT 增键/fixt 通道键进快照 sources_status 断言/金题绑定面复核,均在 WP-B 合同面。

## §四 v1.4 处置实录(N3d 域化+真实采集+CI 终态;全过程=REPORT §零.16/§零.16.1)

- **N3d 域化(v1.4③(l))**: `range(expected_registry_count()-4)`(=90,≥floor82 不咬合)→`range(bl.W4_REPORT_ROWS_FLOOR-1)`(=81,双咬合);选 floor−1 弃 live 自适应=锚定冻结常量与 live 解耦+与 R060 迁移后锚值 81 数值连续;check 两条件子式逐字保持(禁语义弱化;weakened 反证算术见 n3d-sensitivity-check.log);v1.2 轮 §零.8.1 漏报 N3d 已在 §零.15 如实更正在案;v1.3 轮 commit message「28通过/2失败」vs 实录「28通过/3失败」差异亦以 §零.15 实录为准(不 amend)。
- **真实采集(要点②;零凭证零付费,白名单五域)**: jp 1 次全成(4 系列);ea 2 次零改参尝试(服务端 504/reset 瞬时形态,如实 READ_FAIL,终态 1 系列),全部尝试 log 入证据包;锚定=既有 25+13 件哈希零变化,新增仅 A6/A7 两档。
- **CI 终态**: 70 slots=69 exit=0+1 SKIPPED+FAILFLAG=0(ci-summary-v14.txt);CI dispatch 于最终尖端由操作者 CHECKPOINT 执行(登记件 rounds/044/P1-WP-A-CI-dispatch-evidence.md,执行Agent 不自行 dispatch)。

## §五 AC 自检摘要(v1.4 终态;逐条全文见 stdout 四段自述)

AC-01 绿(§零.1 抄录+v1.4 白名单增量 M-l 登记 §零.16)/AC-02 绿(要点①-④ 全映射,§二;DP 零载明判定+v1.4 定值登记 §零.16)/AC-03 绿(23+31 测+70 槽;漂移维护策略 §三;桩注入面=v1.3 已登记)/AC-04 绿(引用可寻;注入摘要标注)/AC-05 绿(018d913..终笔=A7[含已产 2 档]+M12[M-l 系 v1.4 新增恰 1 件];纯线性;分支尖端唯一新增)/AC-06 绿(本地 70 槽全绿+证据 zip 八类+DELIVERY 五节;CI dispatch=操作者 CHECKPOINT 面)/AC-07 绿(诚实缺席纪律三处落地;零 GLM/零凭证/零付费;网络面仅采集运行时白名单五域)。

## §六 证据包 zip 哈希终笔(AC-06.2;装配实测登记)

- `/tmp/p1-wp-a-evidence/IA-P1-WP-A-EVIDENCE.zip` sha256=**a4d7b439bc9fd2a4cf067233d9024075692736fc8c186bf0489471b2b6df1c88**(134 成员/578676 字节,装配时点 2026-11-05T15:57:33Z,装配 TIP=0c28e96);SHA256SUMS=zip 外 `/tmp/p1-wp-a-evidence/SHA256SUMS`(逐成员 134 行,**清单自身显式豁免不入 zip 自身**,沿 R019 审计 D3 措辞/R023/R060 先例);交付文件双源副本交叉哈希 0 失配(cross-hash.txt);推送终态(zip sha 行所在提交的尖端与 ls-remote 实取值)见证据目录 `08-sidecar/final-state.txt`(zip 内 DELIVERY 副本=0c28e96 装配时点版无本行,自指豁免)。
