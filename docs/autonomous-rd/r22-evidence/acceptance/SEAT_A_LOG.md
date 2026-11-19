# Seat-A 判断席全程日志(Audit-R22 一问验收)

工单原文: `/tmp/r22/run_question_verbatim.txt`
隔离树: `/tmp/r22`(CODE_VERSION.json 印章=b45b810)

## 步骤记录

### 1. 环境核验
- 20261119 通道面在位: data/daily/{china,ea,global,jp,japan,macro,shiller}_20261119.json + jp/japan/ea_20261105.json + hk_index_history.json(11 件)
- 快照缺席(research_snapshot_*.json 不存在)

### 2. 正式计划(plan)
- 命令: `python3 ia_cli.py research-one --stage plan --question "$(cat run_question_verbatim.txt)" --out-dir output/r22map --engine-root /tmp/r22`
- 首跑(20261119T153521Z): run_ok=False——S3/S5/S6/S7/S8 全 False,notes=「地图计划指标缺数」22 项。根因=快照缺失(该命令并未自建快照)。
- 用本树代码自建快照(纯本地,不改代码): `python3 scripts/snapshot_builder.py --date 20261119`
  → research_snapshot_20261119.json 落盘,事实 95,Gate A=FAIL(core_missing=[CN_TOTAL_TURNOVER, DFEDTARL, DFEDTARU, DFF, SH_AMOUNT, ZQ_IMPLIED_AVG];既有源端缺口,如实披露面)
- 重跑 plan(20261119T153709Z): **run_ok=True**,全部 61 步 True。run 目录:
  `output/r22map/20261119T153709Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最`
- notes(缺数披露,不阻断): US_REAL_GDP、CORE_PCE、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY、JP_CPI_YOY(=窗口内缺数/锚可见性注记,点值面逐格呈现)

### 3. 判断席真产出(agent_judgment.json)
- 读面: AGENT_SEAT_ENVELOPE.json(68 证据行/三时点锚 2025-11-19、2026-08-19、2026-11-19/资产宇宙 30/us_rates_trio 月窗+年窗/转折候选 9/政策簇 3/FOMC 纪要 1/JP 政策目标 registry_absent)
- 全部数字取自引擎面: 点值面(22 格)、转折候选面、us_rates_trio、asset_moves、S6 analog top5(distance 排序)、S4 序列面(经引擎自身函数 _monthly_series_for_turning/ex_post_windows/月末观测复算)
- 结构: 3 矛盾(CON-1/2/3)+2 机制链(E1/E1/E2/E3 + E1/E3)+2 情景(基准/反例)+reader_map 五面(总判断/四地走位+anchor_echo/传导 2 链 5 环含对质三值/三转折/rates_decomposition+asset_returns_echo/历史 3 段含 anchor_ym/match_window/judgment_cutoff_ym/aftermath_obs_months/us_analog/sample_note)

### 4. attach 迭代(3 次调用: 2 次拦截 + 第 3 次通过;引擎 attach_history 在档)
- 命令: `python3 ia_cli.py research-one --stage attach --report-dir <RUN> --engine-root /tmp/r22 --judgment <RUN>/agent_judgment.json`
- **第 1/2 次调用: blocked=contract_contradicted**(attach_history 20261119T154801Z / 154812Z)——矛盾 basis 文本中指标 ID 内嵌数字被文本一致性扫描器当作裸数字 token,绑定到最近面值后 CONTRADICTED,涉及 4 处:
  1. `CN_OMO_7D` 的「7」被绑定 ECB_DFR@2026-09-16=2.5(文本写 1.4)→ 矛盾
  2. `UST_10Y` 的「10」被绑定 UST_10Y=5.1 → 矛盾
  3. `TIPS_10Y` 的「10」被绑定 TIPS_10Y=2.89 → 矛盾
  4. `BEI_10Y` 的「10」被绑定 BEI_10Y@2026-11-18=2.19 → 矛盾
- 修订(只改 judgment 文本,不动引擎面/校验字段): CON-1 basis 中 `CN_OMO_7D`→「央行七天逆回购利率」、`CN_LPR_1Y`→「LPR 报价利率」;CON-2 basis 中显式序列引用改为中文描述「十年期名义、十年期实际、十年期盈亏平衡三序列(共同交易日复算;快照事实见 evidence_refs)」——序列引用保留在 evidence_refs(supports 面不展开仅披露,非阻断)。
- **第 3 次调用(20261119T154917Z): attached=True,contract_verification 全 VERIFIED**(0 contradicted / 0 unbound / 0 map_fail / 0 six_fail;六查+地图面检查全过)。

### 5. report
- 命令: `python3 ia_cli.py research-one --stage report --report-dir <RUN> --engine-root /tmp/r22`
- 产出: MAP_REPORT.md + FULL_REPORT.md + MAP_REPORT.sha256 + report.md;L3/L4 produced=True,machine_verified=True,copies_consistent=True
- **deliverable=False(语义审查门)**: review={required: true, reasons: [l3_qualitative_inference, l4_conditional_scenarios], seat_invoked: false, verdict: null}——须独立语义审查席裁决登记后方可交付(见步骤 6)。

### 6. 独立复核(零共享上下文审查席)
- 规程文件: `/tmp/r22/output/_review_protocol_round1.md`(不含判断席任何内容——只含工单问题原文+run目录路径+审查要求: 只读/引擎面独立复算每个数字日期方向/逐节核对/JSON 裁决)
- 审查席进程: VSCode 扩展 claude 二进制(2.1.327),`--permission-mode acceptEdits`,只读复算约 11 分钟
- 命令: `"$CB" -p "$(cat 审查规程文件)" --permission-mode acceptEdits > <RUN>/verdicts/PROSE-round1.md`
- **Round-1 裁决: UPHELD**(解析档 `<RUN>/verdicts/VERDICT-round1.json`)
  - 复算覆盖: 约 350 个复算点(独立于 report.json 的快照/CLI 直算约 340),远超规程 40/25 门槛
  - 分节全过: ①61 格值+18 派生同比 ②政策一年窗 8 条净变动+事件逐笔+POLCLUSTER-03 聚簇+13 个决议/生效日星期几 ③三利率两窗 +97/+104/−7 与 +1/+15/−14、恒等残差 0 ④资产月窗 8 行 ⑤传导/对质 observed_fact+近30日Δ面(BEI 行「支持主解释」符合自述裁决口径,余四行诚实缺省) ⑥三转折与候选面 9 行、先后未定纪律 ⑦历史类比 3 段×3 窗×9 行 162 项+同步性 19 个他经济体数值 ⑧总判断与走位文字 ⑨情景阈值/期限 ⑩事后回顾标注与 plan vintage 一致
  - items=3(零 MAJOR): 1 MINOR(政策一年窗「净变动」口径: ECB_DFR/ECB_MRO/JP_POLICY_RATE 变更日/月均序列以窗内首观测为基点——生效口径为 +50bp/+75bp;报告已内联披露公式与全部事件,系引擎渲染面非判断席文本)+2 NIT(JP_CPI 2.35 舍入边界写作 2.4;JP 月均两笔 ±0.1bp 亚基点变动按 bp 取整省略)
  - 诚实性证实: JP_CPI_TOKYO 12个月前格(序列 2026-01 起)与 CN_POLICY_OVERNIGHT 12/3个月前格(序列 2026-11-02 起)的「数据不可得」、JP_POLICY_TARGET 注册表缺席均经序列级证实;gate_a=FAIL 与报告内容无冲突
- 裁决登记(引擎正式接口 `record_semantic_verdict`): overall=UPHELD, reviewer=independent-zero-context-seat-round1 → `audit/semantic_review/20261120/VERDICT-20261119T153709Z-01.json`(revision=1, content_sha256 绑定)
- 登记后语义审查面: seat_invoked=true / verdict=UPHELD / fresh=true / verdicts_n=1

### 7. report(复跑,裁决后)
- 命令: `python3 ia_cli.py research-one --stage report --report-dir <RUN> --engine-root /tmp/r22`
- **deliverable=True**(mvp_complete=true;MAP_REPORT.md 语义审查节渲染「席位已裁: UPHELD(裁决链 1 档)」)
- 内容摘要稳定性: content_digest 登记前后均为 cd3e173213a53c3e(semantic_review 为挥发性键被剥,无循环绑定)

### 8. 归档
- 首跑 `--archive-dir research_archive` 被拦(blocked=archive_exists——该参数须给完整目标目录,树内 research_archive 已有 8 件既有归档,append-only 拒覆盖,不触碰)
- 改用缺省目标(=research_archive/<run目录名>): `python3 ia_cli.py research-one --stage archive --report-dir <RUN> --engine-root /tmp/r22` → exit=0
- 归档目录: `/tmp/r22/research_archive/20261119T153709Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最`
- **九件套在档**: AGENT_SEAT_ENVELOPE.json / FULL_REPORT.md / MAP_REPORT.md / MAP_REPORT.sha256 / agent_judgment.json / evidence_index.json / report.json / report.md / views_digest.json + ARCHIVE_MANIFEST.json + verdicts/20261120__VERDICT-20261119T153709Z-01.json
- **content_sha256 = cd3e173213a53c3e79cf6ec9c868cbbf08fe2db159ace7bbff8a666e1749a957**(前三处一致: ARCHIVE_MANIFEST = 裁决档 = 登记 digest 逐位相同)
- MAP_REPORT.md 归档副本与 run 目录逐位相同(sha256=c96124f2...d1a45,与 MAP_REPORT.sha256 一致);verdict_chain=[{overall: UPHELD, revision: 1, predecessor: null}]

## 交付摘要
- run 目录: `/tmp/r22/output/r22map/20261119T153709Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最`
- 最终裁决: **UPHELD**(Round-1 即过,无修订轮;1 MINOR + 2 NIT 在档未阻断)
- attach 迭代: 3 次调用(2 次 contract_contradicted 拦截 + 第 3 次通过)
- 修订条数: attach 阶段 2 处文本修订(矛盾 basis 序列 ID 改中文描述);审查阶段 0 条(UPHELD)
- 归档 content_sha256 前 16 位: `cd3e173213a53c3e`
- MAP_REPORT.md: `<RUN>/MAP_REPORT.md`(归档副本同)
