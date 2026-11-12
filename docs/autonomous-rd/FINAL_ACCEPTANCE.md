# FINAL_ACCEPTANCE — 最终验收结果

> 依据 `PRODUCT_GOAL.md` §八 AC1–AC10。状态只允许 PASS / PARTIAL / FAIL / NOT_VERIFIED。
> 历史文档的 PASS 不作数——本档只登记**独立审计复核后**的结论(复核日期+证据指针)。
> 整体判定: 全部 AC = PASS 方可宣布最终目标达成;任一 FAIL / NOT_VERIFIED = 未完成。

## 验收矩阵(2026-11-11 R1 审计初始化,逐项复核后更新)

| # | 验收项 | 状态 | 证据 / 差距 | 复核记录 |
|---|---|---|---|---|
| AC1 | 真实全球宏观全景 | NOT_VERIFIED | R1 审计中 | — |
| AC2 | 真实机构研究 | NOT_VERIFIED | R1 审计中 | — |
| AC3 | 正确的机构观点验证 | PARTIAL | R1 三型证据落库: VP v1.1 阶段A/B 结构化(`scripts/view_plausibility.py --build-all`,本地 17 份重建)。A面 5/17 有真判定(4 PARTIALLY_SUPPORTED+1 MIXED),B面 5/17 MIXED(发布后数据走向与假设相反);C(到期预测实判)全库未到期=不可判(首验窗 2026-12)。差距: 阶段A vintage 仍 DEGRADED 近似锚(采集档无历史 vintage,已如实标注)+C 面零实判 | R1 自测 50 判定(含 R1.1 修复回归);独立审计已收口: 6 维全 PASS/无 BLOCKER,交付物 17/17 清洁+31 数值复算全中;2 MAJOR 已修(R1.1),对照实验零语义差异 |
| AC4 | 经济机制与历史研究 | NOT_VERIFIED | R1 审计中 | — |
| AC5 | 独立研究结论 | NOT_VERIFIED | R1 审计中 | — |
| AC6 | 真正的一键研究 | PARTIAL | R2: `ia_cli research-run` 十一步确定性编排真执行(每步真子进程+信封留档/ok 与 semantic 分记/L3+L4 恒 declared-not-produced/逐数证据索引/零映射如实 unmapped);单问直跑已验(31 判);**R3 十问扇出** --fanout 十问清单逐条真跑(47 判定+全套 129/129 绿) | 剩余: AC7 端到端 3 任务+1 开放题未跑;真实案例积累 |
| AC7 | 真实端到端验收(3 任务+1 开放题) | EXECUTED | R7(2026-11-12, dev/rd-r7-ac7-e2e): 数据面修复(HSI/HSCEI core 缺席→腾讯 2000 根重采+PPI 真实复拉; 快照 research_snapshot_20261112_v2, Gate A=DEGRADED core 0 缺)后真跑——任务A 13 节全景(research-run 十一步+--fanout 16 命令; 13/13 节无空置)+任务B 17 档/15 机构分歧矩阵+M 表八问+新鲜 CPI/PPI 更新评注+任务C view_verifier A/B/C×17 档+VP sidecar 重建(B 面 23 机械判定=11 against/5 supports/7 neutral; C 层全未到期如实)+开放题金油比条件前视(现场生成非反刍); 四 QB 归档=QB-20261112-001~004(全绑 v2 快照) | 终判留 AC 覆盘轮(R8=独立验证轮他席复算);非自动 PASS |
| AC8 | 研究可复核 | NOT_VERIFIED | R1 审计确认交付物可复算(逐字节重建一致+31 数值独立复算中);R2 每步信封留档已落;端到端研究复核(AC7 式)未跑 | — |
| AC9 | 真实用户可用(干净安装全链) | EXECUTED | R12(2026-11-12, dev/rd-r12-ac9-clean): **①--force 坑修复**——根因=local_modifications 只比对当前源树,git 拉新后未动过的旧装机面被误判"用户修改";修复=matches_source_history(git blob 逐字节比对近 64 提交,装机面与任一历史版本一致⇒幂等刷新带 stale_version_refreshed 旗,真修改仍拒/备份,非 git 部署保持旧语义),套件 16/0+回归 32/0;**②干净环境全链**(/tmp/r12-clean 全新 clone): 安装零旗标 ok→配置(.env 三 key 只读注入零回显/venv 依赖/零 Key 面=doctor ok+research 诚实拒答 no_snapshot)→更新(首轮 10/15 Gate A 拒=港股双通道环境面[腾讯 WAF 拦 10y 深窗+yfinance 直连 IP 429],与 LIVE 同日同败逐字一致;补 HTTPS_PROXY 恢复"境外源走代理"设计姿态+--allow-revision 同日修订→**15/15 exit 0**,快照 v2 DEGRADED core 0 缺,HSI/HSCEI 真值入档)→一键研究两问(自然语言面 11 步诚实跳过有注记/指标面 **14 命令全 executed**)→地图十问(空面如实注"干净 clone")→追溯 3/3 数值命中源档+sha256 链→归档 **QB-20261112-001**(绑 v2,record/full 回读逐字一致);证据档 /tmp/r12-clean/evidence_log.md;**③用户文档面发现: shell 启动管线须带 HTTPS_PROXY(系统代理不自动进 shell env)——登记待补 USER_GUIDE** | 终判留 AC 覆盘轮(不自动 PASS);--force 坑登记面=本行+SKILL_GUIDE(均已收口;OPEN_ISSUES 原本无此条目,如实在 R12 报告注记) |
| AC10 | 可靠性与安全 | EXECUTED | R1 审计红线核查过(无前视/不造数/不越付费墙/密钥不入库);R2 归档默认关+信任边界=resolve_inputs 规范核验(符号链接逃逸被拒=验证有效);**R14 红线终审(2026-11-12, dev/rd-r14-ac10-redline)**: 五面全 PASS 零违规——厂商词(守卫 5/5✅+72 文件残余全为豁免类)/个人路径(3 命中全为负向守卫与审计引用)/密钥(0 真泄漏,sk- 全 FAKE 明标)/档案真实性(97+97+1 全字段完整零合成冒充)/源披露(110 指标全 source+source_symbol,11 快照逐 fact 注册+带源)+九红线映射(含交易执行面 0 命中、端点全免费公共源);报告=R14_AC10_AUDIT.md | 终判=PASS 候选,留用户裁定席(矩阵纪律) |

## 验收标准来源与交叉映射(2026-11-11)

两份用户指令各带一套 AC,编号不同、内容同源,矩阵以上表 `PRODUCT_GOAL.md` §八 AC1–AC10 为准:

| `RUN_MANDATE.md`(启动指令 §十一) | 本矩阵 | 说明 |
|---|---|---|
| AC1–AC6 | AC1–AC6 | 同名同义 |
| AC7 研究地图 | (并入 AC1/AC7 上表现状) | 页④ research-map 为其雏形,验收仍以 AC7 开放题为硬门 |
| AC8 三案例 + AC9 开放题 | AC7 | 三任务+一开放题合并验收 |
| AC10 干净环境全链 | AC9 | 装机/配置/更新/研究/展示/归档 |
| AC11 可追溯可复核 | AC8 | — |
| AC12 模型无关/合规/无未授权付费 | AC10 | — |

## 最终交付清单(§十一,达成后逐项勾验)

- [ ] 可运行完整产品
- [ ] 一键全球宏观研究地图
- [ ] 机构观点与证据验证系统
- [ ] 完整真实宏观研究报告
- [ ] 原始资料与可复核证据索引
- [ ] 工程测试与金融正确性测试
- [ ] 独立审计报告
- [ ] 所有关键能力最终验收矩阵(本档)
- [ ] Git 开发分支与提交记录
- [ ] 用户安装、使用与更新说明
