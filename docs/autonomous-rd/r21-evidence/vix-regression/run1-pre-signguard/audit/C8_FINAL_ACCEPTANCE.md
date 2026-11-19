# Charter 8 终验报告(E席独立审计)

- **席位**: E席终验(独立审计总席,与 A/B/C/D 席无隶属;同席承 Charter 7 D席纪律:只验不修,缺陷分级,数据不足=NOT_VERIFIED 如实标)
- **日期**: 2026-11-10(晚)
- **冻结输入**: D席工程 `dev/charter8-research-map-v1@d5c4c75`(22文件 +2367/−172);A席研究 `/tmp/auditA/c8/{final_report_c8.md, map_phase1.md, views_verification.md}` + QB-20261110-032/033;B席库 `data/institutions/views/` 11文件;C席复验 `audit/C8_RESEARCH_REVERIFY.md`(7/7 PASS)
- **隔离环境**: `/tmp/ia-c8` = git clone `dev/charter8-research-map-v1`(d5c4c75)+ dev 库 `data/` 全量拷贝 + 独立 .venv(requirements + pytest 8.4.2 + requirements-workbench/streamlit 1.50)。**零Key零API 全程**(每命令显式 `env -u MODEL_* 厂商A_* FRED_* TUSHARE_* FINNHUB_*`);**LIVE 生产零触碰**;dev 仓未动(仅本报告落档)

## 总判定: 七面全 PASS,BLOCKER = 0

| 面 | 判定 | 一句话依据 |
|---|---|---|
| 1 三真实验收(A/B/C) | **PASS** | A结构10节/8M/4S全在场;B 11文件10机构,自选2 URL(V-003 PIMCO/V-009 MSIM)逐字核验真实;C抽3行(R6/R7/R24)独立复算判定与证据相符 |
| 2 四层区分(核心) | **PASS** | 见独立节;④层 Agent Native 五步真走通,全程零模型API |
| 3 红线十项(§13) | **PASS** | 十项逐一扫描,零违例(明细见下节) |
| 4 D席代码 diff 级评审 | **PASS** | 22文件全阅;6新套件167断言独立复跑 0 失败;113基线无弱化;view_store/view_verifier 零网络零AI(import级扫描 NONE) |
| 5 勘误链审查 | **PASS** | CAPE 勘误独立复算**完全证实**;两勘误 append-only、QB 主体冻结、判定不翻转声明成立;GOLD_F 追溯链有缺口(观察④) |
| 6 产品面新用户验收 | **PASS** | 零Key AppTest 四页+关于 全渲染零异常;views list/get 真实11文件;无模型指引文案在场 |
| 7 证据索引核验(§14) | **PASS** | 抽7条:命令可重放(4组数值全中)/URL存活(2)/QB引用正确(2,冻结值核验) |

---

## 四层区分判断表(独立成节·Face 2 核心产出)

| 交付物 | ①代码实现 | ②合成测试通过 | ③真实数据测试通过 | ④真实Agent端到端 |
|---|---|---|---|---|
| view_store + views schema v1.1 | ✅ 315行,linter纯函数 | ✅ 27断言/0败 | ✅ 真实11文件装载+lint(12合规/0隔离) | ✅ 五步走①②:合规样例入册;负样例3项违规精确拦截(attribution缺失/quote 2904>500/publish>fetch),rc=1隔离不装载 |
| view_verifier(确定性验证器) | ✅ 207行 | ✅ 40断言/0败 | ✅ 真实 VIEW-003(PIMCO):82证据行/5缺席(如实)/2支持/0反对,snapshot v5 | ✅ 五步走③:rc=0,零AI零网络 |
| transmission_edges + 传导地图 | ✅ 25边强制 qb_source(缺即 raise) | ✅ 33断言/0败 | ✅ VIX→SPX r=−0.7138/n=2512 经引擎相关复算**逐位一致**(−0.7137845828…);QB-022 在档 | ✅ 五步走④:边引用经 archive 复核 |
| archive --snapshot-id 显式绑定 | ✅ 前缀归一+load_snapshot_by_id(委托唯一私有读取面) | ✅ 13断言/0败 | ✅ 真实归档:save --snapshot-id v4 → QB-20261110-040,record.snapshot_id=research_snapshot_20261110_v4 绑定成立;get 往返全文/统计/证伪条件完整 | ✅ 五步走⑤ |
| workbench_data C8 段 + app.py 四页 | ✅ 窗口区间唯一实现(horizon_start/metric_window_changes) | ✅ 35断言/0败 | ✅ AppTest 零Key渲染5导航面零异常;页③11份/schema v1.1;页②14强+11近零边 | ➖(Skill 工作流以 CLI 为链路,见下行;数据层④经CLI同函数覆盖) |
| china_market_collector HK 深窗 | ✅ 10y深窗+同口径统一计算,兜底不降级 | ✅ w3套件绿且锁面**强化**(单请求纪律+独立手算期望) | ✅ 隔离环境快照 HSI/HSCEI 序列 n=2460(**本席一手复核**,非仅听D报) | ➖(采集器非Agent交互面) |
| SKILL.md 研究地图工作流 + ia_cli views | ✅ 五步工作流入Skill;views list/get/lint 三动作 | ✅ 19断言/0败 | ✅ views list=11/0隔离;get VIEW-003 全档;不存在件 rc=1 | ✅ **五步全链真走**(本席以装Skill后的工作流逐步执行,样例采集→lint→verifier真view→边引用→archive落档,全程零模型API) |
| A席三份研究档 | — | — | ✅ 抽样数值全部复算命中(见 Face 1C/7) | — |
| B席机构观点库 | — | — | ✅ 11文件/10机构≥5≥8阈值;V-003/V-009 原文逐字比对一致 | — |

**④层结论**: Agent Native 端到端**真实走通**,无一步依赖模型 API 或网络。跑得通,非 NOT_VERIFIED。

---

## Face 1: 三真实验收明细

### A席地图(结构核验)
- 终报告10节齐(一执行摘要…十缺口清单)+证据索引A-D;M1-M8 每条含五问语义成分(事实/重要性或其并入/竞争解释/支持反对数据/证伪);S1-S4 八要素 ①成立×4 ⑧证伪×4 在场;R1-R30 30行齐。**PASS**
- 抽验内容锚点: Fed 3.63→3.75→3.88 月度路径、S1四项全未触发、已到期可判仅2项(MSIM 9月加息>50%→兑现;10Y 4.75%→吻合)与 views_verification 一致无内部矛盾。

### B席机构观点(阈值+URL真实性)
- 11文件/10机构(IMF/Fed/PIMCO/GS/ECB/BOJ/WB/BlackRock/MSIM×2/IEA),阈值 10≥5、10≥8 达标;access 6 public_full + 4 public_summary + 1 headline_only(honest)。
- **本席自选 URL 验证(避开 C席已验 V-002/005/006)**:
  - **V-003 PIMCO** `pimco.com/us/en/insights/growth-holds-risks-widen`:页面存活,发布2026-10-06、作者 Tiffany Wilding/Andrew Balls 与档一致;逐字核对≥5段原文全中("Our baseline is that the Federal Reserve and other major central banks ultimately won't need to fully deliver…"、"The main exception is China, where a prolonged and ongoing housing downturn…"、r*≈1.5 从0.5上移、Kevin Warsh 表述、实际收益率主导名义上行段)。**真实**。
  - **V-009 MSIM** `morganstanley.com/im/de-de/.../a-firmer-fed.html`:页面存活,2026-09-18 发布、Broad Markets Fixed Income Team;原文逐字核中:"The 10-year Treasury yield rose 1.5 basis points (bps) to 4.75%, while the 2-year yield increased 5bps"、"leave rates unchanged at 3.50%-3.75%, despite three votes for a 25bps hike"、"September hike expectations moved back above one-half"、日元最弱1.5%、Warsh Jackson Hole/PCE 3.7%、IG 78bps/HY 261bps/战术立场(UW IG/small OW HY/OW EMD/OW securitized/long duration)全部与档一致。**真实**。

### C席证据核验 R1-R30(分布合理性+抽3行独立复核)
- 分布 支持8/部分5/冲突2/不足15:不足占比高与"10机构×多论点 vs 本地证据面"的窄口径一致,抽行未见以"看起来对"替代复算的迹象,分布合理。
- **R6(PIMCO 实际收益率主导,E1)**: 本席引擎复算 UST_10Y 1y **+0.73pp**、BEI_10Y **−0.05pp**、TIPS_10Y **+0.77pp**(compare 自配对,基准2025-11-07)——与A席三值逐位一致;+0.73−(−0.05)=+0.78≈TIPS+0.77 分解自洽;原文段落在场。**判定与证据相符**。
- **R7(PIMCO 利差偏紧,冲突+长历史NOT_VERIFIED)**: 复算 发布日10-06 HY_OAS=**3.03**、11-06=**3.42**、3年窗 n=**784**、中位数 **3.02** 全中;分位 p(3.03)≈50.5、p(3.42)≈87.3(midrank口径;A席 p50.3/p87.0 为另一分位约定,差0.2-0.3pp,判定"窗内中位+其后走宽"不受影响)。**判定与证据相符**。
- **R24(MSIM 8月曲线趋平,E2)**: 复算月末口径 UST_2Y 4.28→4.34(+0.06pp)、UST_10Y 4.75→4.75(0.00)、2s10s 0.47→0.41——与A席三值逐位一致;原文"10Y +1.5bps至4.75、2Y +5bps、曲线平"方向与量级吻合(5bps盘内 vs 6bps月末为口径差,A席已注明月末口径)。**判定与证据相符**。

## Face 4: D席代码 diff 级评审

- **22文件全阅**(diff cd5524c..d5c4c75): view_store 315行(linter 21必填+枚举硬拦截+quote≤500任意basis+隔离不降级);view_verifier 207行(区间变动薄委托 workbench_data 唯一实现;relation 仅显式 directions 机械计算);workbench_data C8段(窗口区间唯一实现/覆盖矩阵/传导边 qb_source 强制/隔离件绝入面);app.py 312行重组;china HK深窗;research_archive +9行(委托既有私有面零新实现);SKILL/cli-contract/README/USER_GUIDE 文档面;6新测试套件+2改动套件。
- **6新套件 167断言独立复跑**(脚本约定,隔离venv): edges 33/0、view_store 27/0、view_verifier 40/0、views_cli 19/0、workbench 35/0、archive_snapshot_binding 13/0 —— 与 D 报 167 断言口径一致,全绿。指定抽验 view_store 27/verifier 40 均实锁(非弱断言:含负样例拒绝面、装载纪律、映射完整性 106指标全注册)。
- **113基线有无弱化**: 全量套件脚本约定复跑 **117/118 绿**(唯一例外见观察③,系 C8 diff 零触碰的预存件);test_data_w3_fixes 改动为**锁面强化**(单请求纪律 calls==['10y']+独立手算 ytd/week 期望+异常路径保留),test_p03_e2eb_b4 仅白名单扩面 load_snapshot_by_id。**无弱化**。
- **view_verifier 零AI零网络声明**: import 级扫描(含 ast 遍历)网络模块 NONE;relation 未传 directions=None+note;证据表纯快照事实+interval_change。**声明成立**。
- app.py 重组审查: 四页按章程重设计;数值口径 caption 随行(interval_change 自配对同函数);页②"方向可引=统计事实非因果"、近零渠道如实呈现;页③ attribution 徽章+quote≤500 纪律展示;页④零模型+Agent Native 引导。移除的旧 UI 面见观察⑥(章程驱动,库函数保留)。

## Face 5: 勘误链审查

- **CAPE 勘误独立复算(本席自建复算,未用A席脚本)**: 以引擎自身 `analog_engine.z_at`(expanding z,泄漏规则1)在隔离快照 SPX_CAPE(n=1750, 1881-01..2026-10)复算,并**完整复现六维候选池准入**(19/19特征序列、U=17特征×6维、重叠排除 m0−12、MIN_VALID_DIMS=4):
  - 池=**73候选**(与 A席/引擎报 valid=73 精确一致);锚点 2026-10 z=**2.9991**;池内 CAPE z 峰值=**3.0216@2021-11**;高于锚点的候选**恰1个**→"锚点高于72/73、唯一例外2021-11"**完全证实**;2022-01 z=2.7734 证实系簇代表口径来源。
  - 注: 单维全网格有58个月 z 高于锚点(1899/1929/1997-2001),均因六维准入(其他维度历史不足)被排除出池——非口径错误。
  - **判定不翻转成立**: 锚点≈池内次高,z≈+3.0 历史极高区结论两端一致。
- **append-only 纪律**: engine-notes 两段勘误均为追加不改写;QB-20261110-032 答文仍含 **126.90**、QB-033 仍含 **2.77**(冻结如旧)——勘误走注记不改历史主体,纪律成立。
- **GOLD_F 勘误追溯缺口**: 无 engine-notes 条目,仅见于 C席报告与修正后 /tmp 文件(观察④)。

## Face 6: 产品面新用户验收

- 零Key streamlit AppTest: 安装 requirements-workbench(streamlit 1.50)后,四页+关于 共5导航面全部渲染,**零异常**(7.7s)。页③渲染 11份/schema v1.1/隔离不入面文案;页② 14强+11近零=25边+机制层结论;页④ Agent Native/零模型/view_verifier 指引文案在场。
- ia_cli views list: 11合规/0隔离/11文件;views get --view-id VIEW-20261110-003: PIMCO 全档(11核心观点/9逐字/5预测);不存在件 rc=1 如实。
- 无模型环境指引: USER_GUIDE「页面零模型调用」、README Agent Native/data-only 周报默认形态文案在场。

## Face 7: 证据索引核验(抽7条)

| 条目 | 类型 | 复放结果 |
|---|---|---|
| compare 自配对 UST_10Y/BEI_10Y/TIPS_10Y 1y | 命令重放 | +0.73/−0.05/+0.77pp 逐位命中 |
| history HY_OAS 3年窗 | 命令重放 | 3.03/3.42/n=784/med 3.02 命中(分位差系约定,见R7) |
| history UST_2Y/10Y/2s10s 2026-08 月末 | 命令重放 | 4.34/4.75/0.41 命中 |
| analog --anchor 2026-10 --top 5 | 命令重放 | scanned=1871/valid=73/clusters=5 命中 |
| V-003 PIMCO URL | URL存活 | 存活,逐字一致 |
| V-009 MSIM URL | URL存活 | 存活,逐字一致 |
| archive get QB-032/033 | QB引用 | 在档;冻结值 126.90/2.77 如旧(append-only 佐证) |

## 红线十项终检(章程§13)

| # | 红线 | 判定 | 依据 |
|---|---|---|---|
| 1 | 编造数据 | 通过 | 引擎数值全复放命中;引文逐字比对原件一致;零编造迹象 |
| 2 | 机构观点当事实 | 通过 | attribution 硬必填(institution_stated/ai_inferred),linter 拦截缺失;报告与页面均带徽章 |
| 3 | 相关→因果 | 通过 | 传导边"方向可引=统计事实非因果";近零渠道如实标"流行叙事 E1 不支持";多处"相关≠因果"披露 |
| 4 | 事后修订冒充当时 | 通过 | 勘误 append-only;QB 主体冻结(126.90/2.77 复核);revisions[] 三键只追加 |
| 5 | 记忆代替检索 | 通过 | 全部数值快照接地;verifier 每次现读快照;未见记忆型断言 |
| 6 | 付费墙内容当公开 | 通过 | access_level 诚实三档(6/4/1),headline_only 如实标注 |
| 7 | 数量当正确性 | 通过 | E1/E2/E3 分级;财政/贸易两维四经济体 NOT_VERIFIED 如实;不以数量掩质 |
| 8 | 未授权付费API | 通过 | C8 面(app四页/verifier/view_store/CLI)零网络零模型(import级扫描 NONE) |
| 9 | 生产环境触碰 | 通过 | 全程 /tmp 隔离 clone;LIVE 零触碰;dev 仅落本报告 |
| 10 | 降质量过关 | 通过 | HK 兜底=10y深窗非短窗凑数;views 隔离不降级装载;verifier 缺席如实 |

## BLOCKER 清点与分级清单

**BLOCKER: 0。DEFERDED: 2。观察: 6。**

- **DEFERDED-1(合并前必办)**: engine-notes 两段勘误(335天四值注记 + CAPE R12 峰值口径)目前是 dev 工作树**未提交**修改——append-only 内容本身合规,但不随 d5c4c75 提交则勘误链在版本史上不可溯源。建议随 C8 合并一并 commit。
- **DEFERDED-2**: view_verifier 硬编码 `wd.latest_snapshot`(无 --snapshot-id 旁路)。当前无害:本席实测 v4/v5 facts **逐位相同**(0差异),A席 v4 基准与 verifier v5 输出数值等价。但未来出现 v6 且 facts 有变时,verifier 会静默换基。建议补 --snapshot-id(与 archive 同参式)。
- **观察①**: pytest 不在 requirements.txt(本席隔离装入 8.4.2);且测试件为自跑式(module 级 check 循环+sys.exit),pytest 收集会 INTERNALERROR——套件约定=逐文件脚本执行。文档宜写明跑法,防新用户 pytest 踩坑。
- **观察②**: D 报"119/119绿"与可执行口径 118(排除 test_model_live.py)差1;本席独立复跑 **117/118 绿**,唯一例外= test_oss_product W7"无Python→rc=127"行为检查在隔离环境未复现绿(standalone 60s 超时/套件内 rc=1)。该文件与 run_daily.sh 在 C8 diff **零触碰**(git 证实),属预存环境敏感检查,非 C8 回归。建议 D 席补一次环境标注的绿证或该检查加环境豁免。
- **观察③**(并入②): run_daily.sh 清空 PATH 场景依赖 `date` 可用前的日志重定向,行为在不同 bash/环境下不稳定,与 C8 无关但值得 D 知悉。
- **观察④**: GOLD_F +126.90→+126.94 勘误无 engine-notes 条目,追溯仅靠 C席报告+修正后文件;建议补一条注记与另两勘误同链。
- **观察⑤**: B席库覆盖缺口: VIEW-003 subjects 映射 5 指标缺席(BUND_10Y/BUND_2Y/CN_OMO_7D/CN_SF_FLOW/JP_CPI_TOKYO_YOY,原因"来源文件在场而指标缺席(采集遗漏)")——verifier 如实报缺席(正确行为),采集覆盖可作后续工作。
- **观察⑥**: app.py 重组移除旧"AI研究"交互面(本地作答/AI解释/存档按钮)、sources_status 展开器、跨指标对比叠加图——系 Charter8 页④章程设计(零模型+Agent Native 引导),库函数仍在 workbench_data 保留,基线测试无弱化;记录以免后续误认为意外丢失。

## 结语

七面全 PASS、红线零违例、BLOCKER 零。四层中 ④ 层(Agent Native 端到端)由本席按 Skill 五步工作流**真实走通**,是本次终验区别于 C席复验的关键增量。两项 DEFERDED 均为合并前小动作,不阻塞判定。Charter 8 工程面、研究面、产品面**具备合并条件**(勘误提交与 verifier 快照参数建议随合并处理)。

—— E席(独立审计总席),2026-11-10
