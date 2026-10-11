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
