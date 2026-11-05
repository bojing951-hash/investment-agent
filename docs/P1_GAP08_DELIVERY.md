# IA-P1-GAP08 DELIVERY(快照接线+研究消费面收口轮交付件)

- 工作包: IA-P1-GAP08-WIRING-AC-v1.1(R061;合同 sha256=69555cf7b112e89acabcb4cd119c97fcf7a4807239fb5f004f0de8ac5e7ebe1d)
- BASE-GAP08: 82d41e214b99f09bf4521c137261f61f17a3e5ff(=origin/main 开工 ls-remote 实取)
- 分支: dev/p1-gap08(自 BASE-GAP08 切出,纯线性,零 push/零 amend/零 force)
- 本地 CI 镜像: 74 槽=73 exit=0+1 test_glm_live SKIPPED(逐件退出码=证据包④类;CI dispatch=操作者 CHECKPOINT 面)
- 配套: docs/P1_GAP08_REPORT.md(§零 登记+§一-§六 实录)

## §一 改动清单(diff 预期: M8+A3+条件类 (j) 5 件;合同宣 M9 为计数滑笔,REPORT §零.3 登记)

| 类 | 文件 | 面 |
|---|---|---|
| M-a | scripts/snapshot_builder.py | F1(L335-351+适配器 L234-262)/F6(L352-373)/F2(L450-469) |
| M-b | scripts/research_provenance.py | F3 三键(L117-124);SOURCE_FILE_RULES/SOURCE_CHANNELS 零改 |
| M-c | scripts/research_task_manager.py | R47-F1 economy 条件写(L56-76/L151-155) |
| M-d | scripts/research_history_query.py | R47-F3(ACCESS_POINTS/ECONOMIES/economy echo/过滤参数/CLI) |
| M-e | tests/fixt.py | F4 三处注释勘正(L197-200/L214/L218-220),零功能 |
| M-f | docs/P1_WP_B_REPORT.md | L20 单行勘正+§零.9 F1-F6 承接回填注记 |
| M-g | docs/P1_WP_C_DELIVERY.md | §三 AC-05 v1.2 注记+§五.2 勘误族注记 |
| M-h | docs/P1_WP_D_DELIVERY.md | §五 辅锚勘正(L165-179)+§七 F1/F3 承接回填 |

(M 白名单=合同 §零 表列 8 行 (a)-(h);合同文面"M 恰 9"与表列 8 行计数不一致=滑笔,如实登记于 REPORT §零.3;零表外文件改动。)
| A1 | tests/test_p1_gap08.py | 新增(13 测/6 类,首次运行即绿) |
| A2 | docs/P1_GAP08_REPORT.md | 新增(本件配套) |
| A3 | docs/P1_GAP08_DELIVERY.md | 新增(本件) |
| (j) | tests/test_p1_wp_a.py | t2c: 三键冻结态断言→三键映射断言(1 处) |
| (j) | tests/test_p1_wp_b.py | t13/t14/t16/t18: boundary→noncore_missing 口径翻转(4 处) |
| (j) | tests/test_p1_wp_c.py | L438: gate PASS→DEGRADED(1 处) |
| (j) | tests/test_gate_chain_p01.py | PASS 日声明一致族 5 处 check 值翻转 |
| (j) | tests/test_e2e_frozen14.py | E2E-02d/02d2: noncore_missing 名单扩三指标(2 处) |

fact_engine.py/china_market_collector.py/metric_registry.json/LIVE/launchd/.github/.gitignore/test_glm_live/data-daily: diff 零涉。

## §二 运行与验证摘要

- 新套件: tests/test_p1_gap08.py 13/13 绿(Ran 13 tests, OK;全合成 fixture+[实取] registry 只读;零网络零 GLM)。
- 负向敏感性: 3 注入(删 F3 jp 键→3 红/禁 F1 jp 接线→2 红/删 F2 ea 池→1 红)全部复原复绿,pre/post sha256 双文件全等=零残留(证据包④类)。
- 本地全量: 首跑 74 槽=70 绿+3 红(wp_a/gate_chain_p01/e2e_frozen14)→逐处诊断=F1/F3 直接涟漪属 (j) 覆盖→13 处 1:1 勘正(§五演进表);**终跑 74 槽=73 exit=0+1 SKIPPED 全绿**。
- 真实运行面: 零运行产物(要点均【测试/CI】限定;data/daily 三档 sha 运行前后一致;零 GLM/零网络/零凭证/零付费)。

## §三 合同 AC 逐条自评摘要(全文自检=stdout 自述段3;判据细节=REPORT §一-§五)

- AC-01 规格链五源抄录: 自评**过**(§零.2 逐字锚+行号 grep 实测;引擎侧三条标注「注入」+DEV 侧在场性实证)。
- AC-02 七项授权面全落地: 自评**过**(REPORT §五 映射恰 10 行+F5 排除表尾)。
- AC-03 测试与确定性: 自评**过**(①13 测覆盖 F1/F2/F3/F6/R47-F1/F3 全项;②74 槽终跑全绿逐件退出码;③预期值全硬编码字面量+registry 只读实取;④3 注入红绿转换零残留;⑤§五 漂移三要素+映射表;⑥涟漪 13 处 1:1 演进表禁弱化)。
- AC-04 引用真实性: 自评**过**(行级引用 grep 实测±3 行内;注入摘要标注;否定性声明附反证命令=证据包⑤类)。
- AC-05 范围/分支/生产隔离: 自评**过**(diff=M9+A3+(j)5 件逐处登记;纯线性 reflog 佐证;45 支零漂移唯一新增 dev/p1-gap08;main/registry/china/LIVE/launchd 零触碰;三档 sha 复算一致)。
- AC-06 CI 与证据包: 本地镜像已录;**CI dispatch=操作者 CHECKPOINT 面**;证据包八类+SHA256SUMS 自指豁免=§四。
- AC-07 研究纪律: 自评**过**(缺席照实披露不填 0 不造数;零投资建议文案;DP 零新增;状态档/W4/W5 零触及;白名单外发现 REPORT §四 PENDING 不越界)。

## §四 证据包登记

- 路径: /tmp/p1-gap08-evidence/IA-P1-GAP08-EVIDENCE.zip(八类成员: ①规格链五源抄录件 ②双源副本(交付文件 git 尖端版+工作树版交叉哈希) ③git 取证(diff name-status/rev-parse+log 线性/reflog/ls-remote 全表) ④本地 CI 镜像 74 槽逐件记录+负向注入日志 ⑤LIVE 隔离+红线反证命令输出 ⑥逐要点映射表+DP 登记副本 ⑦自述报告副本 ⑧SHA256SUMS——清单自身显式豁免不塞入 zip,R023/R060 先例)。
- (zip 哈希终笔=§六,装配后回填;zip 内 REPORT/DELIVERY 副本=装配时点版,终笔定值以本件 §六 为准,先例沿 WP-B/WP-C/WP-D。)

## §五 漂移维护策略声明(AC-03 三要素)+fixture→预期值映射+(j) 演进表

1. **预期值唯一来源=仓库内版本化合成 fixture**: 本包测试一切期望值来源于 tests/fixt.py 合成载荷与 tests/test_p1_gap08.py 内显式发明值([示意]标注)+registry 只读实取([实取]标注: g10 economy 值域/锚值),不依赖 data/daily 真实档。
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: JP_F1_EXPECT 十指标值映射(test_p1_gap08.py L50-63)与 fixt.py jp/ea/japan 节(L196-276)同 commit 冻结;fixture 路径锚定: fixt.py L40(collector_payloads)/L201-210(japan data)/L220-243(jp)/L244-274(ea)。
3. **真实数据档永不进入测试预期值来源**: 测试零读取 data/daily;真实三档(jp/japan/ea_20261105.json)仅 §零.1 sha 红线核验与 REPORT 文字引用,不入断言。

fixture→预期值映射(逐断言组→定义处):

| 断言组 | fixture 定义处 | 预期值形态 |
|---|---|---|
| g01 F1 十事实 | tests/test_p1_gap08.py:50-63(JP_F1_EXPECT;fixt L201-210/L220-243/L244-274) | 值+权属+批次文件名字面量 |
| g02 缺源披露 | tests/test_p1_gap08.py:104-125 | MISSING+来源级缺失理由串字面量 |
| g03 F2 三键 | tests/test_p1_gap08.py:139-163(档内 series 直通复核) | {dates,values} 字面量+逐值回读比对 |
| g04/g05 F3 双分支 | tests/test_p1_gap08.py:164-203 | 采集遗漏/来源缺失理由串字面量 |
| g06 F6 对账 | fixt.py:226-236(policy/jgb 值)+japan data 值 | consistent+差+0.0000 子串 |
| g08/g09 R47-F1 | registry economy 字段(TIPS_10Y=US/GOLD_F=GLOBAL/UST_*=US/NIKKEI225=JP) | 派生值/None 条件写 |
| g11/g12 R47-F3 | fixt.py:233-236(NIKKEI225 series)+registry economy | [2026-10-29,2026-11-05]/[37800.0,38000.0] 字面量 |

(j) 涟漪演进表(13 处 1:1 before/after;禁删/禁 skip/禁语义弱化):

| # | 文件:断言 | before | after |
|---|---|---|---|
| 1 | test_p1_wp_a.py t2c(更名 t2c_d7_boundary_preserved→t2c_d7_source_to_input_wired) | 三键 assertNotIn(边界冻结态) | 三键 assertEqual 映射值 jp/ea/japan;SOURCE_CHANNELS 冻结断言不动 |
| 2 | test_p1_wp_b.py t13(更名 …boundary_excluded→…missing_flipped) | JP13 全员 assertNotIn noncore_missing+boundary 7/3 项 | 在场者不入/缺席者入 noncore_missing(F3 翻转面)+boundary 0/0+缺席收敛 3 项集合断言 |
| 3 | test_p1_wp_b.py t14(更名 …absent_boundary_legal_registration→…absent_noncore_missing_after_mapping) | boundary=13+"无法映射采集通道"文案 | boundary(JP13 面)=0+noncore_missing=13 全员+采集遗漏理由串×2 |
| 4 | test_p1_wp_b.py t16 | boundary=13 | boundary=0+noncore_missing∩JP13={JP_CPI,DAX,CAC40}+status=DEGRADED |
| 5 | test_p1_wp_b.py t18 | facts/quality 全等+noncore_missing 全等 | US 面过滤后 facts/quality 全等+新增事实恰 10+gate 同级 DEGRADED+JP13 面 3 vs 13 如实分列(US 面零回归语义保持) |
| 6 | test_p1_wp_c.py L438 | gate status=='PASS' | gate status=='DEGRADED'(F3 口径翻转注记) |
| 7 | test_gate_chain_p01.py check"真实快照gate_status读取PASS" | got=='PASS' | expect='DEGRADED' if st=='PASS'(重算裁决非盲信语义不变) |
| 8 | test_gate_chain_p01.py check"裸字符串(兼容)" | gate_a='PASS'/got=='PASS' | gate_a='DEGRADED'/got=='DEGRADED'(兼容分支不变) |
| 9 | test_gate_chain_p01.py check"上下文携带Gate A" | ctx['gate_a']=='PASS' | =='DEGRADED' |
| 10 | test_gate_chain_p01.py check sidecar | final_quality/gate_a=='PASS' | =='DEGRADED'×2(gate_b=='PASS' 不变) |
| 11 | test_gate_chain_p01.py check footer | '数据质量降级披露' not in 报告 | in 报告(DEGRADED→footer 在场) |
| 12 | test_e2e_frozen14.py E2E-02d | noncore_missing==['UMCSENT'] | ==['CAC40','DAX','JP_CPI_TOKYO_YOY','UMCSENT'] |
| 13 | test_e2e_frozen14.py E2E-02d2 | load_meta noncore_missing==['UMCSENT'] | ==同上四元名单 |

## §六 zip 哈希终笔登记
(装配后回填)