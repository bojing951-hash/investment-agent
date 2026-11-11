# ITERATION_LOG — 研发轮记录(只追加)

> 记录粒度: 一个章程/一个重要阶段一条。历史大节点自 git tag 与发布记录回填(2026-11-11)。
> 2026-11-08 之前的 38 包轮次明细在 `~/agent-loop/rounds` 与 `contracts/`(仓库外,不迁入)。

| 日期 | 轮/章程 | 交付 | tag@SHA | 验收 |
|---|---|---|---|---|
| 11-04 | W5 终局 | china 采集通道改造+重跑 | w5-final-20261104@5ab7c16 | Agent4 终裁 |
| 11-05 | P3 终局 | 38/38 全收口+四层封版 | p3-final-20261108@bafb0f3 | 四层全封 |
| 11-07 | P1/P2 终局 | 实现链封版 | p1-final-20261107@0c9fc3f / p2-final-20261107@9fb23ec | 用户亲批 |
| 11-08 | OSS 产品化 | 公开仓+主 CI 基线 90 | v0.1.0-alpha@ac5d2a2 | 已公开 |
| 11-08 | Agent Skill 化 | 技能+ia_cli 八能力+安装器 | v0.2.0-alpha@cb38e21 | CI 绿=基线 93 |
| 11-09 | v1.1 整改 | P0×4+安装器+档案旁挂 | v0.3.0-alpha@79f2551 | 九项验收 9 PASS |
| 11-09 | Model-Agnostic v2.0 | Agent Native 零额外 Key/凭证消毒/归档六参 | v0.4.0-alpha@2af3f9f | 四路验收 9 PASS+CODEX NOT_VERIFIED |
| 11-09 | v2.1 整改+glm 清零 | 旗标删除/模块改名/门禁三态/--lag | v0.5.0-alpha@0f92151 | 13 判定全 PASS |
| 11-10 | Charter 6 全球宏观深度 | analog 六维引擎/十年数据/Shiller 145 年 | v0.6.0-alpha@cca2e4a | 四路审计+D 席四案例全 PASS |
| 11-10 | Charter 7 能力建设 | P0 七问题修复+SOFR/WALCL+缺口台账 18 项 | v0.7.0-alpha@97d758e | D 席终验六项全 PASS |
| 11-10 | 数据批 1 | SPX_EPS 145 年+DAX/CAC/CN 六指数+M2SL | v0.7.1-alpha@cd5524c | 复验五面全 PASS;LIVE 部署此面 |
| 11-11 | Charter 8 机构观点 | 观点库 11 份/10 机构+view_verifier+四页工作台 | v0.8.0-alpha@06bb65d | 五席协作+E 席七面零 BLOCKER |
| 11-11 | Charter 9 研究闭环 | 三型验证/六标签/四状态/research-map/一键研究 | v0.9.0-alpha@cdffebe | A-E 全 PASS+反例 10/10;CI 基线 126 |
| 11-11 | 长期研发章程初始化 | CLAUDE.md+autonomous-rd 七文件 | dev/autonomous-rd-charter | 总指令+启动指令原文落位 |
| 11-11 | R1 三型证据落库 | VP v1.1 阶段A/B+stage_labels(C 契约零变动)+research-map 命令可执行化+页③三阶段披露 | dev/rd-r1-stage-evidence@26d4ef7 | 自测 39 判定过;全套回归 129/129 绿(11-11 干净重跑) |
| 11-11 | R1 独立审计 | 对抗式 6 维(无前视/标签纪律/方向归因/契约真实性/可复算性/B面抽验) | (后台 Agent 对 26d4ef7 diff) | 六维全 PASS,交付物清洁;无 BLOCKER,2 MAJOR+6 MINOR+3 NIT |
| 11-11 | R1.1 审计整改 | MAJOR-1 入口日期归一 _norm_ymd;MAJOR-2 linked_forecasts 定 1-based 单基+记基制;MINOR-3 词表否定护栏+英文词边界;NIT-9/10/11(判定数/死代码/n 硬编码/定基夹具) | dev/rd-r1-stage-evidence(本提交) | 套件 50 判定全绿;受影响 8 文件全 exit 0;对照实验=17 份 VP 语义零差异 |
| 11-11 | R2 一键研究真执行 | research_orchestrator 十一步确定性管线(S1 分解→S11 归档,零模型,每步真 ia_cli 子进程+信封留档,ok/semantic_ok 分记,L3/L4 恒 declared-not-produced,逐数证据索引)+`ia_cli research-run`;并入 R1.1(merge 946625b) | dev/rd-r2-research-orchestrator@946625b 后 | 自测 31 判定绿;R1 无回归(50 判定);全套回归 129/129 exit 0(全仓口径=tests/128+根 test_env.py,后者为环境探测脚本,外部连通面 11/14 与研发面无关) |
| 11-11 | R2 独立审计 | 七维对抗(真执行面/诚实面/证据索引/实体映射/红线/测试真实性/Skill 对照) | (后台 Agent 对 ac40ef8 diff) | 无 BLOCKER;2 MAJOR+4 MINOR+5 NIT;主体成立(证据索引实测对上快照/红线全过/31 判独立) |
| 11-11 | R2.1 审计整改 | MAJOR-1 S7 gate 改取 compare 对齐门+记 gate_source;MAJOR-2 L4 五行回归纪律16 权威模板+L3 补 E1/E2/E3 指路+research_map RQ9 统一;MINOR-1 诚实拒答豁免 run_ok;MINOR-2 compare 截断披露;MINOR-3 台账语义列 | dev/rd-r2-research-orchestrator(本提交) | 套件 38 判定绿(+7 回归);R1 50/50 与 research_map 32/32 无回归 |
| 11-11 | R3 十问扇出入口 | research-run --fanout: QUESTION_COMMANDS 十问逐条真跑(16 命令 ia_cli+scripts 双通道)+信封留档;Agent 层问(RQ3/RQ9)declared-not-produced;占位符确定性替身(VIEW-…→首条 view_id/A_ID,B_ID→命中前二)且披露;report.md 十问台账;run_step 泛化 _run_proc | dev/rd-r2-research-orchestrator(本提交) | 套件 47 判定绿(+9);全套回归 129/129 exit 0(全仓口径) |
| 11-11 | R4 NIT 清理 | 同分钟目录碰撞→追加序号不覆盖;vp_face root 透传;S3 默认 US+CN 披露;_run_proc 进程启动异常留痕;R1 套件幂等比全档+无前视扩全量 17 份 | dev/rd-r2-research-orchestrator(本提交) | R1 52 判定(+2)/R2 47 判定绿 |
| 11-11 | 用户「全部审批通过」四卡点执行(①③毕/④受阻) | ①merge --no-ff=be8dabd→tag v0.10.0-alpha→Release 441746111→CI 43030767965 绿=基线128;③LIVE 部署 v0.10.0 面(git archive 覆盖+三 key 重注入[注入正则 bug 即时修]+data/.env 保护+冒烟绿);②原则获批无即需项;④无头运行启动器被权限分类器拦([Create Unsafe Agents])待用户放行;登记生产观察=weekly Gate A 拒(ZQ_IMPLIED_AVG 采集缺口,既有非回归) | dev/ops-post-approval-20261111 | 冒烟: changes/research-map/research-run 14步0败/report_generator+app 导入/launchd 在场;全套回归未重跑(纯文档轮+部署面,代码零改动) |
| 11-11 | R5 阶段证据覆盖面轮(无头首轮;操作者代收尾) | 16 指标缺席分解四类: ①假设引用超出 subjects 映射面→证据面=subjects∪假设 refs(标 hypothesis_ref);②注册表外语义 id(CPI_YOY)→精确注记禁猜;③mode A 截断过杀→尾值近似 level(level_source=series_tail_le_publish+DEGRADED 披露+fact_observation_date 留原观测日;无 ≤publish 观测仍真缺席);④真缺席(BUND/CN_OMO_7D/JP_CPI_TOKYO/HY_OAS)=台账不造数;C 层契约零变动 | dev/rd-r5-stage-coverage | 新套件 38/0/0;R1 52/52+R2 47/47 零回归(操作者独立复跑);无头轮停在收尾 Monitor 等待(设计缺陷已修=禁异步泊靠),提交与记账由操作者会话补完 |
| 11-11 | R6 采集面修复轮(操作者网络轮) | D1: G-P1-15 金十停更通道→tushare pro 换源——cpi_yoy=cn_cpi.nt_yoy 真实拉取验证(202609=0.9 月末观测日);ppi_yoy=cn_ppi.ppi_yoy 接线毕但 token 权限档不足(卡点②候选);registry v2.8.1(source_symbol 同步+notes);新纯函数 _tushare_monthly_last+测试 t56;D2: CN_OMO_7D 四路免费源实测全阻(tushare 无接口/央行 502/akshare 1.18.47 零端点源码证/东财 cookie 门)→登记 source-blocked 不造数 | dev/rd-r6-collection-fixes | wp_e 26 OK(t40-t42/t56 换 tushare 桩)/data_batch1 38/0/charter6_p2 88/0/R1 52/R2 47/R5 38/snapshot 46 全绿;版本锁三处随升 2.8.1 |
| 11-11 | R5+R6 发布+LIVE 同步(v0.11.0-alpha) | 用户「批准」+合并纪律更正(验收绿即合并发布不逐次请批,逐次报批仅剩付费类);merge=**9051e7f**→CI 43052903525 绿=**基线129**→tag v0.11.0-alpha→Release 441903695;LIVE 同步 v0.11.0 面(archive 覆盖+三 key 重注入 56/32/40+冒烟绿+**生产树真实拉取终验 cpi=0.9@2026-09-30**);PPI=用户裁定暂不付费先跑通其他(如实缺席留后议);干净 clone 全量回归抓出版本锁漏网 6 处随升(129/129 exit0);AC7 首跑计划入 docs(AC7_RUN_PLAN.md) | main=9051e7f | 干净 clone 129/129+CI 绿+LIVE 冒烟全绿+终验真实值 PASS |
| 11-12 | R7 AC7 真实端到端首跑 | 数据面修复(HSI/HSCEI core 缺失→腾讯 2000 根重采经 env 缝+PPI 真实复拉; snapshot 20261112_v2 Gate A=DEGRADED core 0 缺)+任务A 13 节全景(research-run 十一步 16 命令真跑, 13/13 节无空置)+任务B 17 档/15 机构 M 表八问+分歧矩阵+新鲜 CPI/PPI 更新评注(上游通胀=机构面空白登记)+任务C 三型验证+17 件 VP 重建@v2(B 面 23 机械判定 11 against/5 supports/7 neutral; C 层全未到期如实)+开放题金油比压缩 32.3%仍 80 分位(现场生成, n=6 如实); 四 QB 归档=QB-20261112-001~004 全绑 v2; AC7=EXECUTED(终判留覆盘轮) | dev/rd-r7-ac7-e2e | 13/13 节验收;全套回归 129=128 exit0+1 环境性 FAIL(worktree 清单断言测到本 fork 活 worktree;干净 clone 同套件 31/31 绿=非回归);零引擎代码改动(纯执行轮) |

| 11-12 | R8 独立验证+AC7 合并(操作者轮) | 七面独立复算(不 import 项目代码): 数值面 ZQ−DFF 单项 FAIL(归档 +0.295 实为 +0.305,方向/量级/S1 结论不变,dae5a41 零命中)其余全 PASS(PPI−CPI=4.10/CAPE z=2.999/金油比逐位);档完整性/诚实面(反刍 grep 178 旧档零命中)/Gate A 复算(DEGRADED core 0 missing 逐字段一致)/干净 clone 研究面 339 判定 0 败/红线全净=**零 BLOCKER**;MINOR 处置: ①QB-001 更正评注 C1 随行+草稿五处修正 ②dev 树陈旧工件同步(china_20261112 sha=87d300e3 对齐快照声明+VP 面 20261112);merge=**825eb4f**(docs-only 不另发 tag,LIVE 不受影响) | main=825eb4f | R8 七面 6 PASS+1 单项 FAIL(非 BLOCKER);C 层口径以档内原文"全不可判"为准 |

| 11-12 | R9 采集缺口波(fork 开发+操作者复核) | CN_SF_FLOW 社融换通道 mofcom 直取(根因=本机 LibreSSL 2.8.3 与 mofcom TLS 协商即断,三库同因;修复=curl 子进程零新依赖+_shrzgm_rows/_shrzgm_last 纯函数;真拉 6245.0@2026-04-01,滞后≈7个月如实 DEGRADED);BUND_10Y/2Y=四路证据确认源端封锁维持诚实缺席(TLS 握手后被服务端重置/ECB 303 dataflows 无国别德债/tushare 无);JP_CPI_TOKYO=e-stat 免费通路探明需 appId 新凭证留裁定;CN_OMO_7D 不动;registry v2.8.2 版本锁 15 处/9 文件随升 | dev/rd-r9-noncore-gaps@59ff08e+017e838 | wp_e 29/29+全仓 128 exit0+1 环境性;操作者独立复核=真拉复现(136 行/2026-04/6245.0)+Gate A 注入复算(noncore_missing 5→4+SF_FLOW→degraded)+红线 0+版本锁扫无漏网 |
| 11-12 | R9 发布(v0.12.0-alpha) | merge=**bd8b853**→tag v0.12.0-alpha→Release 442060959;**LIVE 同步被权限分类器拦(与 11-11 启动器同款),待用户放行**——部署脚本已备(/tmp/deploy_v012_live.py: archive 覆盖+三 key 重注入+冒烟含 mofcom 真拉断言) | main=bd8b853 | CI 盯 bd8b8530e7d8(后台);操作者复核全绿后合并 |

## 排队中

- **F 补证轮**: 2026-12-05 观察钟满,引擎自动触发(日历门,勿手工提前)。
