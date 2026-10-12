# 系统升级计划：Global Macro Research & Allocation Agent

> 依据 2026-10-11 升级提示词制定。**硬约束：周报产出形式与八节结构不变**，新能力装入现有结构。
> 状态标记：✅已完成 | 🔧部分完成 | ⬜未开始

## 一、能力差距矩阵

| 目标能力 | 现状 | 差距 | 优先级 | 状态 |
|---|---|---|---|---|
| 数据采集（全球/A股/宏观/新闻/利率） | 9步流水线每日运行 | 基本达标；新闻AI摘要调用已下线的DeepSeek API | P0 | ✅已修 |
| 流水线失败传播 | run_weekly无论成败永远exit 0 | 失败被静默吞掉 | P0 | ✅已修 |
| 体制切换"连续两周"确认 | 比较相邻两个**文件**（每日一份）→两个自然日即可确认"两周验证" | 时间语义错误 | P0 | ✅已修 |
| 宏观指标频率标注 | 6个月度FRED序列的change无频率标注流进周报 | 统计频率混淆 | P0 | ✅已修 |
| 锚点时间元数据 | 只有value+source_file，无采集日/观测日 | 时点不可追溯 | P0 | ✅已修 |
| 校验失败阻止状态污染 | thesis.json无条件回写 | 错误数字可污染论点状态 | P0 | ✅已修 |
| framework.md与代码一致 | 体制映射表为v1旧规则（无类滞胀分档） | 文档与代码不一致 | P0 | ✅已修 |
| 配置引用一致 | news_collector/daily_report_generator仍引用死掉的DeepSeek | news已迁GLM；daily_report_generator为遗留脚本不在流水线，标记弃用 | P0 | 🔧 |
| 报告校验覆盖时点 | validate_report只比数值不比观测时点 | 锚点带obs_date/as_of，比对时显示观测日；日频行情滞后>5天提示⚠️时点滞后（月度序列免检，不拦截回写） | P1 | ✅已修 |
| 宏观研究深度（体制成因/驱动/切换路径） | 评分卡只输出当期分数+体制 | attribute_regime反事实分解：剔除单指标后体制翻转者=关键驱动，写入评分卡JSON/MD，随data_assembler进周报prompt | P1 | ✅已修 |
| 跨资产传导机制分析 | 报告靠模型自由发挥，相关性矩阵刚接入 | 缺结构化传导分析 | P1 | ⬜ |
| 资产配置研究引擎（评级/超低配/条件观点） | 无 | allocation_engine.py渲染观点库进周报prompt；ALLOCATION_STATUS块回写评级/确信度/history；评级变更行自动登记预测 | P2 | ✅已修 |
| 配置观点+预测的长期记忆 | 仅thesis.json（9论点），无观点库/预测记录 | allocation_views.json：9资产观点+predictions[]（方向/期限/deadline/裁决）；PREDICTION_STATUS块裁决hit/miss/expired | P3 | ✅已修 |
| 月报/季报体系 | 无（仅周报） | monthly_review.py/quarterly_outlook.py，月末/季末最后一个周五由周报主流程自动触发，读整月/整季原始JSON | P4 | ✅已修 |
| 证据分级v2/禁语v2 | v1规则在硬约束块 | 系统提示词主体不变（秘书角色），V2正式清单以规则附录接入提示词末尾；style_constraints/framework.md/data_validator禁语扫描三处同步 | P1 | ✅已修 |

## 二、目标架构（最小必要新增）

```
现有9步采集(P0修复后) ──┐
                       ├→ data_pack + anchors(带as_of/obs_date)
scorecard(跨周确认) ───┤
                       │
              ┌────────┴─────────┐
              │ P2 配置研究引擎    │  scripts/allocation_engine.py
              │ 输入: scorecard+  │  读 config/allocation_views.json(观点库)
              │ 数据包+相关性     │  输出: 各资产评级/倾向/条件/反证 → 拼入数据包
              └────────┬─────────┘
                       ↓
         周五08:00 report_generator(八节结构不变,
         第五/七节装载配置观点,第八节论点追踪不变)
                       ↓
         校验(先) → thesis回写(数值错误则跳过) → allocation_views回写(同机制)
                       ↓
         P4: 月末/季末附加 monthly_review/quarterly_outlook 生成器
         (读整月/整季原始JSON,不拼接周报)
```

**存储选型**：继续JSON（allocation_views.json 与 thesis.json 同构），不引入SQLite——项目规模不需要。

## 三、P0 修复清单（2026-10-11 完成，全部有代码）

| # | 缺陷 | 修复 | 文件 |
|---|---|---|---|
| 六.1 | news AI摘要调用已下线DeepSeek | 迁移GLM流式（与周报同通道） | scripts/news_collector.py |
| 六.2 | 流水线失败仍exit 0 | 任一步失败sys.exit(1)，run_daily.sh如实传播 | run_weekly.py |
| 六.3 | 月度指标change无频率标注 | series_map加freq，输出"[Monthly]+变化区间+观测日" | scripts/rate_expectations.py |
| 六.4 | 两自然日误触发"两周确认" | resolve_transition纯函数+_prev_distinct_week_file（ISO周去重，同周文件=回声） | scripts/macro_scorecard.py |
| 六.5 | 锚点无时间元数据 | 每锚点带as_of(采集日)+obs_date(观测日,取兄弟.date字段) | scripts/data_validator.py |
| 六.6 | 校验不覆盖时点 | 锚点侧已就绪（obs_date），报告侧规则P1接入 | 🔧数据侧完成 |
| 六.7 | 校验失败仍回写thesis | 先校验后回写，_has_numeric_errors门禁 | scripts/report_generator.py |
| 六.8 | framework.md体制映射v1 | 同步为v2.0映射+跨周确认规则说明 | config/framework.md |
| 六.10 | 新闻摘要降级原始标题 | 根因即六.1（DeepSeek死API），随迁移修复 | scripts/news_collector.py |

**回归测试**：tests/test_p0_fixes.py（纯函数单元测试+真实数据集成测试）

## 四、后续阶段路线

### P1 研究增强（2026-10-11 完成4/4）
1. ✅校验规则接入obs_date：比对时显示观测日；日频行情观测日落后报告日>5天→⚠️时点滞后（提示级，不拦截回写；月度FRED序列免检）
2. ✅提示词配置化：SYSTEM_PROMPT/硬性约束外移至 config/prompts/system_prompt.md + style_constraints.md，热加载；文件缺失硬中断（配合六.2失败传播）
3. ✅证据分级v2/禁语v2正式接入（用户提供清单）：**系统提示词主体不变**（仍为"首席宏观研究员兼投资委员会秘书"版），其引用的"证据分级v2和禁语v2"以规则附录形式接在提示词末尾（★=独立证据数量×机制覆盖×观察期跨度，未解释重大反证封顶3★，关键数据缺失不评级，不得机械继承上期星级；禁语中英文全清单；数值须绑定指标ID/单位/观测期/来源；相关性不得直接当因果）。同步处：style_constraints第1/3/7条改为引用v2定义、framework.md禁止用语节升v2.0、data_validator禁语扫描扩为v2清单（"绝对"豁免绝对收益/绝对估值等金融惯用词防误报）
4. ✅体制归因：attribute_regime反事实分解（剔除单指标→体制翻转者=关键驱动），写入评分卡JSON字段regime_drivers/regime_counterfactuals + MD"体制归因"节
   - 首跑实证(2026-10-11)：类滞胀的关键驱动=零售销售环比(+2)与WTI油价(+2)；另纠正了今晨旧代码因同周回声提前"确认"类滞胀的问题→正确回到待确认(3★)

**回归测试**：tests/test_p1_fixes.py（26项：归因正反例/真实评分卡字段/提示词v2加载/时点检查边界/禁语v2豁免逻辑）

### P2 配置研究引擎（2026-10-11 完成）
- config/allocation_views.json：9资产观点库（美股/利率久期/信用/美元/贵金属/能源/A股港股/加密/现金短债），评级取超配/标配/中性/低配/观望，含理由/正反证据/升降级触发器/失效条件/关联论点/history；初始评级与thesis.json 9论点一致
- scripts/allocation_engine.py：render_views_block渲染进周报prompt（第五节各资产小节末尾标注"配置观点: 评级|确信度"，触发条件跨越才输出调整提案）；update_allocation_status回写（备份.bak+原子写，与thesis同数值门禁）
- 回写机制复用THESIS_STATUS模式：ALLOCATION_STATUS块；仅评级变更行可附pred/pred_weeks自动登记预测
- **报告八节结构未动**——观点只作为一行标注嵌入现有小节

### P3 预测追踪（2026-10-11 完成，随P2落地）
- allocation_views.json的predictions[]：pred_id/方向/horizon_weeks/deadline/status(open/hit/miss/expired)/resolved_note
- 每周render时扫描到期预测并在prompt标注"⏰已到期,本周必须裁决"；报告第七节给判断，PREDICTION_STATUS块回写裁决
- 评级变更自动生成新预测（有方向有期限才收，id顺延，deadline按周数计）

### P4 月报季报（2026-10-11 完成）
- scripts/monthly_review.py：月末最后一个周五由report_generator主流程以子进程触发（无需新launchd任务，避开launchd后台进程坑）；--dry-run可单独装配数据
- scripts/quarterly_outlook.py：季末月(3/6/9/12)最后一个周五触发
- 数据口径：整月/整季原始JSON回溯（月度区间表月初→月末/最高/最低、评分卡时间线、论点轨迹、预测命中统计、各月末资产水平），不拼接周报
- 提示词：config/prompts/monthly_review_prompt.md + quarterly_outlook_prompt.md（热加载）
- 附加报告失败只记日志不回滚周报（周报已落盘）
- 产出：output/monthly/monthly_review_YYYYMM.md、output/quarterly/quarterly_outlook_YYYYQn.md
- 2026年触发日：10-30月报、12-25月报+季报、2027-03-26季报等

## 五、明确不做（按升级提示词第七节）

券商接入/实盘持仓/资金管理/自动交易/订单执行/真实归因/多Agent架构/网页前端/云服务。

## 六、验收对照（升级提示词第九节）

- 第一~三周循环：✅P2/P3完成（观点库+回写+条件观点+预测追踪）
- 第四周月度评估：✅P4月报完成（首次实跑：2026-10-30）
- 季度展望：✅P4季报完成（首次实跑：2026-12-25）
- 证据可追溯：✅P0完成（锚点as_of/obs_date+校验日志+thesis history+allocation history+预测裁决记录）
- 待办：证据分级v2/禁语v2正式清单（用户提供后接入config/prompts/）

---

# 第二轮独立代码审查(2026-10-11, 分支 dev/round2-audit)

目标: 验证第一轮P0-P4是否真正达到"持续宏观研究与理论资产配置建议系统"要求,只修不加新模块。

## 一、发现缺陷与修复

| # | 缺陷 | 位置 | 修复 |
|---|------|------|------|
| 1 | 无锚点/锚点非当日仍回写长期状态 | report_generator.py | classify_result→PASS/DEGRADED/FAIL;FAIL跳过thesis+allocation回写 |
| 2 | 指标校验只对数值、不看指标ID与观测日,前值当现值不可检 | data_validator.py | INDICATOR_SPECS按指标ID+数值+单位+观测日联合校验;TIPS/UST容差收紧至0.005 |
| 3 | 仅确信度变化不落盘(缺陷#10) | allocation_engine.py | 解析到任一合法观点行即写盘;评级/确信度history分条记录 |
| 4 | 无证据预测裁决可回写(缺陷#12) | allocation_engine.py | hit/miss裁决note必含数字;否则拒收保持observing |
| 5 | 预测无机器可判规格 | allocation_views.json+engine | pred_metric/pred_op/pred_target/evidence_ref结构化字段;到期自动裁决 |
| 6 | 评级量表混用(标配/中性) | engine+views+prompt | 量表v2=超配/标配/低配/观望;中性按v1旧词拒收并自动迁移 |
| 7 | 量化触发器真伪由模型口说 | engine+prompt | evaluate_quant_triggers程序核验:已触发/未触发/待验证;复合/定性条件标待验证 |
| 8 | 月报/季报在期间未完时提前出报(12-25提前出Q4) | report_generator.py | pending_completed_month/quarter=期间结束后第一个周五;2026-12-25→None(回归测试覆盖) |
| 9 | 月报收益率/利差用价格%而非bp | monthly_review.py | 收益率/利差变化×100报bp,百分比序列报pp |
| 10 | 月度数据重复采集不去重、不披露缺口 | monthly_review.py | 按观测日去重(同观测日留最新采集);coverage_report披露缺口 |
| 11 | 季报只用3个时点 | quarterly_outlook.py | 逐月聚合整季:季初/季末/季内极值+各月末水平 |
| 12 | 预测命中率全历史口径 | engine | predictions_in_period按统计周期(月/季) |
| 13 | 账户管理职责残留提示词 | 3个prompt | 统一"全球宏观首席研究员兼跨资产策略师",显式不管理账户/不执行交易;证据分级v2+禁语v2全量接入 |
| 14 | 恒真断言测试(or True) | tests/ | 删除,改可证伪断言 |
| 15 | 触发器阈值文本被当数值偏差误报 | data_validator.py | 阈值/条件语境(≥/若/回落至…)跳过;语境逐数值判定(12字符局部前视),不整窗共享 |
| 16 | 窗口串到相邻指标(BEI 2.35误报为TIPS) | data_validator.py | 窗口遇相邻指标名(BEI/CPI/30Y…)截断;bp形态归一(1229bp↔12.29);周变化值(=|现值-前值|)跳过 |

**实弹验证**: 新校验器跑真实weekly_report_20261009.md+anchors_20261009.json,唯一非豁免警告=🚨前值当现值[TIPS_10Y](报告2.93%为上周前值,本周现值2.92%)——正是审查专项(8)点名的问题,已在生产报告中实际发生并被新门禁捕获。

## 二、角色与纪律(第4项)

system_prompt/monthly/quarterly三提示词统一策略师角色+六步流程+证据分级v2+禁止用语v2;禁语校验含绝对/必然豁免逻辑(绝对收益≠绝对化);时点滞后为⚠️级不拦截回写。

## 三、端到端验收(第5项)

- tests/test_e2e_four_weeks.py(47检查): 固定fixture四周仿真 W1初始观点→W2仅确信度变化落盘→W3降级触发+评级变更+新预测登记→W4预测裁决(GLM带证据hit+引擎自动miss)+9月月报(非预览/bp/UNRATE去重/覆盖披露/周期预测统计)+Q3季报整季聚合+12-25与2027-01-01触发回归+坏报告FAIL门禁。
- 数据装配→模拟输出→验证分级→状态更新→月/季报生成全链路闭环。
- tests/test_glm_live.py(RUN_GLM_LIVE=1): 真实GLM冒烟——锚点渲染观点块→真实API输出状态行→临时副本回写→无证据裁决拒收。实测5/5通过,模型遵从量表v2并按引擎核验结果表述"已触发"。

## 四、测试结果(2026-10-11)

| 套件 | 通过/失败 | 性质 |
|------|-----------|------|
| test_p0_fixes | 22/0 | 离线 |
| test_p1_fixes | 36/0 | 离线 |
| test_p2_fixes | 63/0 | 离线(临时副本) |
| test_p4_fixes | 42/0 | 离线(真实数据优先,fixture兜底) |
| test_e2e_four_weeks | 47/0 | 离线固定fixture |
| test_glm_live | 5/5 | 真实API(显式开启) |

## 五、触发日历更正(取代第一轮P4节)

月报=期间结束后第一个周五: 2026-10-02→202609, 11-06→202610, 2027-01-01→202612。
季报=季末后第一个周五且月份在1/4/7/10: 2026-10-02→2026Q3, 2027-01-01→2026Q4。
**2026-12-25不触发任何月报/季报**(12月/Q4未完结;原"12-25月报+季报"为第一轮缺陷)。
10-16为普通周报日(10月首个周五10-02已出9月月报)。

## 六、未实现/未验证能力(如实声明)

- 真实FRED/Tushare月度序列的整月回溯依赖data/daily历史文件留存;若历史被清理,月报自动降级fixture口径测试所示结构。
- 预测自动裁决仅覆盖单指标规格(带metric/comparator/target);复合条件预测到期仍需GLM/人工裁决(引擎标inconclusive)。
- GLM输出质量属模型遵从性问题,程序门禁只保证"非法值/无证据/量表外"必被拒,不保证研究结论正确。

---

# 第三轮: 研究决策可靠性与长期闭环验证(2026-10-11, dev/round3-reliability)

目标: 不新增功能,提高现有系统的研究可靠性。核心=研究观点的长期维持与按真实新增证据修正,
不因模型改变想法而擅自改变评级;过去的预测被客观检验;每次观点变化能解释机制/定价/反证。

## P0-1 评级变更门禁(allocation_engine.py)

模型输出的新评级不再直接落盘,须满足二选一: (a) 引擎核验为"已触发"的同向触发器;
(b) ≥MIN_EVIDENCE_FOR_RATING_CHANGE(2)项通过程序验证的结构化证据; 转/自"观望"放宽为1项。
不满足→保留原评级+proposals留档(被拒原因+证据拒收明细),同向21天去重(只累计repeat);
后续同向变更落地时旧提案标superseded(反向不标,留21天公示)。变更经触发器路径/证据路径
均写last_change审计(date/from/to/via/evidence/note)与独立history条目("评级:"前缀)。
_change_direction: 观望→任何表态=resume(须证据,不得借降级触发器直接放行)。

## P0-2 预测全生命周期(P0-2)

字段: pred_id/date_made/asset/direction/horizon_weeks/deadline/status/verify_mode/
observe_from/observations[]/premise{metric,op,target}/premise_triggered_date/resolved_*。
- verify_mode双模式: touch(观察期内触及,可提前hit) vs expiry(截止日水平,不得提前裁决),不混用。
- record_observations每期回写: 前提规格程序判定(兑现→转观察中,observe_from=前提观测日,
  截止日不顺延); 观察中预测按观测日去重记录锚点值(同观测日最新采集覆盖)。
- evaluate_predictions引擎裁决: 只用观察窗[observe_from|date_made, deadline]内观测(禁未来数据);
  窗内无记录回退锚点(锚点obs_date须落窗内); touch到期未触及→miss; expiry按窗内最后观测;
  前提至截止日未成立→not_yet_triggered终态; 无数据→inconclusive不硬判。
- 裁决权威序: 引擎hit/miss > GLM。GLM不得覆盖; engine inconclusive允许GLM附窗内引用补位
  (引用数值/观测日须与窗内记录吻合); expiry未到期拒绝GLM提前裁决; 前提已程序触发时
  拒绝GLM改判未触发; 引擎终态后拒绝GLM转观察中。

## P0-3 证据分级v2程序校验

evidence[]每项{metric,value,obs_date,mechanism,contrary?,explained?}逐项验证:
指标在锚点中(虚构嫌疑拒)/数值容差(相对0.2%或绝对0.005,bp形态归一)/观测日与锚点一致/
逐指标新鲜度(过期不作当前证据)。星级STAR_RULES: 1★1项→5★5项3类机制3观察期+反证已解释;
同指标只计一次(distinct metric); 同ISO周=1个观察期(月度值连引四周≠4期); 未解释重大反证
封顶3★; key_metrics缺失封顶2★。确信度上调不得超过程序星级,下调自由;被拒记录为
"确信度N★"提案。星级≠预测概率≠资金比例。

## P0-4 数据新鲜度(data_validator.py)

区分obs_date(观测日)/as_of(采集日); FRESHNESS_RULES按指标频率: 行情5天/macro 7天/
rate_economy月度45天/china 7天(.close仍5天)/scorecard 10天/默认14天。
is_fresh_anchor逐指标判龄; stale_anchor_warning明示"不得作为当前有效证据";
verify_evidence_items对过期证据拒收(第三轮新增)。FAIL分级禁止一切研究记忆回写(第二轮保留)。

## P1-5 研究链路(report_generator.py prompt)

观点输出须按链路作答: 宏观事实→变化驱动→经济金融传导机制→资产价格影响→市场定价
→风险与反证→理论配置倾向; 不可量化机制标注"研究假设"; 禁止评分卡→配置跳步、
相关性→因果。周报八节结构不变。

## P1-6 触发器v3

单指标/all(且)/any(或)复合; sustain_weeks连续N周确认(观点库存trigger_state{consec,last_eval},
断档>10天重置为首次跨越; 中途回落清零); 状态triggered/not_triggered/unverifiable/sustaining;
渲染与回写同函数(persist=False不改动状态)。

## 测试(第六步)

| 套件 | 结果 | 性质 |
|------|------|------|
| test_p0_fixes | 22/0 | 离线回归 |
| test_p1_fixes | 36/0 | 离线回归 |
| test_p2_fixes | 81/0 | 离线(v3语义重写,临时副本) |
| test_p4_fixes | 42/0 | 离线回归 |
| test_round3_p0 | 89/0 | 第三轮P0单元: 新鲜度/证据分级/触发器/门禁/生命周期/裁决权威 |
| test_round3_adversarial | 24/0 | 任务书9个对抗用例+or-True源码自查 |
| test_e2e_four_weeks | 59/0 | 连续四周同一状态: W1初始化→W2证据增厚仅确信度变化→W3触发降级+被拒提案+新预测→W4证据升级superseded+预测裁决 |
| test_glm_live | 8/8 | 真实GLM API(RUN_GLM_LIVE=1; 实测GLM提交非日期obs_date的证据被程序拒收,台账为空) |

离线合计353项检查全通过; test_glm_live单独统计。旧test_glm_live.py:89的`or True`恒真断言已删除,
S0源码扫描(scripts/)确认无恒真短路。

## 修复前后能力对比(交付①)

| 能力 | 第二轮(修复前) | 第三轮(修复后) |
|------|----------------|----------------|
| 评级变更 | 模型输出直接落盘 | 门禁: 同向触发器已触发或≥2项验证证据; 否则保留+提案留档21天去重 |
| 确信度 | 模型说几星就几星 | 上调≤程序星级(证据分级v2); 关键证据缺失封顶2★ |
| 证据 | note自由文本 | 结构化evidence逐项程序验证(指标/数值/观测日/新鲜度),台账留档 |
| 预测裁决 | GLM说hit就hit | 引擎按观察窗记录权威裁决; GLM仅补位且引用须吻合; expiry不得提前 |
| 观察窗 | 无 | [observe_from,deadline]窗过滤; 禁止窗后未来数据; 同观测日去重 |
| 前提预测 | 文本描述 | 前提规格程序判定; 未兑现不启动观察; 至期未成立=终态,不顺延 |
| 触发器 | 单指标瞬时 | AND/OR复合+连续N周确认+断档重置+首次跨越标注 |
| 数据时效 | 无逐指标规则 | obs_date/as_of分离; 频率规则判龄; 过期不作当前证据 |

## 尚未解决的研究质量问题(交付⑥,如实)

1. 触发器数值本身(阈值/方向/持续周数)仍是人工配置,程序只验证"是否触发",不评估阈值合理性。
2. 证据星级衡量"证据充分性"而非"结论正确性"; 程序门禁不保证研究判断对,只保证变更可审计可复核。
3. 复合条件预测(多指标)到期仍标inconclusive留人工; 引擎自动裁决仅覆盖单指标规格。
4. 机制类别mechanism_of按指标名正则推断,新指标可能归错类(可用显式mechanism覆盖)。
5. GLM对非结构化输出的遵从性依赖prompt; 门禁是最后防线而非第一道。

---

# 第四轮: 研究可靠性修复(2026-10-12)

基线: main bc62a41(第三轮合并版)。本轮为修复,不扩产品范围: 无新券商接口/账户/交易执行/前端/多Agent。

## P0-1 连续观察周数(ISO周唯一标识)

`allocation_engine.evaluate_quant_triggers` v4: 观察周标识=ISO year-week元组(`_iso_week_key`/`_prev_iso_week`)。
- 同一ISO周无论运行多少次最多贡献1个观察周(允许修正本周观察,不增加consec);
- 仅当本次评估周恰为存储周的下一个ISO周时consec+1; 跳周(中间观察周缺失)或首次→重置为1;
- 条件明确不满足→清零; 无可核验数据→不推进不重置(数据缺失≠条件失效);
- 跨年正确(2026-W53→2027-W01为相邻周; 2026-12-28锚定法);
- persist=False完全无副作用(渲染路径); trigger_state={consec,last_week,last_eval}含v3状态迁移。

## P0-2 证据去重/方向/新增判定 + 评级门禁

- `split_evidence_direction`: 支持/反对/未解释三分; 反对证据不计入升级支持数量。
- `_base_metric`: 同一底层指标的不同字段口径(.value/.prev/.week_chg…)按基底去重 → 星级与新增判定都数"独立指标"。
- `new_supporting_metrics`: 与该观点证据台账(obs_pairs)比对, (指标,观测日)已记录不算新增; 新一期观测才算新信息; 当周台账重跑不当作历史。
- 评级变更门禁: 同向触发器已触发 或 ≥2项**新增独立**支持证据(MIN_EVIDENCE_FOR_RATING_CHANGE=2按new_support计); 否则保留原评级+提案留档。
- 论点与配置观点统一: 见P0-4。

## P0-3 频率/新鲜度/变化口径统一

- `data_validator`指标频率注册表: 月频(FED_FUNDS/CPI/CORE_PCE/UNEMPLOYMENT/NFP/CORE_CPI/AHE/WTI)45天、周频(ICSA)16天、macro其余日频7天、.close/.high等5天、china 7天、scorecard 10天、未知14天。
- `is_fresh_anchor(key, info, as_of)`: 缺失/非法/未来观测日→False(不默认新鲜); `metric_registry_info`输出指标级元数据(source/frequency/unit/observation_date/release_date如实为null/…), 不伪造发布日。
- `macro_collector.compute_series_changes`(纯函数): 变化按频率计算——日频week_chg(5~10自然日窗口取最近)、周频上一期、月频mom_chg(21~45天)+yoy_chg(330~400天)**不产伪week_chg**; 全部附`_from`起始观测日与formula。
- `detect_revisions`: 与上一采集日文件比对同观测日数值变化,记录{obs_date,prev_value,value,detected}; 无历史文件不伪造。
- `global_market_collector`采集当日盘中High/Low(供touch盘中口径)。

## P0-4 论点与配置观点统一证据验证

`report_generator.update_thesis_status(report_text, thesis_path, today_str, anchors)`重写:
- 论点证据与配置观点共用同一套程序验证(verify_evidence_items/split/star/new_support);
- **终态门禁**: →已失效/→已验证须该论点quant_triggers中invalidation/upgrade触发器被引擎核验已触发,或≥2项本周新增独立支持证据; 否则保留原状态+提案留档(proposals,21天去重);
- 每周对全部论点核验触发器(sustain连续周数在thesis.json累积,与views同构);
- 确信度上调≤程序星级; 下调自由; 整笔拒绝不静默改判;
- 每次变化记录last_change{date,from,to,via,evidence,note}; 论点evidence_ledger台账与views同构;
- 论点失效→提示检查关联论点/资产观点,但不自动改任何评级;
- history行带[from→to via]审计; 9论点及完整历史保留,新增quant_triggers结构化字段;
- `apply_status_updates`调度: 校验FAIL→thesis.json与allocation_views.json都不修改。
- prompt: THESIS_STATUS支持evidence[]并写明门禁; 历史数值须带原始观测日; 5★措辞修正(见P0-5); 研究链路补第8环"调整及失效条件"; pred规格增加pred_basis(close/high/low)。

## P0-5 证据星级逻辑修正

- 5★不要求必须存在反证(5项/3类机制/3观察期即可); 但存在未解释重大反证时封顶3★(MAX_STAR_UNEXPLAINED_COUNTER);
- explained=true不构成"充分解释"的充分条件——封顶只看"是否存在未解释反证";
- 支持证据/反对证据/未解决重大反证分别记录(台账三列); 星级表达证据充分性,不是预测概率。

## P0-6 每日预测观察 + 严格裁决

- `scripts/daily_prediction_observer.py`(新): 接入每日流水线(run_weekly第10步),幂等记录观察期内预测的当期数据(含metric/value/obs_date/retrieved_at/source),不调GLM; 锚点带兄弟.high/.low一并记录;
- record_observations: 新观测/更新观测产生变更消息(修订与补采可追溯),同批重跑零变更;
- 价格口径price_basis: close(收盘达到)/high(盘中最高触及)/low(盘中最低触及); **touch判miss须全窗口都有该口径数据**——只有收盘价不得证明盘中未触及→inconclusive;
- expiry按截止日附近(≤4天容差)最后一个有效观测判定,非交易日按最近收盘; 
- touch窗内任一观测按其口径满足即hit(可提前); 周中盘中触及+周五收盘回落不推翻hit;
- GLM不能凭含数字文本宣布命中: 引用数值须与观察窗内记录吻合,引擎已裁决的以引擎为准;
- 定性预测(无可计算规格)只能inconclusive研究性回顾,predictions_in_period单列qualitative不计入客观命中率;
- 观察窗外/未来数据一律拒绝。

## 测试(全部离线fixture; 真实GLM单独执行)

| 套件 | 覆盖 | 结果 |
|------|------|------|
| test_round4.py(新,82项) | 任务书第九节20项+跨年/非交易日截止+四周端到端(同一状态,正确+错误案例) | 82/82 |
| test_round3_p0 | 91/91 | 回归通过 |
| test_round3_adversarial | 24/24 | 回归通过 |
| test_p0/p1/p2/p4 | 22+36+82+42 | 回归通过 |
| test_e2e_four_weeks | 59/59 | 回归通过(论点路径补传锚点) |
| test_glm_live(真实API,单独执行) | 8/8 | GLM输出obs_date不合规→证据被程序拒收,门禁对真实模型输出有效 |

## 第四轮能力对照(交付④)

| 能力 | 第三轮 | 第四轮 |
|------|--------|--------|
| 连续观察周 | "两次运行≤10天就累计",同周重跑可刷满 | ISO周唯一标识,同周至多+1,跳周重置,跨年正确 |
| 证据独立数 | len(verified),同指标衍生值可凑数 | 按底层指标基底去重,只数独立指标 |
| 证据方向 | 不分支持/反对 | 三分; 反对证据不进支持数量 |
| 新增证据 | 不区分新旧 | 台账比对; 旧值重引不算新增 |
| 论点状态 | 模型输出直接回写 | 与配置观点同门禁(触发器/≥2新增),审计留档 |
| 新鲜度 | 统一7天 | 指标级频率规则; 月度CPI不受7天限制; 缺观测日不默认新鲜 |
| 变化口径 | 第6个观测值之差冒充周变化 | 按频率分口径,附窗口元数据; 修订检测 |
| 盘中触及 | 只看收盘 | close/high/low三口径; 缺盘中数据不判miss |
| 预测观察 | 周报时点 | 每日幂等记录 |
| 定性预测 | 可文本宣布hit | 只能研究性回顾,不计入命中率 |

## 第四轮遗留(交付⑤,如实)

1. 触发器阈值/持续周数与论点quant_triggers映射为人工配置(本轮按原文条件保守映射11条,相关性/评分卡类条件未锚点化,仍走文本+证据门禁);
2. 复合(多指标)预测到期仍inconclusive留人工;
3. FRED发布日(release_date)采集端不可得,注册表如实null;
4. 观察记录的数据源以锚点文件为单位,尚无逐指标来源交叉验证;
5. GLM结构化输出遵从性仍依赖prompt+程序门禁(实测GLM会输出"本期观测"类非日期obs_date,已被程序拒收)。

## 第四轮复审补充(同日,提交于af9f5fd之后)

对照任务书逐条复审发现3处残留,已修复并加测试(test_round4附加B1~B3,套件92项):
1. **中立证据(P0-2.2)**: verify_evidence_items接受neutral=true/stance=neutral,
   数值真实性照常验证但不计入支持数量; split_evidence_direction返回4元组
   (supporting/contrary/unexplained/neutral); 台账分别记录supporting与neutral数。
2. **采集日不得替代观测日(P0-3.5)**: 证据引用的obs_date必须与锚点观测日完全一致,
   原先"等于采集日as_of也可"的容差已删除(锚点缺观测日本就整体拒绝)。
3. **关键传导指标参与(P0-2.4)**: 证据路径的评级变更新增_key_engaged门禁——
   定义了key_metrics的资产(当前id3信用/id5贵金属),新增证据须至少触及一项关键
   传导指标,否则"只能证明宏观事实,不能充分支持该配置方向"→降为候选提案留档;
   未定义key_metrics的资产不适用(由星级门禁把关); 触发器路径不受影响
   (触发器本身即该资产既定传导条件的引擎核验)。

# 第五轮: 可靠性终验与正式运行验收(2026-10-12, dev/round5-reliability)

基线: 1a22af8(main)。原则: 不扩架构,只收纪律; 最小必要修改; JSON状态与周报八节格式兼容。

## P0-1 GLM裁决引用核验(allocation_engine.py)

原缺陷: `cited_ok = (not obs) or any(...)` — **空观察记录反而放行**GLM文字裁决。
重写为配对扫描: note中的数值与观测日必须与观察窗内**同一条**实际记录吻合
(仅数值对日期错→拒; 仅日期对数值错→拒; as_of采集日不算观测日)。
复审加严3处: ① hit引用的记录还须实际满足comparator(拿不满足的记录宣hit→拒);
② miss须window_coverage充分(GLM与引擎同口径); ③ expiry引用须落在有效截止交易日
前4天内(不得拿窗内早期值证明截止水平)。inconclusive裁决不要求引用。

## P0-2 市场日历与观察窗覆盖(新增日历注册表)

每项预测可确定: 观察起止/资产市场/预期有效观察日/已取得观测/缺失日期/覆盖是否充分
(window_coverage)。市场映射: BTC→crypto(7×24), china.*→cn(仅2026长假核心块保守),
.HK→hk(最小集), 其余→us(NYSE规则程序计算节假日,周末休市顺延观测)。
无法可靠确定日历时**保守视为交易日**(宁可inconclusive不假miss)。
- touch: 窗内一项有效触及即hit(单调证据,不看覆盖); 判miss须覆盖充分
  +对应口径数据完整(黄金high>4400仅3个交易日→inconclusive不判失败);
- expiry: settlement_date=截止日(含)**回溯**最近有效交易日,规则预定义不事后挑
  (周六10-31→10-30; crypto不回溯); 截止前4天无观测→inconclusive;
- 渲染层: 覆盖缺口的观察中预测标注⚠️提示"裁决将从严,不得假设未触及"。

## P0-3 证据obs_date必填(三项缺一不可)

metric+value+obs_date整项拒收制: 缺obs_date/不可解析/锚点无观测日/与锚点观测日
不符(采集日as_of不得替代)的证据不得参与评级/星级/状态变更,台账不写。
thesis.json与allocation_views.json共用verify_evidence_items同一套规则。
prompt侧同步: 证据规格明示"obs_date必填且须与锚点观测日完全一致"。

## P0-4 终态退出门禁(report_generator.update_thesis_status)

进入终态有门禁,退出终态同样有: 已失效→进行中/待观察须 (a)原失效条件经引擎复核
不再触发 **且** (b)≥2项新增独立证据; 已验证→重开须invalidation触发器已触发
或≥2项新增独立反证(new_contrary_metrics,与支持证据同一套基底/观测日身份)。
不满足→proposal留档并提示"实质新假设应创建关联新版本论点"; 审计完整
(from/to/via/evidence)。9论点及历史不删不改旧判断。

## P1-1 同日重跑不虚增新增证据

新增判定改为与台账已知(指标,观测日)集合比对(_seen_obs_pairs含同日早前条目,
_new_metrics_vs_seen): 完全相同对不算新增; 仅**更新观测日**算新一期; 修订(同观测日)
只记录不算新观察。台账append移到门禁判定**之后**(update_allocation_status与
update_thesis_status双侧)。_METRIC_FIELD_SUFFIXES补mom_pct/yoy_pct/week_pct
(派生百分比字段不构成独立证据)。

## P1-2 采集失败不更新预测观察(daily_prediction_observer.py重写)

observe()返回(changes,n,PASS/PARTIAL/FAIL): 锚点文件缺失或文件日≠今日→FAIL
("不得以旧数据充当本期观察"),CLI exit 2; 部分资产缺失→只跳过受影响预测→PARTIAL;
逐预测_metric_problem(缺metric/缺obs_date/未来/超频过期)跳过并留日志; 原子写+bak。
run_weekly流水线改(name,script,critical)三元组: 新闻/相关性为非关键(失败降级,
不阻止观察不挂退出码),其余关键(失败exit 1); run_pipeline抽出可测。

## P1-3 宏观变化单位语义(macro_collector.py)

SERIES_UNITS注册表(index/rate/count/price×单位标签)+_CHG_UNIT_BY_KIND:
指数点变化与百分比变化分离(CPI 300→303=mom_chg 3.0点 + 另列mom_pct 1.0%附公式);
利率/利差/失业率=百分点(不产百分比变化); 就业=人数; 每个chg字段附_from/_formula/
_unit,公式含起止观测日。

## 测试(第九节20项+验收模拟, test_round5.py 64项)

20项任务书用例全部落盘断言(非仅返回值),含正例/反例: R1~R3b裁决引用、R4~R8
覆盖/日历/截止、R9~R10证据日期、R11~R12终态门禁(含3组正反例)、R13同日10次
(含阶梯攻击)、R14~R15旧值/修订、R16~R17采集失败(含CLI exit 2与关键/非关键分流)、
R18单位、R19双侧共用规则、R20 FAIL不落盘; 加第十节正式运行验收模拟
(单沙盒连续状态: 每日观察5天→幂等→采集失败隔离→周五PASS周报→GLM虚构hit被拒
→时间一致→FAIL不污染)。

全部套件(2026-10-12): p0=22 p1=36 p2=82 p4=42 round3_p0=91 adversarial=24
round4=94 round5=64 e2e=59,合计514断言0失败; 真实GLM冒烟8/0(RUN_GLM_LIVE=1,
临时副本,真实观点库未动; GLM实测已按新规格附obs_date)。

## 第五轮遗留(如实)

1. 中国日历仅2026年长假块,2027+回退为"周末以外均交易日"(保守方向: 多预期→
   覆盖判定更严,不产生假miss);
2. 港币日历为最小集{元旦,圣诞};
3. launchd每日07:00真实调度与本轮改动兼容性经代码路径验证(观察器CLI退出码
   语义新增exit 2),真实定时任务行为标注"未验证";
4. GLM在长prompt下偶发省略obs_date——程序门禁拒收兜底,依赖prompt纪律+程序核验双保险。

---

# 第六轮: 最终可靠性补丁与正式版冻结(2026-10-12, dev/round6-final)

主题=正式版冻结前最后一轮,只修可靠性缺陷、不加任何新功能。三个P0全部在
d798286基线独立复现后修复,旧用例按新口径更新(不降低验证标准):

## P0-1 观察跳过后仍写入数据(验证与写入未隔离)
- 缺陷: 观察器`observe()`对problem预测只打日志,`record_observations(data, anchors,
  today)`仍收到未过滤锚点→无效数据可进入长期观察历史;只查目标指标不查前提指标;
  引擎侧`obs_date or today_iso`缺观测日时用采集日冒充。
- 修复(`daily_prediction_observer.py`+`allocation_engine.py`):
  - 观察器: 观察中预测查目标指标、未触发预测查前提指标(分别校验,一个有效不得
    放行另一个);problem指标从`valid_anchors`剔除后才交给record_observations;
  - 引擎防御(双侧防线): `_anchor_obs_date_valid`统一校验(缺失/不可解析/未来→拒),
    目标与前提锚点均须过新鲜度窗;不再以today补盖观测日;
  - 跳过说明只打印不进changes(保持幂等信号干净)。

## P0-2 条件预测到期后重新激活(无终态封存)
- 缺陷: record_observations前提分支无截止日检查→截止日后前提兑现仍把
  not_yet_triggered翻成observing;无持久终态标记,GLM可跨周翻案已裁决预测。
- 修复: `_is_final_prediction`(final标记/hit-miss-inconclusive三态/旧记录
  not_yet_triggered+resolved_date+截止已过);`_migrate_views`向后兼容补final
  (旧hit/miss/inconclusive,只加字段不改内容);前提激活须od≤deadline(否则打印
  "截止日不顺延"不激活);引擎裁决落地(含到期未触发终态)与GLM合法裁决均写
  final=True;GLM块对final预测整体跳过(不得改判也不得重复注记刷新审计日期)。

## P0-3 Expiry用截止日前旧数据裁决(±4天容差)
- 缺陷: `_EXPIRY_OBS_TOLERANCE_DAYS=4`让结算日缺数据的案例回退用前一日价格;
  GLM引用核验同容差→Python判inconclusive时GLM可拿前一日满足值裁成hit。
- 修复: 删除容差常量与全部引用;expiry裁决只认`settlement_date`(预定义,非交易日
  回溯,crypto自然日)**当日**观测,缺失→inconclusive并明示"不得以前一交易日价格
  代替";GLM引用须`cited[1]==settle`(与引擎同一结算口径)。

## 旧用例更新(新口径,非放松)
- test_round3_p0 E9: 补10-16结算日观测4350→7600序列改造(断言仍查hit+窗后不算);
- test_round4 #15: pred_out/pred_fut补10-09结算日观测,断言按当日值判;
- test_round5 R7: 标签措辞更新(断言子串本就兼容)。

## 测试与验收
- 新增tests/test_round6.py(48断言): 任务书20项用例+对抗X1-X5(crypto自然日结算/
  GLM终态翻案被拒/绕过观察器直调引擎防御/未触发终态跨周封存/连续状态端到端:
  前提触发→观察→采集失败隔离→到期裁决→final封存→重跑不变);
- 10套离线562断言全过(514基线+48新增);真实GLM冒烟8/8(临时副本);
- 正式版标记v1.0.0-rc,核心架构冻结。

## 第六轮遗留(如实)
1. launchd真实定时任务长期行为未连续观察(代码路径已验证);
2. 窗内前提触发但数据迟到多日才发现的边缘情形: 终态化后不再重开(保守取舍,
   审计以周报裁决为准);
3. 触发器阈值/复合预测裁决边界同第四轮记录,属后续真实运行驱动项,不新增开发。
