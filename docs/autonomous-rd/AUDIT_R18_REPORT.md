# Audit-R18(R62) — 全球宏观地图问句: 共享研究计划+读者报告五面契约

- 基线: 57bcb6659704a0321d234e645b746f38644b831a(分支 dev/audit-fix-r1,PR #1)
- 代码修复固定 SHA: d3dea052585d2e433d92576afe5f70b144722ddd
- 日期: 2026-11-18/19 | 状态: 待外部审计(不并 main、不合并 PR、不部署)

---

## 〇、指令与产品验收场景

第十八轮指令(用户原文): 在 PR #1/dev/audit-fix-r1 完成收尾,基线 57bcb66;
连续完成复现、修复、真实运行、独立复核、推送和 CI;合并与上线由用户决定。
产品验收唯一场景=原问逐字输入(不手填指标代码):

> 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前
> 和最新一期,分别处于什么增长、通胀和货币政策环境?过去一年最重要的三个转折
> 是什么,谁先变,谁跟进或背离?证据最充分的传导机制是什么,还有什么解释,
> 哪个指标能区分它们?历史上哪些时期结构最像,当时其他经济体是否同步,随后
> 3、6、12个月经济和主要资产实际怎么走?

五任务: ①research-one 正常入口复现+共享研究计划+「3个月前」(日历点)与
「事件后3个月」(事后偏移)分记+回放截止 2026-11-18+只输入原问;②完整读者
报告(一句总判断+四地三时点对照+有文字的传导图+三转折按日期+关键数字带来源
单位观测日+历史栏≤3段+美国类比标注+样本不足如实);③逐条复核(央行公告
四分+同观测日三利率复算+传导逐环四件套+情景触发证伪一致+证据不足缩小结论);
④修误通过+反例(机制正文空/None、必需图表缺失、明确指标遗漏须阻止交付归档;
「我关注10年期美债收益率。过去半年,只比较10年期美债收益率和30年期美债收益
率。」两项都保留,缺任一阻止归档);⑤固定提交→真实 Agent 重生成→复核抽查
复算→归档回读 SHA-256→全量离线测试→PR 最终提交 CI。

## 一、基线复现(五缺陷全数在档)

| # | 基线表现(57bcb66) | 类别 |
|---|---|---|
| 1 | 原问 plan: economies=[US,CN,EA,JP] 但 metrics=[] → note「降级经济体概览」,run_ok=True 可交付归档 | 答非所问误通过 |
| 2 | 「我关注10年期美债收益率。过去半年,只比较10年期…和30年期…」→ metrics=[UST_30Y]: 前导句把 UST_10Y 首次命中位锚在限定词前,只记首次位→限定内再提被误删 | 明确指定指标遗漏(R17 未测形) |
| 3 | 「12个月前」「随后3、6、12个月」命中 R10/R13 残缺数量扫描 → unparseable | 时间语义未按计划消费 |
| 4 | reader_map 五面(总判断/走位/传导/转折/历史)无契约——机制正文空、转折数值错、历史 4 段均无拦 | 判定契约缺位 |
| 5 | 篡改在场 MAP_REPORT 后归档内部重跑 report 重渲洗白 | 交付件防篡改缺位 |

(复现证据: 基线行为在本轮门测试 §A/§B/§C 断言的反面+git 双跑对照——HEAD 与
R18 工作树 map_entities 同返 [UST_30Y],证明缺陷②为基线既有非本轮引入。)

## 二、共享逻辑修复(五文件,+1 新模块)

1. **scripts/research_map_planner.py(新,~560 行)**: `detect_map_question`
   严格触发(≥2 经济体∩{US,CN,EA,JP}+≥2 维度词[增长/通胀/货币政策]+形状词
   [地图/转折/传导/结构最像/环境]);`plan_map` 地区×维度→注册表指标(口径
   注记: DFEDTARU=政策目标上限/DFF=市场日频/JP_POLICY_RATE=月均≠宣布值/
   ECB=变更日观测)+`US_RATES_TRIO` 上下文(任务③三利率复算面);
   `parse_point_anchors`(N个月前/N年前→cutoff−N月,kind=point)与
   `parse_ex_post_offsets`(随后N、M个月→事件日+N月,kind=ex_post)分记+
   anchor_semantics_note;`point_values` bisect ≤as_of(水平序列
   derived_yoy_pct——指数漂移不作环境值,禁以现值冒充锚值);`turning_
   candidates`=过去一年 max|3 月滚动Δ|确定性排序 top9(水平序列先转同比空间);
   `render_map_report`=MAP_REPORT.md 确定性装配(零生成,判断文字全部来自
   Agent 席 reader_map 原文)。
2. **research_orchestrator.py**: S1 地图分支注入共享 research_plan(取数/报告/
   验收三段同源);`consumed_time_spans` 透传 `_question_window`(仅地图问句
   ——非地图路径零变化,R10-R17 残缺数量语义保全);计划指标 tier=**planned**
   (序列缺席=缺数格披露不阻断;词面命中仍 required 缺数阻断)+「地图计划指标
   缺数」点名注记;S4 缺席计划指标 honest skipped_step;**map_entities 全命中
   位记录**(re.finditer 全位置),只比较限定按「限定后任一命中」判(修缺陷②,
   R17 全锚保全)。
3. **research_contract/judgment_contract.py**: `_map_checks` 五面契约——
   headline 非空/regions 全走位/transmission 逐环四字段(观察事实/因果假设/
   竞争解释/区分指标∈计划∪证据面)/turnings 恰 3 且数值回贴引擎月末口径
   (水平序列与候选面同口径同比空间;不符=CONTRADICTED)/history 1..3 段含
   ex_post 3m/6m/12m 非空;report=None 守卫(冻结夹具面)。
4. **agent_judgment.py**: 机制环正文空/None=SCHEMA 拦截;BLOCKING_BLOCKED_
   CLASSES 新类 `map_required_face_missing`;`_reader_map_faces_summary`
   粗粒度面随档(attach 成功才 complete)。
5. **ia_cli.py**: map 问句 report 段渲染 MAP_REPORT.md+旁挂锚
   `MAP_REPORT.sha256`(磁盘≠锚=单改: 拒付**不重写**保全证据,归档重跑同拒
   不洗白;文件未动而装配变=合法修订重渲更新锚——REVISE 闭环不误伤);
   archive: MAP_REPORT 缺席拒归(map_required_face_missing),读者报告+锚
   随包归档;envelope produce/discipline 增 reader_map 契约。

## 三、门测试(tests/test_audit_r18_gate.py,40/40)

§A 识别与计划(原问触发/三近失不误触发: 单经济体、无维度词、经济体不足;
四地×三维 18 指标;锚 kinds/labels/as_of 逐位;「一年前」→12 月;ex_post
[3,6,12];语义注记;EA/JP 增长缺口点名;三利率上下文)——§B 窗口(计划时间词
消费后「过去一年」正常解析;同问无透传仍 unparseable=R10 保全;只比较零回归)
——§C 正式 plan 冻结根(原问 run_ok+research_plan 入档+planned 分级+缺数注记
+转折候选同比空间;只比较两案正反)——§D 契约反例×10(空串/None/reader_map
缺席/空总判断/缺字段/转折 2/转折 4/历史 4=NOT_VERIFIED;数值漂移/假区分指标
=CONTRADICTED)——§E 交付归档门(空洞→map_required_face_missing;正例全链
五面俱全+SHA 回读逐位;篡改拒付拒归不洗白+删除恢复通道;MAP 缺席拒归;
只比较正反案)。

合成隔离: 全部夹具 role=R18-SYNTHETIC-ISOLATED-TEST+synthetic:true 双写。

## 四、回归与复放

- 既有门复跑全绿: r4(29)/r5(30)/r6(25)/r7(37)/r8(30)/r9(33)/r10(29)/
  r11(29)/r12(56)/r13(56)/r14(79)/r15(72)/r16(49)/r17(56)+t3(43)+
  charter6 p0/p1/p2/p4。
- 全量电池: 189 绿+phase6 预期红(状态波提交后转绿,190 件口径)。
- 复放四包: BLIND sha feaa1536 逐字节+独立复算 64/64;F10 sha 6e5fcf4a 逐字节;
  cn-task-b recompute_r6b 105/105;e2e-corrected 三争点复算全吻合。
- 复杂度: 生产 86f/52237L(基线 85f/51303L;+1 模块=本轮新能力本体,+934 行)。

## 五、真实运行(任务⑤,代码 d3dea05,零合成)

- 引擎树: ${TMPDIR}r18_real_work/engine_merged(仓码 d3dea05+LIVE 数据面副本,
  LIVE 本体零接触);CN_PMI_MFG 226 月序列逐字节派生自仓内冻结包 cn-task-b
  macro_20261117.json(R6-02 正式入口 provenance 随附+源 sha 登记);快照重建
  research_snapshot_20261118(事实 104,core 缺 0,Gate A DEGRADED=4 项非核心
  缺席如实)。
- 原问逐字 plan: run_ok=True;research_plan 四地×三维 18 计划指标+三利率上下文;
  点值 12 格+缺数 7 格+维度缺口 2 条;转折候选 5(CPI+1.73pp 居首)。
- Agent 席真实判决(零合成,数值全部引擎面复算): l3 CON-1(DFF 全年宽松叙述
  与序列相左)+MECH-1 三环(E1 观察/E2 假设标注/E3 叙事+证伪阈值带数字);
  l4 SCN-A 基准/SCN-B 反例(证伪指标 CORE_PCE/CPI 在证据面,deadline 2027-03);
  reader_map 五面(总判断/四地走位/传导三环四件套/三转折=CPI 2026-05+DFF
  2026-02+JP 2026-07 均引擎候选面数值回贴/历史两段: 2021-06..2022-06 主类比
  +2017-12..2018-12 软着陆对照,ex_post 3/6/12 月全实测)。
- attach: 首提 2 项 SCHEMA 纪律(敏感变量 1-2 个)修正后 **attached=True,
  契约 VERIFIED(map_fail=0)**;期间两处内容自校(CN 走位占位句→实测
  49.77 均值/5 月 sub-50;总判断「全年收缩区」→「荣枯线附近弱势徘徊」)。
- 任务③复算面: 同观测日 2026-11-16 UST_10Y 5.12=TIPS_10Y 2.92+BEI_10Y 2.20,
  残差 0.000pp;央行口径四分逐指标注记(DFF 市场日频/DFEDTARU 目标上限仅现值
  4.0/JP 月均≠宣布值/ECB 变更日观测)。
- 独立语义审查(零上下文独立席): 首审 **REVISE(4 必修)**——①政策事件
  日期系统性错误(降息实为 2025-12-11 3.89→3.64、加息实为 2026-09-17
  3.63→3.88;CON-1 basis 选择性跳月;「政策年内由降转升」对日历 2026
  不成立)②BEI 年变化符号(+11bp 实为 −7bp 同日/−3bp 月末)③CN「7 月
  起重回荣枯线下」与 9 月 50.1 相矛盾④历史段 CN 锚 51.7 无来源;另
  MINOR 组(CPI 基月注记/2018 峰值月/JP 区间/BEI 参照日/link 区分指标
  注记/DFF 带状措辞)。操作者对照 DFF 日频独立证实两级台阶日后修订:
  判决四必修+MINOR 全量改正(CON-1 重写采用等式括注文法与校验器
  掩码形态一致,携带全月序列+台阶日+窗口外两降),重新过机器契约
  attached=True/VERIFIED/unbound=0。**闭环复验 UPHELD(可归档)**:
  四必修逐日对值关闭、回归电池 20 项全绿(含 2017-18 段 CN 中锚 50.8
  补验)、MINOR 组全部落地;残留 3 NIT 措辞层不阻断(Q3/Q4 边界/
  「年中」标签/l3 ref 配对装饰),记下轮候选。裁决链 append-only 三档
  (-01 REVISE/-02 修订后重录/-03 UPHELD),失败证据不洗白。
- 归档: deliverable=True(report 段全绿: machine_verified+UPHELD
  fresh+copies 一致)→ 归档包 r18-map-20261118T160925Z(9 件:
  report/report.md/FULL_REPORT/MAP_REPORT+锚/agent_judgment/evidence_
  index/views_digest/AGENT_SEAT_ENVELOPE),content_sha256=
  90146e0658a5fdc115acdd17c960cd78888e7df8a998dc52e0dd9a6d61c31399
  (报告=裁决=归档三处同锚);**SHA-256 回读**: 归档 MAP_REPORT.md=
  2d6260e6cb0599c9…、agent_judgment.json=f84dfbac4dd0de30…、
  report.json=35c7f389401b432c… 与运行目录/读者件三方 MATCH,旁挂锚
  MATCH。证据包入仓 docs/autonomous-rd/r18-evidence/(交付件+裁决链
  三档+README 复放口径)。

## 六、真实运行产物坐标

- 读者报告(可打开直读): docs/autonomous-rd/r18-evidence/MAP_REPORT.md
  (仓内入档版=归档版=运行版三方逐字节一致,sha 2d6260e6cb0599c9…)
- 原问四问在正文中的位置: ①四地三时点环境对照=「四地三时点环境对照」
  表(12行,每格附实际观测日,缺数格如实标「数据不可得」+检索范围
  注记;另「各地区环境走位」节四地各一段从-到叙事);②三转折谁先变
  =「过去一年的三个转折(按日期)」表(前后值=引擎月末口径,
  first_mover/follow_or_diverge 列,turning_note 分记事件日与候选窗
  端点);③传导机制+竞争解释+区分指标=「证据最充分的传导机制(有
  文字的传导图)」节(三环,每环观察事实/因果假设/竞争解释/区分指标
  四件套,JP_CPI_TOKYO_YOY 缺席如实注记);④历史类比+同步性+事后
  3/6/12 月=「历史上结构最像的时期(可验证;≤3段)」节(两段,主类比
  2021-06..2022-06+对照 2017-12..2018-12 均美国指标类比标注,
  ex_post 3/6/12 月全实测,日历点/事后偏移口径分记);关键数字来源=
  「关键数字与来源(实际观测日)」节。
- 运行目录: ${TMPDIR}r18_real_work/real_run/20261118T160925Z_*/
- 判定档: ${TMPDIR}r18_real_work/judgment_real.json(入档版=仓内
  r18-evidence/agent_judgment.json)
- 一行复用: `python3 ia_cli.py research-one --stage auto --question "<原问>" \
  --engine-root <引擎根>`(plan→attach→report→archive;Agent 席按
  AGENT_SEAT_ENVELOPE.json 产判定+reader_map 后接续)

## 七、坑(操作者)

1. Write 工具不展开 `${TMPDIR}`——judgment 落到字面目录,attach 才暴露;临时
   路径一律先 shell 展开再传。
2. r17 门夹具启示: attach 拒收在 CLI 面=attached=False(rc=0)——门断言要锚
   data.attached+violations,不能锚进程码。
3. 快照 series_store_clean 只存清洗统计,序列本体在 series_store——复算脚本
   读错面全部空表。
4. CPI 序列缺 2025-10 单月→自算 yoy_map 出 NaN,引擎点值/候选用自身月末+同比
   派生不受影响;自算复算须对齐引擎口径(月频取月末、同比用最近前值)。

## 八、状态

- 推送/CI: dev/audit-fix-r1 = 57bcb66→d3dea05(修复固定 SHA)→**26885739fa132c47dac854de9f20b9f778251143**(状态收口: 报告+证据包+状态波)→CI 回填(仅 docs);PR #1 覆盖推送(R1-R17→R1-R18)。
- CI: 状态收口 `2688573` 推送后 run **44350710810**(head_sha=26885739fa132c47dac854de9f20b9f778251143,全 40 位逐位核对)三 job 全绿: gates ✅ / tests (3.11) ✅ / tests (3.12) ✅——本回填提交前的提交树全绿由该 run 复核;回填提交(仅 docs)推送后以其自身 run 复核。
- PR #1 更新: R1-R17 → R1-R18(标题+R18 节: 五缺陷/五文件修复/REVISE→UPHELD 闭环/归档三处同锚+SHA 回读/终跑 CI 链接)。
- 停等外部审计: 不并 main、不合并 PR、不部署、不开新轮。
