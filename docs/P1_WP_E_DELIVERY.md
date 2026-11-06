# IA-P1-WP-E DELIVERY(交付件 · v1.4 涟漪迁移轮 · 状态=本地 75 槽全绿形态)

> 合同: IA-P1-WP-E-AC-v1.4(§十四处置章涟漪迁移续作;基点 BASE-P1E=ee66f3a9 同分支零重锚零重切)。
> 分支: dev/p1-impl-e((d) 登记轮 2 笔+v1.3 实施轮 2 笔+v1.4 涟漪轮续笔,纯线性零 merge;main 未触碰)。
> 数值标注纪律(合同 §5.3): 本文逐值 `[实取·来源]` 或 `[示意·非实取]`;六项自检与 REPORT §零.15/§零.17 同源成件(证据包成员⑤)。

## §一 交付清单与 M-d 演进表(逐项 1:1)

### 交付文件(授权项→DESIGN 依据→验证锚)

| 文件 | A/M | 授权(合同) | 验证锚 |
|---|---|---|---|
| docs/P1_WP_E_REPORT.md | A(扩写) | §十三.4 续作指定 | 证据包①②;REPORT §零.10-§零.16 |
| docs/P1_WP_E_DELIVERY.md | A(新建) | 附录A §零(ii) 必含件 | 本件;证据包② |
| tests/test_p1_wp_e.py | A(新建) | 附录A §零(ii) 含代码必含 | 本地全绿 25 用例;证据包④ |
| scripts/china_market_collector.py | M(a) | 冻结章 §十一.4(a)+§十三.4 | diff hunk 域内;T2/T3/T4/T5/T6 用例 |
| config/metric_registry.json | M(b) | 冻结章 §十一.4(b)+§十三.3 | 机器清点 102/101/'2.3.0'/CN 18/vintage 21 [实取·清点 stdout];validate_registry 零问题 |
| tests/test_p03_e2eb_b3.py | M(d) | §十三.1 恰 4 文件之一 | 演进表 E1-E4;本地全绿 28 用例 |
| tests/test_p03_final_acceptance.py | M(d) | §十三.1 | 演进表 E5;全绿 9 用例 |
| tests/test_p1_wp_a.py | M(d) | §十三.1 | 演进表 E6-E8(+E10 如实登记);全绿 23 用例 |
| tests/test_p1_wp_b.py | M(d) | §十三.1 | 演进表 E9;全绿 20 用例 |
| tests/test_p1_wp_c.py | M(e1) | §十四 (e1) 恰 1 位 | 演进表 E11;本地全绿 OK [实取·运行 log] |
| tests/test_e2e_frozen14.py | M(e2) | §十四 (e2) 恰 2 位 | 演进表 E12/E13;33 通过/0 失败 [实取·/tmp/frozen14-post.txt] |
| scripts/research_provenance.py | M(e3) | §十四 (e3) 恰 1 hunk | 演进表 E14;E2E-02d3 零改动复真 |

### M-d 从属锁域化迁移演进表(1:1 before/after;§十三.1「逐处 1:1 登记(演进表入 DELIVERY 对应节)」)

N=8(机器清点 [实取·§零.11];迁移值=数据驱动与 registry 实况 1:1)。

| # | 文件:函数/位置 | before(基线) | after(迁移) | 同型注记随迁 |
|---|---|---|---|---|
| E1 | test_p03_e2eb_b3.py t01 | `len(REG['metrics']), 94, '指标总数须恰为94(85+9)'` | `…, 102, '指标总数须恰为102(85+9+8)'` | +「IA-P1-WP-E v1.3 域化」注释行 |
| E2 | test_p03_e2eb_b3.py t01 | `active==93` | `active==101` | 同上 |
| E3 | test_p03_e2eb_b3.py t01 | `version, '2.2.0', '版本号须为2.2.0'` | `version, '2.3.0', '版本号须为2.3.0'` | 同上 |
| E4 | test_p03_e2eb_b3.py t06 | `vintage==JP4 \| NEW9(13)` | `vintage==JP4 \| NEW9 \| CN8(21)` | 头注 L18-21「94/93/v2.2.0→102/101/v2.3.0[+IA-P1-WP-E v1.3 域化: 94+8]」+CN8 集合定义 |
| E5 | test_p03_final_acceptance.py t11 | 方法名 `…_94_v220`;docstring「85→94/v2.1.0→v2.2.0/84→93」;`len==94`/`version=="2.2.0"`/`active==93` | `…_102_v230`;docstring 追加「IA-P1-WP-E v1.3 域化(§十三.1): 94→102(94+8)/v2.2.0→v2.3.0/active 93→101」;`len==102`/`"2.3.0"`/`101` | 方法名+docstring 随值同型 |
| E6 | test_p1_wp_a.py t1a | `len==94`/`version=='2.2.0'`/`active==93` | `len==102`/`'2.3.0'`/`101` | +域化注释行(94+8→102/93+8→101/2.2.0→2.3.0/CN 10→18) |
| E7 | test_p1_wp_a.py t1a | 聚合 `{'US':49,'CN':10,'HK':4,'JP':8,'EA':11,'GLOBAL':12}` | `'CN':18`(其余键不动) | 注释行追加「+CN 宏观八条目(P1:calendar=cn)」 |
| E8 | test_p1_wp_a.py t2d | `vintage=={JP4} \| set(NEW9)` | `… \| set(NEW9) \| set(CN8)` | +CN8 元组定义(L41-44)+「13→21」注释 |
| E9 | test_p1_wp_b.py t19 | `reg['version'], '2.2.0'  # 单字段≠版本变更`;`len(reg['metrics']), 94` | `'2.3.0'`;`102` | 注释更新:「WP-B 单字段≠版本变更原则不变;本值=WP-E 结构变更[+8 条目]所递增」 |
| E10 | test_p1_wp_a.py t1e **(授权面外同族·如实登记)** | `REG['metrics'][-9:]==NEW9`(尾块切片序锁) | `[-17:-8:]==NEW9`+新增 `[-8:]==CN8`(锁面净增强) | REPORT §零.13 第 10 位登记(发现过程+单一动因+处置权留操作者) |

- 迁移纪律遵守: 恰等仍恰等/比较符零改动/零删除断言/零 skip/E1-E9=授权面恰 9 位;E10=实现期发现同族位,**不在 §十三.1 恰 9 断言授权面内**,按「同族同型+单一动因(仅 M-b 纯追加致红)+净增强+零弱化」处置并全链披露(§五;stdout 第三段)。

### M-e 涟漪迁移演进表(v1.4 §十四 (e1)(e2)(e3);1:1 before/after;触发=M-b 纯追加直接且仅此一因)

| # | 文件:位置 | before(基线) | after(迁移) | 机器清点依据 |
|---|---|---|---|---|
| E11 | test_p1_wp_c.py t08(L269 assertIn 期望串) | `美国(US)=48项; 中国(CN)=10项; 日本(JP)=8项; 欧元区(EA)=11项` | `…中国(CN)=18项…`(仅 CN 段 10→18,US/JP/EA 三段不动) | registry v2.3.0 活跃计数派生运行实况 [实取·v1.3 轮运行 log+本轮迁移后 wp_c OK] |
| E12 | test_e2e_frozen14.py E2E-02d(L349-354) | `ga.get('noncore_missing') == ['CAC40','DAX','JP_CPI_TOKYO_YOY','UMCSENT']`(恰等 4 名单) | `== ['CAC40','CN_CPI_YOY','CN_LPR_1Y','CN_LPR_5Y','CN_NEW_LOANS','CN_OMO_7D','CN_PMI_MFG','CN_PPI_YOY','CN_SF_FLOW','DAX','JP_CPI_TOKYO_YOY','UMCSENT']`(恰等 12 名单,成员与序=机器输出逐字转录) | 迁移前实跑失败详情 `missing=[…12 成员字母序…]` [实取·/tmp/frozen14-pre.txt L15;入证据包成员⑥] |
| E13 | test_e2e_frozen14.py E2E-02d2(L364-367) | `rp.load_meta(...)['noncore_missing'] == ['CAC40','DAX','JP_CPI_TOKYO_YOY','UMCSENT']` | 同 E12 名单 4→12(与包 meta 实况 1:1) | 同 E12(包 meta 名单=快照 gate 同源同值) |
| E14 | scripts/research_provenance.py gate_reason_desc(L1228) | `','.join(ga['noncore_missing'][:8])`(截 8 渲染) | `…[:16]`(渲染帽 8→16;core_missing L1223/core_fail L1225 `[:8]` 不动;文件其余零触碰) | §十四 (e3) 裁决=FIX4-03 意图恢复;E2E-02d3 断言零改动复真=本轮实跑证实 [实取·/tmp/frozen14-post.txt 33/0] |

- 迁移纪律遵守(M-e): 恰等仍恰等(4 位比较符零改动)/零删除断言/零 skip/零弱化/三文件其余内容零触碰(diff hunk 对照=恰 3 文件 4 hunk);E11-E14=§十四授权面恰 3 文件 4 位(E10 已由 §十四追认,归 M-d 面,无进一步动作)。
- 陈旧注记登记(授权面外零实施): test_p1_wp_c.py L267 注释(v2.2.0/CN10)与 test_e2e_frozen14.py L348/L365 GAP08 时点注记(前=['UMCSENT'])在本轮恰 N 位让渡边界外,未动,留操作者裁量(REPORT §零.17 登记发现项)。

## §二 验收要点逐条映射(DESIGN L173;正文=REPORT §零.14)

① 断点修复(china 档对应节非空)→ 备源切换代码面+离线注入验证(T2/T3/T4);真实档非空=操作者排程运行面(零运行产物声明,§五)。② 源端失败注入→MISSING/缺席披露 → T6/T4 恰等锁(全失败→{};单点失败独立;OMO PENDING)。③ 宏观新指标 registry 条目+单测 → M-b 八条目+T1 全套;CI=操作者 CHECKPOINT(rounds/048 登记件)。

## §三 漂移维护策略专节(AC-03.6 三要素;AC-03 生效=登记清单含 .py)

1. **预期值唯一来源=仓库内版本化合成 fixture**: tests/test_p1_wp_e.py 全部期望值为字面量硬编码,唯一数据源=本文件合成 fixture 函数(sse_margin_df/szse_margin_df/legu_pe_df/lpr_df/jin10_cpi_df/jin10_ppi_df/pmi_df/shrzgm_df/nfc_df/OMO_LINES,值全发明 [示意·合成·值发明]);不 import 被测模块计算预期(禁自证恒真)。
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: 本 commit 内 fixture 与其恰等断言一一对应成对出现;后续演进须同 commit 同步(本表为对照锚)。
3. **真实数据档永不进入测试预期值来源**: 零读取 `data/daily/`(grep 可证: 本文件无 data/daily 路径字面量);akshare/tushare 全 mock 注入,零网络。

**fixture→期望值映射**(逐断言组→fixture 定义处;AC-03.6/R022 同款):
- T2 t20/t21/t23 → sse_margin_df(L116-134)/szse_margin_df(L136-142): 两所同日合计算术(rzye/rqye/balance 硬编码)。
- T2 t22a/t22b → 同上+空 pd.DataFrame: 失败/无配对→None。
- T3 t30/t31/t32 → legu_pe_df(L144-149): 完结行选择(在途行禁用)+pe/date/via/note 恰等;列漂移→None。
- T4 t40/t41/t42 → lpr_df(L151-159)/jin10_cpi_df(L161-167)/jin10_ppi_df(L169-174)/pmi_df(L176-183)/shrzgm_df(L185-189)/nfc_df(L191-196): 七产出键值/日期/源标签恰等;NaN 最新行跳过;单点失败独立。
- T5 t50-t55 → OMO_LINES(L198-204)+内联字面量: 解析形态/去重/today 冻结/注入面末行。
- T6 t60/t61 → 全端点 OSError 桩+OMO_LINES: {} 零 0 填充;PENDING 缺席披露。
- T1 t01-t06 → 生产 config/metric_registry.json 实读(注册表锁,非合成数据面;期望值=域化迁移定值,与 §一演进表 1:1)。

## §四 AC 自检摘要(逐条全文=stdout 四段自述第 4 段)

AC-01 PASS(§零.2 复核逐字一致+§零.3 清单)/AC-02 PASS(§零.14 三要点映射齐;要点①真实运行面=零运行产物如实声明非漏检)/AC-03 PASS(AC-03 生效: 25 用例全绿+§三策略专节+映射;v1.4 轮涟漪修正后全量 75 槽全绿)/AC-04 PASS(file:line 逐条可寻;注入内容已标注)/AC-05 PASS(diff=M 授权域恰 9 文件(a×1+b×1+d×4+e×3)+A 恰 3;E10 披露位见 §五;纯线性零 merge;LIVE 零写入;零网络)/AC-06 执行席面: 本地全量 **75 槽全绿(74 exit=0+1 test_glm_live skipped,nonzero=0)** [实取·local-ci-v14-per-suite.txt];证据包八类;CI dispatch=操作者 CHECKPOINT 待办(§十四 CI 前置已满足)/AC-07 PASS(纪律登记 §零.4 承接;零真实调用零凭证零付费;零投资建议)。

## §五 如实偏差与登记

1. **E10 授权面外同族断言位**(§一演进表): 发现过程/单一动因/处置与处置权留操作者=REPORT §零.13 末条 [实取·迁移后本地复跑 FAILED 现场复扫];非静默,全链三处登记(REPORT/本表/stdout)。
2. **CN_OMO_7D 源缺席(PENDING 身份预注册)**: akshare 1.18.47 无逆回购接口 [实取·安装包源码 grep 零命中]→active 条目+source_symbol='PENDING'+纯解析函数交付+默认装载器 None(JP_CPI_TOKYO_YOY 先例);registry frequency='daily'=§十三.2 裁决承载。
3. **零运行产物声明(AC-02 要点①运行面/AC-06 成员⑥)**: 本包未运行任何真实采集编排(china_*档零新增零改动);真实数据获取=门②开后操作者排程面(免费公开源预授权③);故要点①「数据档引用」面=备源函数交付+离线注入验证,真实档非空验证属操作者运行面。
4. **套件数 74→75**: BASE-P1E-CI-SUITES=74+新增 tests/test_p1_wp_e.py 1 件=75 [实取·本地全量逐件运行计数];实况=73 绿+2 红(红件=§五.6 涟漪,非回归);CI 端=操作者 dispatch 后按 AC-06.1 对照(74+1 零回归,涟漪件同口径注记)。
5. **估值备源口径**: 乐咕=上证主板平均市盈率,注册 SH_PE=上证整体 PE(TTM) 近似代理,note 键如实披露(禁静默混同;REPORT §零.6A/§零.12)。
6. **全量运行涟漪发现(授权面外 2 文件 4 断言位;情形(b) 常规分流,零改动)**〔v1.3 轮原文,历史记录〕: `tests/test_p1_wp_c.py` t08(L268)静态披露串 `中国(CN)=10项`→实渲染 18 项(registry 活跃计数派生);`tests/test_e2e_frozen14.py` E2E-02d(L346-353)/02d2(L354-362) noncore_missing 恰等冻结 4 名单→实值 12 项(原 4+CN8)、E2E-02d3(L363-369) `'UMCSENT' in rmd` 败于 research_provenance.py:1228 `[:8]` 截断渲染(UMCSENT 序位 12 落出可见文本)。单一动因=M-b 纯追加;两文件不在 §十三.1 恰 4 文件授权面(第 5/6 文件=越域),零改动如实登记,处置建议=仿 GAP08-F3 (j) 涟漪先例授权后续迁移工作包(t08 值 10→18;名单扩 CN8;02d3 断言名稳定化或渲染面单独授权)。详情=REPORT §零.13A [实取·/tmp/wpe_run/SUMMARY.txt+运行 log]。→ **v1.4 处置闭合**: 操作者 §十四 (e) 授权(2026-11-06),本项涟漪已按 (e1)(e2)(e3) 恰 3 文件 4 位迁移落定(演进表 E11-E14),本地 75 槽全绿,处置建议全部承载(02d3 走 (e3) 渲染帽路径)。
7. **v1.4 轮如实登记(涟漪迁移)**: ①机器清点纪律——E12/E13 名单成员与序=迁移前实跑 frozen14 失败详情输出逐字转录(禁手抄;证据包成员⑥ v14-e2e-machine-count-basis.txt),迁移后 33/0 全绿复验 [实取·/tmp/frozen14-post.txt];②E14 渲染帽 8→16=§十四 (e3) 单 hunk 授权(core_missing/core_fail `[:8]` 两行不动,e2eb_query_executor/data_assembler/report_generator 消费面均为长度容忍形态,grep 复核无其他断言依赖截断渲染) [实取·grep];③陈旧注记两处(wp_c L267/frozen14 L348+L363)在恰 N 位让渡边界外零实施,登记发现留操作者(REPORT §零.17);④E10 已追认归档,无进一步动作。

## §六 证据包 zip 哈希终笔(AC-06.2;装配后终笔登记,本节值=装配时点实测;v1.4 轮重装配)

- 证据包: /tmp/p1-wp-e-evidence/IA-P1-WP-E-EVIDENCE.zip(v1.4 轮完整八类成员+SHA256SUMS zip 外自指豁免,R019 审计 D3/R023/R060 先例)。
- 定值(装配 stdout 与独立复算 shasum/unzip 双通道一致): **成员 18 件/97961 字节/sha256=ee91bd4de5ff47000148c8bb0e6b338233f072fa320d6afa18947a2da325a0e6** [实取·装配 stdout(Python zipfile testzip=OK+逐成员 18 哈希全匹配)+shasum -a 256 独立复算同值,2026-11-06T11:0xZ UTC];SHA256SUMS 18 行 zip 外自指豁免。
- 历轮旧包保全(禁止静默覆盖消灭): (d) 轮=IA-P1-WP-E-EVIDENCE.d-round-archived.zip(sha256=f8905d00…1a81ce6df,与 340c8e1 终笔登记值逐字一致 [实取·保全时点复算]);v1.3 轮=IA-P1-WP-E-EVIDENCE.v1.3-round-archived.zip(sha256=4662f906029f34cc08984a179000b12d8e1b188481018ad05e25e30fe55d9a22,与 be69968 终笔登记值逐字一致 [实取·2026-11-06T10:5xZ 保全时点复算])。
- TIP=装配时分支尖端(v1.4 涟漪笔,见 git 取证成员③);zip 内 REPORT/DELIVERY 副本=装配时点版(不含本节终笔值,如实披露);终局自述以会话 stdout 四段为准(R023 先例)。
