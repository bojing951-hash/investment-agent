# CAPABILITY_MATRIX — 最终能力 × 当前差距

> 「最终能力」列以 `PRODUCT_GOAL.md`(总指令)为锚——**总指令落位后逐条对齐修订**。
> 在此之前按产品章程(仓库根 `PRODUCT-GOAL.md`,2026-11-08)与已发布能力登记。

| 能力域 | 最终能力(待总指令校准) | 当前 | 差距/证据 |
|---|---|---|---|
| 数据收集整理 | 多源宏观数据自动采集+事实引擎 | 81 指标;FRED/Tushare/Finnhub/Yahoo/BBK/ECB/Shiller 已接线;Gate A/B 数字门禁 | 缺口台账 18 项;000300/000905/000852 取回未入注册表 |
| 整体认识 | 宏观研究周报全景 | 周报(现状/变化/驱动)已上线 | LIVE 面落后 dev 面(v0.7.1 vs v0.9) |
| 传导机制 | 变量→资产传导研究 | 相关性矩阵/阈值/分资产;C8 传导边挂 QB 号;页2 可探索网络 | 真实使用反馈缺(Web 实际使用层) |
| 历史比较 | 深度历史对照 | C6 analog 六维类比引擎(z 防泄漏/巧合旗标/诚实拒答)+Shiller 145 年+FRED 深回溯 | 序列深度随采集累积;60 日窗样本不足项 |
| 机构观点 | 机构怎么看/为什么 | C8→C9 观点库 17 份/15 机构 schema v1.1+attribution 硬拦截(2026-11-11 实数);**R22: C 层机器防线**——方向语义(FX 报价对/国债价格-收益率)/到期新鲜度门/标签-证据绑定校验(validate_vp+binding_check+CLI --verify-binding)/vintage obs≤publish 二次过滤 | C(到期预测实判)全库未到期=不可判,首验窗 2026-12(机器防线已落地,真实已到期样本首验留日历门) |
| 来源验证 | 证据可核验 | C9 source_verifier 四状态+audit/入库消毒;R1 三型证据落库: VP v1.1 阶段A/B 结构化+stage_labels(`view_plausibility.py --build-all`,C 契约零变动) | 阶段A vintage=DEGRADED 近似锚(采集档无历史 vintage,如实标注);A面 12/17 仍 INSUFFICIENT(映射缺口 16 指标缺席快照);CODEX 外部核验通道 NOT_VERIFIED |
| 个人研究工具 | 特定问题深研/验证假设/形成观点 | C9 research-map 十问扇出+三型验证 A/B/C+命令清单(R1 修复: 14 条实解析);**R2: 一键研究真执行**——`ia_cli research-run` 十一步确定性编排(每步真子进程+信封留档,ok/semantic_ok 分记,L3/L4 恒 declared-not-produced,逐数证据索引,零映射=如实 unmapped);**R3: 十问扇出**——`--fanout` 十问命令清单逐条真跑(16 命令+信封留档,Agent 层问 declared-not-produced,占位符替身披露) |L3/L4 恒不产出=诚实面;AC7 端到端 3 任务+1 开放题未跑;真实案例待积累;Web 使用层未满 |
| 独立结论输出 | 证据支撑的条件推演 | 13 节报告模板+条件推演五行+四层区分(客观事实/机构观点/AI 推断/历史统计/条件情景) | 同上,真实研究案例待积累 |
| 自主研发循环 | 审计→优先级→开发→测试→独立验证→状态更新 | 本目录建立(2026-11-11)+R1 轮(AC3→PARTIAL)+独立审计收口(6 维 PASS/无 BLOCKER,2 MAJOR 已修 R1.1)+R2 轮(AC6→PARTIAL);hooks 自主机制(PreCompact/SessionStart);**R20**: 状态管理机器化——任务台账(唯一ID/状态/Git证据)+五项一致性检查门(scripts/rd_state_consistency.py,入 CI 硬门)+检查点管线(rd_checkpoint.py,收口唯一通道)+无上下文恢复验收测试(治 R15→R19 失同步根因=手写状态档);研究能力面本波无变化(§七如实:本波=系统能力) | 持续执行机制真实性待阶段二实查(hooks/launchd 真配置真日志);无头跨会话自动拉起待验(卡点④) |
