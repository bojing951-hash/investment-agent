# IA-P1-DESIGN-COMP 交付说明(DELIVERY)

> 包: IA-P1-DESIGN-COMP(P1 收口链设计补全轮=#19+#20 规格定稿·docs-only,R064)
> 合同: IA-P1-DESIGN-COMP-AC-v1.0(FROZEN 2026-11-06 20:3x HKT,操作者代批)
> 分支: `dev/p1-design-comp` | 基线 BASE-COMP=`64ce40c25409bdb0a3d9fecc4c5f0f5df74dd902`
> 编制: 2026-11-06(UTC) | 正式自述=result.md(stdout 四段,随驱动归档;zip 内自述副本=装配时点版,终局以 stdout 为准)
> 数值标注纪律: 逐值 `[实取·来源]` 或 `[示意·非实取]`;日期/SHA/结构编号/档键成分出圈(REPORT 头部边界声明同款适用)。

## ① 改动清单

| 项 | 值 |
|---|---|
| 分支 | `dev/p1-design-comp`(自 BASE-COMP 切出,纯线性提交,零 merge;已推 origin) |
| 提交 | 3+2 笔(规格笔/报告笔/交付笔+zip 终笔+REPORT 勘正笔[§八.1 范围区间 L196-L210→L196-L200 与 §二两处 §七 红线行号 L179→L181 更正为实值;§5.3 第4项出口];全SHA 见 §二 git 取证与 stdout 自述;zip 终笔=DELIVERY §六定值登记) |
| A 类(恰2) | `docs/P1_DESIGN_COMP_REPORT.md` / `docs/P1_DESIGN_COMP_DELIVERY.md`(与 `git ls-files` 零重合 [实取·2026-11-06]) |
| M 类(实触恰1) | `docs/P1_DESIGN.md`: §六 追加两行 L174-L175(WP-P1-F §4a#19/WP-P1-G 候选名 §4a#20,行式对齐既有 A..E 五列式样)+文档尾 §八 规格节 L188 起(§八.1=L192/§八.2=L225,四要素+DP 节齐备);diff=`74 插入/0 删除` [实取·git diff --numstat,纯追加零删行,P1_DELIVERY.md/P1_DATA_NEEDS_INVENTORY.md 零触碰] |
| 改动面 | 零代码/零测试/零 workflow/零 requirements/零 .gitignore;D=0;白名单外零路径变更(AC-05.1 论证=diff 无 `.py`/`tests/`/workflow/requirements 即 docs-only 零测试面变更) |
| 运行产物 | **零**(`data/` 全域零写入;本地 CI 实测=基线测试面验证,非本包运行产物) |

## ② 证据指针

| 证据 | 落点 |
|---|---|
| 证据包 | `/tmp/p1-design-comp-evidence/IA-P1-DESIGN-COMP-EVIDENCE.zip`(八类成员①-⑧;逐成员 SHA256SUMS 在包内,清单自身显式豁免不自入;zip 整体 sha256=**§六 终笔登记**) |
| 本地 CI(AC-06.2) | 逐套件名称+退出码: **75 槽=74 exit=0+1 SKIPPED**(test_glm_live 按 CI 口径跳过;另单独实跑该套件自跳过 exit=0 [实取·/tmp/p1-design-comp-evidence/local-ci/suite-results.txt,2026-11-06]);对照 BASE-COMP-CI-SUITES=75 零回归;aggregate_fail=0 |
| git 取证(AC-05) | 证据包③: diff --name-status/--numstat(逐文件零 '-' 内容行)/rev-parse/log/reflog/ls-remote 全表(开工+推送后双时点)/设计在场核验输出(merge-base/blob 双侧)/M 面零删行取证 |
| LIVE 隔离(AC-05.5) | LIVE `real_data_acceptance.py` sha256=`f9ca189c5248199bb5acbc78b2a2c82d59c10e1c7c2c2d20bdaaa6105fbfe3eb`(前缀与合同 §五.5 一致) [实取·shasum 2026-11-06,只读];LIVE 全目录本轮标记 grep(`R064|P1-DESIGN-COMP|IA-P1-DESIGN-COMP`)**零命中** [实取·Grep 2026-11-06];LaunchAgents 零改动 |
| 零网络/零调用 | 除 git 取证与推送(GitHub 通道,合同明示)外零网络出站;零真实 GLM/LLM 调用、零凭证、零付费 |
| CI dispatch(AC-06.1/06.6) | **操作者 CHECKPOINT 面**: dispatch `offline-tests` 于最终尖端+登记件 `rounds/064/P1-DESIGN-COMP-CI-dispatch-evidence.md`(引擎侧路径,执行Agent 不可达);本包不代行 |

## ③ 逐 AC 自评(七条)

| AC | 自评 | 证据指引 |
|---|---|---|
| AC-01 开篇核验与设计在场 | PASS(自评) | REPORT §零.1 ①-⑥ 全过+证据包③ git 取证;分支首提交父=BASE-COMP;三件 blob 双侧等值 |
| AC-02 规格落位完备性 | PASS(自评) | §六 恰 2 行(L174/L175)显式挂靠 #19/#20+行式对齐 A..E;两包四要素+DP 节可定位(REPORT §一行号登记);互斥划界显式(行内+§八头);依赖列锚 file:line;要点客观可核验+DP 承接语+PENDING 标注;#21 面不下放(仅衔接注记) |
| AC-03 溯源真实性与数值标注 | PASS(自评) | REPORT §二 溯源表(逐要素→甲/乙/丙锚,零源断言=无);§五 数值扫描清单三态成件;[实取] 项全部工作树实读复核 |
| AC-04 引用真实性与注入边界 | PASS(自评) | 全部 file:line 引用=BASE-COMP 工作树实读(grep/Read 实测,偏差≤3 行);注入内容一律标「注入摘要(2026-11-06),非工作树实读」;跨支引用=零;零引擎路径交付依赖;否定性声明可 grep/diff 反证 |
| AC-05 范围/分支/生产隔离 | PASS(自评) | diff name-status=A2+M1(⊆三件且含 P1_DESIGN.md)、D=0;M 面 numstat 0 删行;纯线性零 merge;ls-remote 双时点对照(47 支基线尖端不变+唯一新增 dev/p1-design-comp);LIVE 零写入(②节取证);.gitignore/data 零触碰 |
| AC-06 CI 与证据包 | PASS(自评,除 CI dispatch=操作者面) | 本地 75 槽全绿(②节);证据包八类成员+SHA256SUMS(zip sha256=§六终笔);DELIVERY 五节齐备;stdout 四段齐备;CI dispatch 登记件=操作者 CHECKPOINT 待落(执行席不代行,见 §④.1) |
| AC-07 使用边界与 DP 分类 | PASS(自评) | DP 节两包齐备(登记型 6+确认型 2,确认型全 PENDING·确认权留用户,REPORT §三);零真实调用/零网络/零凭证/零付费;架构纪律承接(快照+门禁/append-only+状态机);无投资建议文案;W4/W5 不入链;#21 面不下放 |

## ④ 如实偏差与声明

1. **CI dispatch 非执行席动作**: AC-06.1/06.6 属操作者 CHECKPOINT 面(合同 §六.6 明文「执行Agent不得自行 dispatch」);本 DELIVERY 与 stdout 仅登记其将落路径 `rounds/064/P1-DESIGN-COMP-CI-dispatch-evidence.md`,结论值(run ID/conclusion/套件数)由操作者落字面值——非本包偏差,如实登记。
2. **zip 内副本=装配时点版**: 证据包装配于 zip 终笔提交之前;zip 内 REPORT/DELIVERY 副本=装配时点版,zip 终笔追加的 DELIVERY §六 定值行不在 zip 副本内(R019/R048 先例口径;终局自述以会话 stdout 四段为准)。
3. **WP-P1-G 为候选包名**: #20 实现包名未预登记(合同 §八.6),规格以「候选名」标注,终名由主Agent #20 实现包预拟轮定——登记性让渡,非终局裁断。
4. **编辑前行号估值更正**: REPORT §零「§八=L184 起」为编辑前估值,实测 L188,已按实值更正登记(REPORT §五 #18 D 态=无残留疑似失实)。
5. **本地环境差异预声明**: 本地 Python 3.9.6(CI 固定 3.11);75 槽全绿已实测,若操作者 dispatch 的 CI 因环境差异出现漂移→情形(b)分流处置,本包零 workflow 改动。
6. **INVENTORY/DELIVERY(设计两件)未触碰**: M 授权面⊆三件,实际触碰=恰 1 件(P1_DESIGN.md);规格落位不需要另两件(落位形态=§六行+文档尾节,合同 §零(iii)),非偏差。

## ⑤ 参考

- 合同: IA-P1-DESIGN-COMP-AC-v1.0(冻结版,提示词附录A内嵌;引擎侧存档 `contracts/IA-P1-DESIGN-COMP-AC-v1.0.md`,执行席不可达)
- 规格落位: `docs/P1_DESIGN.md` §六 L174-L175+§八 L188-L257 [实取]
- 配套: `docs/P1_DESIGN_COMP_REPORT.md`(§零登记/§一落位/§二溯源/§三 DP/§四能力面/§五扫描/§六指针/§七声明)
- 上游对照同源: docs/P1_WP_A..E_REPORT.md §零 登记清单+docs/P1_GAP08_REPORT.md §零.3 [实读]
- 架构: docs/ARCHITECTURE_V2.md v2六层 L26-L49 [实读]

## ⑥ 证据包 zip 定值登记(终笔)

- zip: `/tmp/p1-design-comp-evidence/IA-P1-DESIGN-COMP-EVIDENCE.zip`
- sha256: **`0921b0993427ef4b0a3ae07742db6a1384d9550f6bff878b71e5adecf3c0ebf7`**(105 成员/300812 字节;装配 stdout[python zipfile]与 shasum 独立复算一致;testzip=OK;成员逐哈希=包内 SHA256SUMS 104 行,清单自身显式豁免不入 zip 自身校验和,R019-D3/R026 起口径)

(§六 定值行由 zip 终笔提交落笔——R048 v1.3/v1.4 先例口径;zip 内本 DELIVERY 副本=装配时点版不含本定值行,如实披露;终局自述以会话 stdout 四段为准。)
