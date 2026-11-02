# P03 E2E-B 交付说明(DELIVERY)

> 包: R014 · IA-P03-E2EB-DESIGN(P0-3 设计线第1包,docs-only 零代码)
> 合同: IA-P03-E2EB-DESIGN-AC-v1.0(2026-11-02 冻结,BASE-E2EB=`1ddfb65ec78f4358b7a004be8ef5d8916ba0f052`,BASE-CI-SUITES=53)
> 分支: `dev/p03-e2eb-design`(自基线切出,线性提交,推送 origin)
> 交付时点: 2026-11-02(UTC)

---

## ① 交付清单

| 文件 | 角色 | 状态 |
|---|---|---|
| `docs/P03_E2EB_QUERY_SURFACE_INVENTORY.md` | 查询面盘点(事实层) | 新增,commit `a21da8f5df2e90800d54e5af509c5a21318a2179` |
| `docs/P03_E2EB_DESIGN.md` | 架构设计(判断层) | 新增,同上commit |
| `docs/P03_E2EB_DELIVERY.md` | 本文档(叙述层) | 新增,第2个提交(分支尖端;尖端全SHA以自述报告/证据包`git-forensics.txt`/推送后`ls-remote`取证为准,本文档自身无法先于自身提交预知) |

提交结构: 恰2个线性提交,父链=基线`1ddfb65…`→`a21da8f5…`→(本文档提交)。零修改零删除既有文件;零代码/测试/工作流/配置改动。

## ② 内容摘要

- **INVENTORY**: 五层查询入口全量行级登记——①fact_engine 17个可查询实体(E1-E17,`scripts/fact_engine.py`行号区间) ②注册表v2.0.0结构与查法+**实测81指标**(active 80+deprecated REAL_SHORT 1;core 32/important 48/context 1;E2E-B相关13条目逐条行号) ③快照构建S1-S5+读取R1-R7(不可变语义/确定性版本选择/Gate口径) ④data/daily四通道命名/字段/时区(样本实取自`*_20261102.json`) ⑤装配A1-A5/评分M1-M7/相关性C1-C6。已知缺口G-01~G-08;跨分支工具登记2条(data-inventory@`7cbef4c9…`、data-coverage@`06f715b6…`)。关键实测: **日本利率侧(JGB/日银目标)81指标零命中**;USDJPY在场(global通道260观测序列)。
- **DESIGN**: 七节齐备——目标与边界(模式B定义+E2E-B场景+in/out)/盘点引用与决策点D1-D7(候选+选定+依据)/NL→查询映射((a)IR字段级schema(query_id/as_of/target_snapshot_id/metric_bindings/derived_operations/unresolved_entities/answer_constraints等逐字段) (b)接地规则(数值必携metric_id+fact_id/快照字段/文件+观测日之一,渲染fail-closed) (c)四级缺席路径(ABSENT_REGISTRY/SOURCE/DATA/WINDOW,零填0) (d)美日USDJPY端到端走查: 美端7项在场实取·引擎值+日端2项ABSENT_REGISTRY+OP-1/2 NO_DATA+OP-3查询期0.37pp对照注册CURVE_2S10S 0.38pp,四环闭环)/E2E-A八要素逐条处置(沿用/扩展/分歧+字段机制落点)+共享档案衔接(query_id=QB-YYYYMMDD-NNN、task_id=RT-YYYYMMDD-NNN、origin_query_id/promoted_to_task_id、snapshot_id+digest内容级绑定)/差距GAP-01~08全承接/工作包WP-B1~B5(每包目标/范围/依赖/验收要点草案,工件=测试/CI/文件/SHA/数据档引用)/红线四条(快照门禁不可绕开/LIVE禁写/禁交易承诺/数据不足不填0)。
- 数值纪律: (R016更正: 原表述"两文档全文无未标注数值"经R014审计证伪——DESIGN八处计数类数值当时未标注)本整改轮后 DESIGN.md 全文数据统计类数值均已二选一标注(补注T1-T8+全文扫描新发现项,扫描方法与清单见R016证据包⑥);INVENTORY 标注状态沿 R014 审计认定(认定范围=与指认处对应的登记带标注,非全文认定);[实取](文件+日期)/[实取·引擎](fact_engine离线确定性运行于授权副本,as_of=2026-11-02T12:00:00+08:00)/[示意]三态中前二为实,DESIGN仅schema示例ID字符串为标识符(已显式声明非数据值)。

## ③ 证据指针

- **本地逐套件运行(CI同构,AC-06(a)主证据)**: 全新clone(无`data/`等ignored目录=CI checkout同构)按offline-tests工作流同构逐套件运行: **53/53全部exit=0,OVERALL_FAIL_FLAG=0(情形a)**;逐套件退出码与日志: 证据包`local-suites-cisim-tip/suite-summary.txt`与`local-suites-cisim-tip/logs/*.log`。
- **工作区首轮运行(环境差异记录)**: 本机工作区含授权数据副本`data/daily/`(gitignored,先前轮次同步)时,`test_p4_fixes` exit=1(该套件检测到`data/daily/global_2026*.json`即走真实数据路径,202609月度序列在仅有20261101/1102两日数据下为0,4项check失败)——**CI同构clone中同套件exit=0**,判定为本地数据在场导致的环境差异,非代码回归;记录于`local-suites-workspace/suite-summary.txt`+`local-suites-workspace/test_p4_fixes.log`,如实留档。
- **git取证**: 证据包`git-forensics.txt`(尖端/父提交全SHA+`git log --oneline -5`)、`git-diff-name-status.txt`(`git diff --name-status 1ddfb65ec78f4358b7a004be8ef5d8916ba0f052..HEAD`全文)、`ls-remote-after-push.txt`(推送后全量)。
- **证据包**: `/tmp/p03-e2eb-design-evidence/IA-P03-E2EB-DESIGN-EVIDENCE.zip`(成员①-⑦: 三白名单副本/git取证/diff全文/本地逐套件日志(CI同构+工作区差异附录)/ls-remote全量/SHA256SUMS/DELIVERY副本;SHA256SUMS覆盖除zip自身外全部成员)。zip自身sha256见自述报告。

## ④ 偏离与如实声明

1. **本地解释器版本**: 本机python3=3.9.6(CI为3.11;本机另有python3.11但执行需额外授权,未动用)。CI同构运行以3.9.6完成,53/53全绿;版本差异如实登记,最终以操作者CI dispatch(3.11)为准。
2. **工作区数据副本影响**: 如③所述,`test_p4_fixes`在工作区环境exit=1(授权数据副本在场→套件走真实数据路径)。未删除/移动任何本地数据文件;以clone方式取得CI同构结果。此为AC-06(a)的环境注记,不构成零回归证据的削弱(clone侧全绿),但如实呈报。
3. **DEV侧无持久化快照**: 本checkout `data/daily`无`research_snapshot_*.json`(INVENTORY层③实测)。DESIGN走查数值= fact_engine离线确定性运行于采集文件副本(等价于快照构建的规范化+派生路径,`compute_derived`按snapshot_builder流水线顺序执行);非完整快照产物,差异(无Gate A落盘/sources_status节)已在INVENTORY G-05与DESIGN GAP-05登记。
4. **DESIGN §三(d)中`UST_10Y−UST_2Y=0.37pp`**: 为确定性算术(两[实取·引擎]输入相减),标注口径已在文中显式;与注册指标CURVE_2S10S(0.38pp@2026-10-30)观测日不同,文中已并注不混同。
5. **CI dispatch(AC-06(b))**: 属操作者CHECKPOINT登记件,非执行方职责;本包推送后由操作者侧dispatch,登记于`rounds/014/E2EB-DESIGN-CI-dispatch-evidence.md`。
6. 本包零网络(除git/GitHub推送);registry/data/daily只读;LIVE与launchd零触碰。

## ⑤ 后续建议(不冻结AC;正式AC由主Agent后续轮拟定)

1. 排程建议: WP-B1+B2先行(映射与执行器,无外部依赖,纯DEV可测);WP-B3(JGB/日银数据)独立并行,循免费公开源预授权③规则;WP-B4依赖B1;WP-B5收口。
2. WP-B3注册表变更(81→81+N)建议单独走registry变更纪律(对齐P0-2-W1审计实践),不与其他包混提交。
3. E2E-A冻结合同(IA-P03-W1-E2EA-AC-v1.0)落定后,DESIGN §四对齐表如与其冻结文本冲突,按AC-03注以登记型修订承接(建议在首个实现包内登记)。
4. GAP-05(DEV侧快照测试范式)建议在WP-B2实现时直接固化write=False快照夹具,兼作GAP-08接地渲染测试的数据底座。
5. 本设计§六验收要点均为草案;DEFERRED类设计性意见(如IR schema字段增删)由审计轮记录,不阻断本包。

---

*证据与自述: `/tmp/p03-e2eb-design-evidence/` + 本轮stdout自述报告(四段)。*
