# P2 深研能力交付说明(DELIVERY)

> 包: R020 · IA-P2-DESIGN(P2 设计线第1包,docs-only 零代码)
> 合同: IA-P2-DESIGN-AC-v1.0(2026-11-02 冻结;BASE-P2=`f1fe593faa0f1754e6a6ab14c39f39fc0848550a`;CI 套件基准=53)
> 分支: `dev/p2-design`(自 BASE 切出;线性提交;推送 origin)
> 交付时点: 2026-11-02(UTC)
> **会话恢复声明**: T1+T2(INVENTORY+DESIGN)由本包先前执行会话完成并提交(`d2d4a59`);本会话为同轮续作(T3+自检+本地CI+证据包+提交推送),reflog 佐证同一分支同一基线,非跨包混入。

---

## ① 交付清单

| 文件 | 角色 | 状态 |
|---|---|---|
| `docs/P2_INVENTORY.md` | 五面盘点(事实层,182 行 [实取·`wc -l`,2026-11-02]) | 新增,commit `d2d4a59fabe742bafa500b2cda3042acd5ab359a` |
| `docs/P2_DESIGN.md` | 架构设计八节(判断层,232 行 [实取·`wc -l`,2026-11-02]) | 新增,同上 commit |
| `docs/P2_DELIVERY.md` | 本文档(叙述层) | 新增,第 2 提交;尖端全SHA以推送后 `ls-remote`/证据包 `02-git-forensics/`/自述报告取证为准(本文档无法先于自身提交预知) |

提交结构: 3 个线性提交,父链 = BASE `f1fe593…` → `d2d4a59…`(T1+T2)→ 本提交(T3 v1)→(zip sha256 补登行,第 3 提交)。零修改零删除既有文件;零代码/测试/工作流/配置改动。

## ② 内容摘要

- **INVENTORY 五面**(AC-01): (a)研究基础设施五项载体齐备=研究快照/`Gate A`/装配/`Gate B`/论点·观点·预测状态保护,另追加 a.6 GLM 调用链能力级登记,逐项 `文件:行号`;(b)E2E-B 三件实读定位(184/253/52 行)+E2E-A 以注入摘要引用且三模块名零在场实测复核;(c)registry 81 指标双通道实测+USDJPY 260 观测(节点键 `JPY=X`,registry 身份 `USDJPY` L445/L448)+P1 跨支登记(`dev/p1-design@049ec978…` 全SHA,另支);(d)GLM 支 ls-remote 实况 `dev/p03-w2-glm-design@0c8de3c3…`(恰 3 文件+448 行 git show --stat 复演)标注**在途,不作冻结事实**;(e)外部约束登记(dateutil 漂移先例/预授权③ 免费源边界/凭证纪律/CI 基准 53)。缺口 P2-G-01~08(8 项 [实取·缺口表清点]);跨支登记 4 条(全SHA,交付时 ls-remote 复核一致)。
- **DESIGN 八节**(AC-02): §一范围(P2=多轮竞争性假设深化;P3 排除;禁交易/仓位/收益承诺)/§二任务模型(3 类发起=模式A异常升级+模式B用户指定+跟踪触发;生命周期状态机;P0-3 档案衔接;DP-1~6 四要素,GLM·费用类 DP-4/DP-5 标「确认权留用户」)/§三数据契约(5 类三态+快照纪律禁直读)/§四假设论证(≥2 竞争假设+证据矩阵+反方证据强制+多轮推进与终止)/§五 GLM 能力级接口(全程标「待 R019 定稿,实现包阶段对齐」)/§六可反驳性(falsifiable_conditions 字段级推导+Gate B 对接+append-only+结论状态机含证伪后处置 3 条)/§七实现包 WP-P2-A..D(4 包四要素+P0-3 落地前置声明+登记型参数先登记后运行禁回改入验收要点)/§八红线六条。
- **数值纪律**(AC-03): 双文档全文扫描,计数类/统计类数值 61 项逐值二选一标注(`[实取]` 复演全部一致/`[示意]` 合规);扫描方法+D 裁决+逐值映射成件(证据包成员④⑥);疑似失实=0。

## ③ 证据指针(证据包 `/tmp/p2-design-evidence/IA-P2-DESIGN-EVIDENCE.zip`,八类成员)

- **本地 CI 实测(AC-06(a)主证据,CI 同构情形a)**: 全新 clone(无 `data/` 等 ignored 目录=CI checkout 同构;HEAD=`d2d4a59`)按 offline-tests 工作流逐字同构逐套件运行: **53/53 全部 exit=0,OVERALL_FAIL_FLAG=0**;逐套件记录=成员③ `local-suites/cisim-tip/suite-summary.txt`+`logs/`(53 份)。套件数实测 = 登记值 53 ✓(情形a)。**作用域延伸声明**: 实测时点=第 1 提交尖端 `d2d4a59`;最终尖端与本实测点之 diff 仅 `docs/P2_DELIVERY.md`(name-status 取证在案),零代码零测试面变更,测试面结论按同一性延伸至最终尖端(沿 R014/R016「零测试面 diff 有效性延伸」先例)。
- **工作区运行(环境差异如实记录)**: 本机工作区含授权数据副本 `data/daily/`(gitignored)时 `test_p4_fixes` exit=1(39 通过/4 失败 [实取·套件日志 tail,2026-11-02],数据副本在场→套件走真实数据路径,202609 月度序列为 0)——CI 同构 clone 中同套件 exit=0,判定为本地数据在场的环境差异,非代码回归(与 E2E-B 轮同签名);其余 52 套件 exit=0;记录=成员③ `local-suites/workspace/`。
- **git 取证**(成员②): 上下文(UTC 时刻/解释器版本)/开工 status/分支表/reflog/log/name-status(BASE..HEAD)/rev-parse 父链/推送前后 ls-remote/推送输出。
- **LIVE/凭证取证**: LIVE 目录标记 grep(`R020|P2-DESIGN|IA-P2-DESIGN`)**零命中**(AC-05(d));三文档凭证模式 grep 零命中(AC-07(d));launchd 零触碰。
- **八类成员**: ①三件交付物双源副本(git show 装配时尖端版+工作树版,交叉哈希)②git 取证③本地 CI 逐套件记录(克隆+工作区)④全文扫描清单⑤引用清单⑥数值标注清单⑦自述报告副本⑧SHA256SUMS(逐成员)。
- **zip 整体 sha256**: 依合同 AC-06(b)⑧「不塞入 zip 自身」,字面值以**本文件末尾补登行(第 3 提交)**与 stdout 终版自述为准——zip 含自身哈希在数学上不可行,装配时尖端=第 2 提交,补登行提交后最终尖端以推送后 `ls-remote` 取证为准。装配时 zip 内 `P2_DELIVERY.md` 副本=v1(补登前),与第 3 提交版差异仅补登行,如实登记。

## ④ 偏离与如实声明

1. **会话恢复**: 本包分两个执行会话完成(先前会话 T1+T2 已提交 `d2d4a59` 后中断;本会话续作 T3 及以后)。分支/基线/父链未变(reflog 取证在案);本轮内零 PREEMPT-STOP 触发(R007 排程 2026-11-03 00:07 HKT,晚于本包推送)。
2. **本地解释器版本**: 本机 python3=3.9.6(CI=3.11;本机另有 3.11 但需额外授权未动用)。CI 同构运行以 3.9.6 完成 53/53 全绿;版本差异如实登记,最终以操作者 CI dispatch(3.11)为准。
3. **工作区数据副本影响**: 如③所述 `test_p4_fixes` 工作区 exit=1(授权数据副本在场)。未删除/移动任何本地数据文件;以 clone 取得 CI 同构结果,如实呈报。
4. **DELIVERY 双提交机制**: 因「zip sha256 落 DELIVERY」与「DELIVERY 副本入 zip」自指,采用 v1(入 zip)→装配→v2 补登字面值(第 3 提交)机制,差异仅一行补登,非内容改写。
5. **CI dispatch(AC-06(e))**: 属操作者 CHECKPOINT 段(登记件 `rounds/020/P2-DESIGN-CI-dispatch-evidence.md` 落字面值),执行 Agent 零 dispatch、零 `gh` 调用。
6. **网络与隔离**: 本包网络操作仅 git push/ls-remote/fetch(跨支只读);零 GLM 调用、零凭证触碰、零付费;LIVE 与 launchd 零触碰(取证在③);引擎目录零读写(不可达性声明+自述确认)。

## ⑤ 合同逐条自检(执行方自评;独立验收权属 Agent 4)

| AC | 自评 | 一句证据指引 |
|---|---|---|
| AC-01 五面盘点 | PASS | INVENTORY 面(a)~(e) 逐项 `文件:行号`;行号经 verify.py 复演偏差 0(证据包④附件/⑥);81 双通道实测;GLM 支在途如实标注 |
| AC-02 八节完备 | PASS | DESIGN §一~§八逐节强制要素齐备(3 发起/5 类三态/矩阵+反证+多轮/能力级 GLM/状态机/4 包四要素/红线);零交易仓位收益设计;P3 排除 |
| AC-03 数值标注 | PASS | 61 项逐值二选一标注,`[实取]` 复演全一致,模糊词零,疑似失实零;方法+清单成件(成员④⑥) |
| AC-04 引用真实性 | PASS | 引用清单(成员⑤)逐条可寻偏差 0;跨支 4 条全SHA 交付时 ls-remote 实取;注入摘要逐处标注;零引擎//tmp 依赖 |
| AC-05 范围分支隔离 | PASS | name-status = 恰 3×A(取证②);首提交父=BASE;单分支;LIVE grep 零命中;launchd/引擎零触碰 |
| AC-06 本地CI+证据包 | PASS | 53/53 exit=0 情形a=登记值(成员③);八类成员齐备(成员①-⑧);DELIVERY 登记交付事实;dispatch 属操作者 |
| AC-07 边界与 DP | PASS | 零调用/零凭证/零付费;DP-1~6 四要素齐备,DP-4/DP-5「确认权留用户」;登记型 DP 禁回改入验收要点;仓库零新增凭证(取证③) |

---

*证据与自述: `/tmp/p2-design-evidence/`(zip+staging)+ 本轮 stdout 自述报告(四段,存 result.md)。设计未冻结任何 AC;WP-P2-A..D 验收要点为草案,正式 AC 由主 Agent 后续轮拟定。*
