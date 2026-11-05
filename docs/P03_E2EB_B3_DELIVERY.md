# P03 E2EB WP-B3 交付文档(IA-P03-E2EB-WP-B3-AC-v1.4 案A回做版 / R023)

任务: 日本利率数据身份与获取——注册表 81→85、japan 通道登记、
japan_rate_collector 采集器、真实采集落档、四文件演进域化迁移、离线测试锁。
REPORT(docs/P03_E2EB_B3_REPORT.md)载登记全稿(D1-D17)与预期红面;本文件为
交付视图,重复处以 REPORT 为登记权威。

## §零 基线实读与登记型决策点摘要

基点 `04ead6d`(R058 merge,分支 dev/p03-e2eb-b3,operator-reset)。§零 全量
登记见 REPORT §零.1-§零.6: 规格逐字转写、M1-M6/A1-A5/D=0 白名单、无 (d) 级
冲突、D1-D17 先登记后实现、预期红面表(fix6 B[japan]×4/w4 d2×1/equivalence
Z0+R[legal85]+四电池)、白名单外零触碰红名单。要点: D6 SOURCE_CHANNELS 四通道
冻结;D7 _SOURCE_TO_INPUT 有意不加(缺席走 noncore_missing_boundary 边界记录);
D5 四条目 important 非 core;D11 全字段冻结与 A3 硬编码三方一致;D13 可选⑦取
映射表分类(不追加 N8 等价用例——等价套件为 R057 冻结 M 件)。

## §一 交付清单与分支谱系

分支: `dev/p03-e2eb-b3`(自 04ead6d 切出,纯线性提交,零 merge/零 rebase/零
force;main/legacy 零触碰)。diff 统计: 8 M 件 +195/−17,3 A 件(REPORT/
collector/A3)+1 A 件数据档+本 DELIVERY。

| 类 | 件 | sha256(工作树终态) |
|---|---|---|
| M1 | config/metric_registry.json | 63fe1cbf0735606afcfc7cf59378e7134e8ef1ca2cbc7acf155076398e93f68a |
| M2 | scripts/research_provenance.py | e4af2acff6e00eaeba9924b3a337f4b442686337ccdc04a4670962e34905fa5a |
| M3 | scripts/registry_semantics.py | 5e1fa786f84d7001f9f8f91be65b69fd8a186818c18c8b4db455d7070d78db4b |
| M4 | scripts/trading_calendar.py | df3b1c759a82b38b3b1e8b2df4de4f4b2e45cd4cf4780ab70388555b80054ca9 |
| M5 | tests/test_e2e_frozen14.py | 684f810ed56341f4a4e981efb387ee0629d1e2a0cbfb9c982a1dc2cd3bada49b |
| M5 | tests/test_e2e_orig14.py | 1fcd78bce9efd06531a6b3ba8eaf8302965b4fed4908888c47e973c7930c8878 |
| M5 | tests/test_gate_chain_p01.py | 1615301a5ec2d949edd8d7c2b4aa6c968649ff4faf4b1811fecbe0768c5bd8bb |
| M5 | tests/test_fact_engine.py | 929eeeb12ff2ad0ace70073f97b50b3844a937543d1b5fc5abed0d8679e8c8e2 |
| A1 | scripts/japan_rate_collector.py | e2aa06cd958961464031d9a875aeb2c58e5aa20f9d68ac3f8adbcb9344bd5d8b |
| A2 | data/daily/japan_20261105.json | 6bba4718759ba12546499c1bdc510a1157b87f9462408e14071967d29e14e7f1 |
| A3 | tests/test_p03_e2eb_b3.py | 4e8a2b72357c342103f176b556fa5c50a23e2650ad773f0586455436c7ccc317 |
| A4 | docs/P03_E2EB_B3_REPORT.md | 装配时点见 SHA256SUMS(REPORT 先于 zip 定稿) |
| A4 | docs/P03_E2EB_B3_DELIVERY.md | 本件(装配后 zip 哈希终笔按 R058 自指豁免先例) |

D 行: 无(D=0)。白名单外字节级零触碰(mfile_sha256.txt 断言 SAME):
snapshot_builder.py / fact_engine.py / historical_coverage_audit.py /
tests/helpers/baseline_locks.py / tests/fixt.py /
test_p0_baseline_lock_equivalence.py / test_p01_fix6.py / test_p02_w4.py、
launchd/LIVE/CI 配置、data/daily 现存 16 档(daily_pre/post.sha256 零变化)。

## §二 实现摘要

身份层: 注册表 85 条(active 84,v2.1.0)新增 JP_POLICY_RATE+JGB2Y/5Y/10Y
(important 非 core;percent;japan 日历;range [-0.5,2]/[-0.5,15]+周动 1.0;
freshness 60 月频注记/7;release_semantics 按 MOF/FRED 发布口径保守登记)。
通道层: SOURCE_FILE_RULES+japan(japan_ 前缀,5 自然日回退)→ snapshot_builder
SOURCES 自动派生(零 sb 改动);SOURCE_CHANNELS 四通道迭代域冻结不动(历史快照
兼容);_SOURCE_TO_INPUT 有意不加→演进日 JP 缺席入 noncore_missing_boundary
(边界记录,不入 noncore_missing,不影响 gate)。日历层: tc.MARKETS+japan,
最小集(周末+01-01+12-25,保守宁多勿漏,2026-11-03 文化日如实 True)。
采集层(A1): 标准库-only;MOF jgbcme Shift_JIS 列头映射取最后合法行;FRED
fredgraph '.'跳过取最后有值行;逐源 UA(FRED 对陌生 UA 挂起→'curl/8.0 前缀+
身份'实测登记);单源失败→缺席+alerts;全缺→exit 1 不落盘;原子写。
真实采集(A2): 2026-11-05 一次运行,mof.go.jp+fred.stlouisfed.org 白名单域
零凭证;观测日逐系列如实(JGB 2026-11-04 / policy 2026-09-01)不冒充运行日;
alerts=[]。

## §三 测试面(离线锁,零网络零 skip 零删断言)

**A3 新增** tests/test_p03_e2eb_b3.py: 28 用例全绿(T1 身份 6/T2 通道 5/T3 日历
2/T4 采集器 11/T5 一致性+真实档 4);合成 fixture 复刻 D12 锚定值为期望常量;
真实档全文 sha256 冻结;沙箱 build_snapshot 生产链集成(japan EXACT+四通道
MISSING+gate FAIL/core_missing);负向: 超回退窗 MISSING、坏日历日期/跨通道/
路径成分拒、期限坏值缺席+告警、MOF/FRED 单源失败降级、双源失败 n==0 且
main exit 1 不落盘。

**演进域化迁移表(D14;1:1 before→after;四套件迁移前后均绿=纯域化)**

| 套件(现态) | 迁移点 before → after | 语义 |
|---|---|---|
| test_e2e_frozen14.py (33/0) | E2E-01a: `snap['gate_a']['status']=='PASS'` → `bl.gate_vintage_ok(_ga01)[0]`(PASS 恒真;DEGRADED 仅 core 桶空且 noncore_missing⊆演进新增合法) | Gate-PASS 锁族 R057 形迁 vintage 域,基线指标静默死亡仍红 |
| 同上 | E2E-01b: `meta.get('gate_a')=='PASS'` → `meta==快照实际 gate 且 vintage 合法` | 一致性绑定强化(声明须与权威实际值一致) |
| 同上 | E2E-01c: `final_quality=='PASS'` → `==combine_gates 精确一致`(_exp_fq 按 gate_a 实际值推导) | 绑定快照实际值,非弱化为任取 |
| test_e2e_orig14.py (43/0) | 场景7声明改写前**新增前置**: `rp.gate_status(snap)重算恰为请求gate` | 域化旁证(fixture 标签→重算对齐);声明冲突语义零变化 |
| test_gate_chain_p01.py (88/0) | 三态循环后**新增两检查**: 合成 PASS 快照 vintage 合法;合成失败日 DEGRADED(noncore_fail 非空)**被 vintage 拒绝**(`not _okv and 'noncore_fail' in _whyv`) | 正反旁证:vintage 锁区分演进日与失败日,防洗白 |
| test_fact_engine.py (61/0) | g10 分级检查后**新增一检查**: JP 四条目⊆vintage_additions 且 overall==PASS | 身份登记不拉低在场事实分级(接线属 E2E-B) |

**全量真实运行(69 件,fullrun-logs/)**: 66 PASS / 3 RED,零意外红;三红面与
REPORT §零.5 预登记逐项吻合(fix6 86/4 全为 B[japan];w4 d2×1;equivalence
25/6=Z0/N1a/N3d/N5d/N7b/R[legal85])。路由 **(b) 上游漂移诚实报告**: 三红全为
R057 冻结锁族对新通道的未覆盖面(bl 冻结 4 采集器映射/hca 冻结映射/fixt 冻结
fixture 域),非本包缺陷,禁当场改,修复归重冻轮(§五)。非常规件如实注记:
test_glm_live 自护栏跳过(RUN_GLM_LIVE 未设,零 GLM 触碰);fixt.py 直跑 exit 0
且 tests/fixtures 零变化;69=实验宇宙 66+A3+fixt+glm_live。

## §四 证据包

`/tmp/p03-e2eb-b3-evidence/IA-P03-E2EB-WP-B3-EVIDENCE.zip`——九类成员:
①合同/设计引用件 ②REPORT/DELIVERY 稿 ③M 件 diff+sha256 前后对照(含白名单外
8 件 SAME 断言) ④A 件+指纹 ⑤真实采集原始回执(real/jgbcme.csv+
real/irstci01jpm156n.csv) ⑥D16 证据快照(digest=8dc327664b8309fb;japan EXACT
sha256 全值;gate_a=DEGRADED vintage 合法;noncore_missing=china 档既有
[MARGIN_BAL,SB_FLOW,SH_PE];noncore_missing_boundary=JP 四条目恰) ⑦data/daily
前后指纹 ⑧实验+全量日志(exp-logs/ 66、fullrun-logs/ 69、工具脚本)
⑨SHA256SUMS 全成员清单。

## §五 漂移维护三要素与未尽事项

**三要素**(重冻时点=后续轮,禁本轮顺手):
1. **冻结面扩展**: bl.evolution_legal 采集器映射+baseline_locks 电池算术锚
   (live=85 重校准)、hca.REGISTRY_SOURCE_CHANNEL 映射、fixt B 循环 japan
   fixture、w4-d2 词表——四点合一轮重冻(重冻轮自证 N5d/R[legal85] 复绿);
2. **红面清单**: 本轮 (b) 三件(REPORT §三表)即重冻轮验收基线,重冻前不得
   作为回归信号误读;
3. **锚定值登记**: D12 实测锚定+真实档 sha256+A3 硬编码三方绑定,后续源端
   改版(如 MOF CSV 形态/FRED 系列 id)时 A3 先红=感知点,修复按"新锚定实测
   →登记 → 同步三处"流程,禁单点改。

**未尽事项**: ①JP 四条目事实提取接线(source→input 映射+japan 档→事实流)
属 E2E-B 分轮,本包 D7 边界记录即其占位;②BOJ 政策利率决议值口径(与月均
operative 值差异)已在 release_semantics 登记,决议值指标化留待需求轮;
③CI dispatch 登记件(rounds/023)归操作者动作,不在本执行器白名单;
④zip 哈希终笔见下。

## zip 哈希补记(装配后追加;自指豁免: 上方 zip 内 DELIVERY 副本无本行)

IA-P03-E2EB-WP-B3-EVIDENCE.zip sha256 = 0f14d11f895ed8b2695d9e912831ee3915eed990615bb4869d93899ea1a09232 (187成员/674941字节, 装配时点TIP=378fd04, 装配后实测; zip外终态见证据目录08-sidecar/final-state.txt)
