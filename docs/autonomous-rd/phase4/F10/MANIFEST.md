# F10 独立研究席 MANIFEST(Audit-R1 受测席)

- 席位: f10-research-seat(独立 Agent 研究席, 零操作者提示, 方法全自选留痕)
- 产品仓: ~/investment-agent-product @ dev/audit-fix-r1, 冻结候选 SHA 1656294ddcdc0ab1128feac2e3b9e44c5ba54273(席位亲验)
- 引擎树: ~/investment-agent-dev(只读, 未改任何文件)
- 执行日: 2026-11-16
- 研究问题: 逐字见 question_prereg.json(验收席预注册, 本席收到即原文执行)

## 链路结果表(三段式单入口 ia_cli.py research-one)

| 段 | 命令要点 | 结果 |
|---|---|---|
| plan | --stage plan --question '<问题逐字>' --out-dir /tmp/phase4_F10 --engine-root ~/investment-agent-dev | run_ok=true; run 目录 20261116T114933Z_布伦特原油价格…; 快照 research_snapshot_20261112_v2(target 20261112); gate_a=DEGRADED(5/5 信封步非 OK, 降级不阻断); 证据索引 64 行; L1 事实 1 行(BEI_10Y 2.2@2026-11-10); L2 n=17 全库 INSUFFICIENT_EVIDENCE(库龄函数, 首验窗 2026-12); L3/L4 produced=false(待本席) |
| attach | --stage attach --report-dir <run> --judgment docs/autonomous-rd/phase4/F10/judgment_mvp.json | attached=true; validation_passed=true; violations=[](纪律校验+契约门双绿, 一次过门, 无降阈值无删数字) |
| report | --stage report --report-dir <run> | generated=true; machine_verified=true; L3_produced=true; L4_produced=true; 四态门 review 态= required:true / seat_invoked:false / verdict:null(独立审查席尚未裁决, 诚实状态不阻断交件); deliverable=false / mvp_complete=false 系 review 缺席所致, 如实呈现 |

步骤台账要点: S1-S4 OK; S5_compare 如实 SKIP(命中指标不足 2, 本席对齐改自选内连接并在计算档留痕); S6_analog OK; S8_grounded_qa 引擎面 unmapped(该问题不在确定性 QA 支持类型内, 语义✗如实落档)——判断层由本席补作即本档 L3/L4。

## 判断面概要(核心结论)

问题三选一(减弱/锚定/时有时无)按证据的回答: **均不单独成立——传导呈「频率增强+幅度钝化」的结构转型, 方向传导在增强、幅度传导在上行侧大幅钝化, 且涨跌不对称(下行传导约三倍于上行)**。

- 频率维度: 分年日度相关 2016 +0.11 → 2026 +0.54(全窗最高年); 60 日滚动相关负窗仅 2.1%、|r|<0.1 合计 5.3%、r≥0.3 占 59.9%, 方向稳定为正——「时有时无」不成立于方向, 成立于强度(0~0.82 宽幅摆动)。
- 幅度维度: 大涨月(月涨≥8%)每 10% 油价的 BEI 月响应, 2016-2021 窗 +0.0846pp → 2022-2026 窗 +0.0235pp(降幅约七成); 2026-03 布伦特单月 +63.3% 而 BEI 仅 +0.050pp。
- 不对称: |单日|≥6% 事件同日响应: 上涨组 +0.0209pp vs 下跌组 -0.0400pp(下行约两倍); 2022+ 大跌月每 10% 响应 +0.0746pp vs 大涨月 +0.0235pp(约三倍)。「油价暴跌、预期纹丝不动」的直觉在平均意义上不成立(个别近零/反向月确在, 如 2021-11/2024-09), 直觉体感来自个例选择。
- 锚定检验: BEI_10Y 60 日滚动 std 无压缩(2019 前 0.0476pp / 2024 起 0.0569pp / 2026 年 0.0521pp)——锚定不体现为波动消失, 而体现为对油价冲击的幅度响应被压缩; 期限结构自洽: BEI_5Y 分年相关每年更高(2026 +0.63), 短端更敏感、十端更钝化。
- 机制(E2, 假设): 政策反应函数中介——机构侧证词 MSIM(VP-VIEW-20261111-006, institution_stated): 10Y 实际收益率单月 +49bp 而盈亏平衡仅 +5bp 且发生在布伦特触及 106 美元/桶的月份, 重定价由实际利率承担。机构分歧如实并列: MSIM(实际利率主导但仍维持盈亏平衡敞口对冲通胀更久)vs UBS(VP-VIEW-20261111-004, 预计 2026-12/2027-03 各加息 25bp)。
- 证伪条件(节选, 全文见 judgment_mvp.json): ①任一自然月 BEI_10Y 上行≥0.25pp 且 BRENT_F 单月涨≥8% → 幅度钝化证伪; ②BEI_10Y 从未收于 2.50 上方(年内上沿, 前提 BRENT_F 曾站上 118.35)→ 传导重开未兑现; ③BEI_10Y 始终收于 2.18 上方(前提 BRENT_F 曾跌破 59.96)→ 脱锚未兑现。期限均 2027-06-30, 两态口径(前提缺席=未触发不计证伪)。

## 本席自选方法清单(全留痕于 f10_calc.py, 纯 stdlib 零模型零网络)

M1 对齐(共同交易日内连接+连续日变化对, n=2494) / M2 全窗 pearson+OLS 斜率 / M3 分年相关与斜率 / M4 60 日滚动相关(占比/范围/逐月末) / M5 事件研究(|单日|≥4%、≥6% 两档, 涨跌分组, 同日+前向 5/10/20 日) / M6 月度聚合(±8% 大月分组, 前后段窗对比, 每 10% 油价响应) / M7 BEI 60 日滚动 std 分段(锚定波动检验) / M8 稳健性(WTI_F 代 BRENT_F、BEI_5Y 代 BEI_10Y 分年旁证) / M9 2026 锚点(年内区间/钉死百分位 100×count(v<cur)/n)。

## 诚实边界(如实, 禁编造清单)

- BRENT_F=主力连续期货, 引擎 identity 注记「含展期跳空可能」; BEI_10Y=名义-实际利差, 含通胀风险溢价与 TIPS 流动性溢价, 非纯预期; 引擎无流动性调整分解序列, 该分解不可做。
- 相关与 OLS 斜率均为统计描述, 相关≠因果(纪律 7); 按统计期对齐, 不代表当时市场信息集(纪律 5); 无发布日事件面, 事件研究不作「当时市场反应」声明。
- 窗口约十年(2016-11 至 2026-11), 分年样本 215-251 个变化对; 60 日滚动窗长为方法自选, 窗敏感性未做全谱检验, 以分年口径(换分组)方向不变旁证, 已在 judgment CON-3-3 如实披露。
- L2 全库 INSUFFICIENT_EVIDENCE(首验窗 2026-12), 机构观点一律归因转述(institution_stated), 不作可验证预测背书; 机构数字(49bp/5bp/106 美元等)为机构原文转述, 不与引擎面绑定。
- S5_compare 引擎面如实跳过, 本席对齐口径为自选, 与引擎 compare 产物的口径差异由此说明。
- E3 环为纯叙事并给证伪指标, 不作预测; 三情景并列(基准+反例+反例二)。

## 工件清单(均在 ~/investment-agent-product/docs/autonomous-rd/phase4/F10/)

- judgment_mvp.json — 判定档 schema v1.1(sha256 前 16 位 9d8fd3292750a6dd)
- f10_calc.py — 本席复算脚本(方法 M1-M9 全留痕, 只读引擎树)
- f10_calc_output.json — 复算全量输出
- FULL_REPORT.md / report.md — 链路 report 段产物(attach 后重渲, 自 run 目录拷贝)
- evidence_pack_agent_judgment.json — attach 落位后的判定档副本(自 run 目录拷贝)
- question_prereg.json — 验收席(f10-acceptor-seat)预注册问题档(非本席产物, 只读未动)
- run 目录原件: /tmp/phase4_F10/20261116T114933Z_布伦特原油价格的大幅波动_还会传导到美国长期通胀预期_10年期盈亏平衡通胀率_B/
