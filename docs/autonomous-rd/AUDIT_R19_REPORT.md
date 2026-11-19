# Audit-R19(R63) — 地图问句: 同比基期/发布纪律/三维转折/历史类比结构面+读者版量化显示

- 基线: 2178b2d3dbcb8bd15cde2537d3ef35f369f810f9(R18 收口+CI 回填后)
- 修复提交: **e6f77e11c2fc4858d1ba5c8f6dab063cba9a084f**(六文件+1003 行)
- 分支: dev/audit-fix-r1(PR #1);合并与上线由用户裁定,本波不并 main 不部署
- 状态: 停等外部审计

## 〇、指令与唯一验收场景

用户指令(节选): 在现有 PR #1、分支 dev/audit-fix-r1 完成第十九轮收尾;审计基线 2178b2d;
一次完成复现、修复、真实运行、独立复核和推送。

验收场景=全新 Claude Code 会话只输入原问(逐字)即可拿到可打开、可核查的中文报告:
「给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，
分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？
证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，
当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？」

## 一、基线复现(六缺陷全数在档,基线树实测)

1. **同比基期错配**: 地图问句的月度同比锚可配到非去年同月;缺基期格未标不可得也未另列最近有效同比
   ——10 月总体/核心 CPI 的 13 个月变化被写成同比路径。
2. **提前引用未发布数据**: 锚值无发布日纪律——2025-08-18 锚可引用 2025-10-29 才公布的三季度 GDP。
3. **转折候选单维**: 候选池缺增长维,增长/通胀/政策未全部进入候选。
4. **历史类比无结构面**: 匹配区间/判断截止月/事后窗口三概念混写;锚+N 月无唯一算术源
   (2022-06 锚 12 月可写错终点);事后结果可落回匹配期内。
5. **契约无四阻断器**: 错用同比基期/提前引用未发布/同一转折重复三次/历史结果落匹配期,均不拦正式归档。
6. **读者版量化缺席**: 后台已有的 S6 历史比较与量化说明不进普通读者版(VIX 样本验证)。

## 二、修复(D1-D8,@e6f77e1 六文件)

| # | 修复 | 落点 |
|---|---|---|
| D1 | 月度同比只配去年同月;缺基期=None+no_same_period_base+最近有效同比另列 | snapshot/orchestrator |
| D2 | RELEASE_RULES 发布日推定+锚值只取发布日≤锚日观测;关键数字表带发布日期列 | research_orchestrator.py |
| D3 | 转折候选池扩增长维;每指标至多一候选 | research_map_planner.py |
| D4 | 历史类比结构化 anchor_ym/match_window/judgment_cutoff_ym/aftermath_obs_months;ex_post_windows 锚月+N 月唯一算术源 | research_map_planner.py |
| D5 | 判定契约四阻断器(CONTRADICTED)+三转折维度覆盖+传导图须达资产 | judgment_contract.py |
| D6 | CN PPI 归价格维;JP 隔夜市场利率与央行目标分别列示(目标=声明式缺口带检索范围+影响) | registry/planner |
| D7 | 传导图连到资产指标(ASSET_UNIVERSE 30 项+asset_reach 契约检) | research_map_planner.py |
| D8 | 读者版渲染 S6 历史比较+S5 日度相关(_render_quant_sections;VIX 样本形状验证) | research_orchestrator.py |

文件: ia_cli.py / scripts/research_contract/judgment_contract.py / scripts/research_map_planner.py /
scripts/research_orchestrator.py / tests/test_audit_r18_gate.py(夹具升级,历史段结构面)/
tests/test_audit_r19_gate.py(新)。

## 三、门测试(tests/test_audit_r19_gate.py,35/35 全绿)

§A 缺基期/13 月窗反例;§B 发布纪律(UNEMPLOYMENT 2025-11 值发布 2025-12-05>锚 2025-11-17 被排除);
§C 增长维入池+维度覆盖;§D 锚+N 月唯一算术源;§E 四阻断器正反例(dup_turning/same_dim/no_asset/
hist_no_anchor/hist_short_reach/hist_leak/hist_cutoff_early);§F 契约 CONTRADICTED 落位;
§G 读者版量化段(VIX 样本: S6 top-5+aftermath、S5 日度相关,真档底+注形状渲染);
§H 交付门(席位裁决前置+归档计数+SHA 锚)。
保留回归: 空机制链通过+美债期限缺失(既有口径)全绿。

## 四、回归与复放

- 电池 191/192→提交后 phase6 重跑 29 PASS/0 FAIL=有效 192/192(唯一红=phase6-D3 工作面洁净检查,
  属提交前预期红;rc 口径=逐件 rc∈{0,5} 绿)
- 四复放包 BLIND/F10/cn-task-b/e2e-corrected 全 PASS(口径同 R18)

## 五、真实运行(任务②③④⑥,代码 e6f77e1,零合成数据)

引擎树=仓码@SHA+LIVE 通道副本(20261015..20261118 窗)+CN_PMI_MFG/CN_NEW_LOANS 226 月冻结包注入
(provenance=frozen_pack)。快照 80 序列;Gate A DEGRADED(4 非核心缺席:BUND_10Y/BUND_2Y/
CN_OMO_7D/JP_CPI_TOKYO_YOY);事实 104 核心缺 0。

全链: plan(8 转折候选跨三维/asset_universe 30)→研究席判决(schema 1.1,L3 矛盾+机制链×3 环每环
竞争解释+区分指标,L4 两情景带证伪阈值,reader_map 四问五面)→attach 四轮迭代全被契约拦截后
VERIFIED(v1 SCN 敏感变量>2;v2 ex_post_reach 月算错;v3-v4 文本一致性等式括注纪律)→
**独立语义审查席三轮: REVISE(5 必修: 2 MAJOR+3 MINOR)→修订→REVISE(残留 1)→修订→UPHELD**
→report(deliverable=True)→archive(content_sha256=8ea0485d…=UPHELD 档绑定值)。

审查席必修台账(全部数值经其 series_store 直读零信任复算):
1. [MAJOR] CORE_CPI 转折同窗值误用候选窗值(2.8229→2.4462「回落」)→同窗严格同基期 2.4725→2.8229
   (+0.3504pp,核心仅部分跟随)——研究席把引擎候选窗(2026-05→08)的值写进了转折窗(2026-02→05)叙述
2. [MAJOR] CORE_PCE 证伪基线月标错(2.9592=2026-02 值标作 2026-09)→3.1212
3-6. [MINOR] 2025-03 锚 6m 失业率 4.1→4.4;12m JP_POLICY_RATE 0.727→0.728;data_note 12 月窗
   止点 2025-12→2026-03;传导链步骤标签「核心未跟随」→「仅部分跟随」

**席位存在理由第三证**: 必修 1/2 类缺陷(候选窗值串写/月标错)不在机器契约面内(数值各自真实,
错在窗口归属),只有零信任复算席能拦——契约门四轮全绿后仍被审查席抓出 2 MAJOR。

## 六、真实运行产物坐标

- 运行目录: /tmp/r19_real/runs/20261119T024247Z_给我一份全球宏观经济变化地图_*/
- 归档: /tmp/r19_real/engine/research_archive/20261119T024247Z_给我一份全球宏观经济变化地图/
  (ARCHIVE_MANIFEST+九件套+verdicts 三档)
- 证据包: docs/autonomous-rd/r19-evidence/(MAP_REPORT.md+sha256/agent_judgment.json/
  report.archive.json/verdicts//README)
- SHA-256 三方回读: agent_judgment 运行=归档(315e9727…);MAP_REPORT 运行=归档=.sha256(f018d6ef…);
  report.json 运行=归档(2c945e36…)
- 读者报告四问落位: ①四地三时点对照表(L12-46)②三转折表+谁先变/跟进背离(L77-98)
  ③传导机制四件套含区分指标(L61-75)④历史类比+同步性+事后 3/6/12 月(L138-158)

## 七、新会话验收(任务⑥,PASS)

零上下文子会话(general-purpose 席,不继承主会话任何上下文)只输入原问(逐字)+机器环境
同等信息(引擎根在位),不告知任何答案位置。结果:

- **发现路径**: 未新跑管线——以原问对 research_archive 各 ARCHIVE_MANIFEST.json 的 question
  字段逐字匹配(含全角标点)命中 20261119T024247Z 归档,定位主交付 MAP_REPORT.md+配套
  FULL_REPORT.md/verdicts 三档。
- **可核查性核验**: MAP_REPORT sha256=f018d6ef… 与 .sha256 及 manifest 一致;归档内 7 副本
  sha16 与 manifest 逐件一致;终裁档 revision=3/UPHELD 的 content_sha256 与 manifest 相同
  (8ea0485d…)。
- **抽查复算**: series_store 直读 30+ 数值零偏差——CPI/CORE_CPI/CORE_PCE 同基期同比逐位;
  三时点锚值(PMI/JP/ECB/DFF 含台阶日);利率分解(+1.00=+1.07−0.06pp 自洽);历史事后窗
  8 个资产涨跌幅按报告口径逐位复现(初用错起点得 −5.28%,按头部明示口径改窗起日首观测后
  精确一致=口径差非数值错)。
- **四问落位**: 对照表+走位/转折表/传导四件套/历史类比两段,全部在正文。
- **缺陷面如实**: 缺数格(CN 通胀政策/EA HICP/JP 东京 CPI 等)在件内披露检索范围与影响;
  渲染器标签回显重复(观感,R20 候选,与本波审查席观察一致);零付费零联网。

## 八、坑(操作者)

- zsh 速算脚本把同比基期写成上月份(自查推翻重算)——复算脚本先自证基期口径
- attach 重挂同文件名幂等: attached_at 不刷新/attach_history 无新条目(内容绑定经审查席实核;
  机制面 R20 候选)
- 渲染器标签回显重复五处(「因果假设: 因果假设:」类;判决文本自带标签+渲染器再加)——观感问题
  零数值影响,R20 候选

## 九、状态

- 提交链: 2178b2d → e6f77e1(D1-D8+门) → 本报告与状态收口提交
- CI: 推送后以全 40 位 head_sha 查验三 job 绿(结果见 PR/CI 链接)
- PR #1 更新至 R1-R19;**停等外部审计: 不并 main 不合并 PR 不部署不开新轮**
