# IA-P1-WP-D DELIVERY(交付说明)

> 包: IA-P1-WP-D(P1 四经济体底图层第 4 包: 查询面与共享档案衔接)
> 合同: IA-P1-WP-D-AC-v1.1(FROZEN 2026-11-06 04:0x HKT)
> 分支: `dev/p1-impl-d`(自 BASE-P1D=c11c998d7c6265a9dbc9ef67bcae5757ec57df9d 切出)
> 配套 REPORT: docs/P1_WP_D_REPORT.md(§零 登记+§一 实录;本文件为其交付面摘要)

---

## §一 改动清单

| 类 | 文件 | 摘要 |
|---|---|---|
| A | docs/P1_WP_D_REPORT.md | 登记件+实录(规格抄录/纪律/DP/参数 PD-1..PD-7/映射表/自检) |
| A | docs/P1_WP_D_DELIVERY.md | 本文件 |
| A | tests/test_p1_wp_d.py | 30 用例(要点①t01-t15/要点②t16-t20/要点③t21-t29+t00) |
| M | scripts/e2eb_query_ir.py | ECONOMIES 枚举+validate_ir economy 可选键校验(纯插入) |
| M | scripts/e2eb_query_mapper.py | ECONOMY_CUES 词表+map_question economy 识别条件写(纯插入) |
| M | scripts/research_archive.py | append economy echo 条件写+validate 三条校验(纯插入) |
| M | scripts/e2eb_query_executor.py | CHANNEL_OF_SOURCE 增 jp/ea 两键(纯插入) |

git diff --stat vs BASE-P1D: 4 files changed, 53 insertions(+), 0 deletions(-)(M 类零删除行=既有逻辑零改动);A 类 3 件为白名单全量。

## §二 证据

- 本地 CI 同构: **73 槽=72 exit=0+1 test_glm_live SKIPPED**(逐套件记录 2026-11-05T19:5xZ UTC;logs=/tmp/p1-wp-d-evidence/suite-logs/);预期口径=BASE-P1D-CI-SUITES 72+新增 tests 文件 1(合同 §六.1),一致零漂移。
- 负向敏感性: 4 注入(ECONOMIES 去 EA/mapper 无条件写键/archive echo 校验删除/CHANNEL_OF_SOURCE 去 ea 键)全部 rc=1 红转换,恢复后 30 用例复绿。
- 证据包: `/tmp/p1-wp-d-evidence/IA-P1-WP-D-EVIDENCE.zip`(八类成员+SHA256SUMS;zip 整体 sha256 见 §四)。
- 零运行产物(要点全为【测试】件;REPORT §一.5 对照依据);LIVE 标记 grep 零命中+real_data_acceptance.py SHA256=f9ca189c…前缀一致(合同 §五.6)。
- CI dispatch: 操作者 CHECKPOINT 登记件(引擎侧 rounds/047/P1-WP-D-CI-dispatch-evidence.md,执行Agent 不自行 dispatch)。

## §三 逐 AC 自评

| AC | 自评 | 一句证据指引 |
|---|---|---|
| D-AC-01 规格抄录与登记 | PASS(自评) | REPORT §零.2 L172 逐字抄录+行号;A3+M4 清单;git ls-files 零重合 |
| D-AC-02 逐要点映射 | PASS(自评) | REPORT §一.2 映射 3 行=要点 3 条;落点行号实录;参数登记制三者一致(§一.2 末段) |
| D-AC-03 测试与确定性 | PASS(自评) | 30 用例全合成 fixture+字面量硬编码;73 槽全绿;漂移维护专节=§五;AC-03.7 不适用(§五末判定) |
| D-AC-04 引用真实性 | PASS(自评) | REPORT §零.4/§一.1 行级引用;注入摘要标注「注入」;跨支=基线工作树实读+冻结章 |
| D-AC-05 范围/分支/生产隔离 | PASS(自评) | diff=M4 恰授权触面+A3 恰 k=3;纯线性零 merge;LIVE grep 零命中+SHA 前缀一致 |
| D-AC-06 CI 与证据包 | NOT VERIFIED(执行面自评 PASS/CI 面待操作者) | 证据包八类齐+自述四段;CI dispatch=操作者 CHECKPOINT 面(登记件将落 rounds/047/) |
| D-AC-07 研究纪律 | PASS(自评) | 特有纪律 6 条登记(REPORT §零.4)并遵守;零网络/零 GLM/零凭证(源码 grep+测试直读);发现 F1-F3 登记未越界 |

## §四 如实偏差与登记

1. **合同注记节号笔误(如实登记,非偏离处置)**: 合同 §零(iii-b) 注记与冻结章写「W-1/W-2 场景定义=P1_DESIGN §四 L88-115」——实读为 **§三(d)**(L86 节起;W-1@L88-100/W-2@L102-113;§四 自 L120 起);行号锚定正确、内容无歧义,按节号笔误登记于 REPORT §零.4,未触发 (d)。
2. **rtm.py 侧 economy 字段(F1)**: DESIGN §四 L143 与 L132「task schema 沿用」并存,rtm.py 不在白名单→保守落地 QB- 侧 echo+RT- 引用约定证成;完整落地待操作者处置(REPORT §一.6-F1)。
3. **上游快照 facts 级 jp/ea 接线缺席(F2)**: W-1/W-2 场景以合成 fixture 证成(真实链路执行期缺席=常态如实);WP-B 发现延续,非本包违约。
4. 零其余偏离: 套件数一致(73=72+1 预期口径)、零调参重跑、零运行产物(要点无真实运行面)、零数据档触碰。

**zip 哈希终笔登记位**(装配后回填): 见 §六。

## §五 漂移维护策略声明(AC-03.6;沿 R022 三要素)

1. **测试预期值唯一来源=仓库内版本化合成 fixture**: tests/test_p1_wp_d.py 文件内定义(MAPPER_REG/W1_REG_FORM1/FORM2/W2_REG@L58-91、W1_SNAP 及变体@L100-130),零真实数据档依赖;
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: 预期值字面量与 fixture 定义同文件同 commit,fixture 任何改动须同步重算登记值(digest 类经离线预计算重录,记录于测试文件头注释);
3. **真实数据档(data/daily/ 等)永不进入测试预期值来源**: 测试不读取任何真实档(mapper 测试经 registry= 参数注入;executor 测试经 snapshot=/registry= 注入;archive 测试经 archive_dir=tempdir+合成快照文件)。

**fixture→预期值映射**(逐断言组→fixture 定义处):

| 断言组 | fixture 定义处(file:line) | 预期值形态 |
|---|---|---|
| t01 枚举 | tests/test_p1_wp_d.py:227-229 | 手写字面量元组 |
| t02-t08 schema/接地 | tests/test_p1_wp_d.py:231-278(_mapped_ir/_ea_provenance@L141-168) | 手写字面量+issue 文本子串 |
| t09-t15 mapper economy | tests/test_p1_wp_d.py:281-303(MAPPER_REG@L58) | 族值字面量(EA/CN/JP/US) |
| t16 W-1 形态1 values | tests/test_p1_wp_d.py:308-331(W1_SNAP facts@L100-124+PD-5) | {MB-1:3.88,MB-2:3.75,MB-3:4.00,MB-4:4.98,MB-8:1.12,MB-9:65.16} |
| t17/t18 A2/A3 归因 | tests/test_p1_wp_d.py:333-354(W1_SNAP/W1_SNAP_EA_OK sources_status) | 状态+reason 子串字面量 |
| t19/t20 W-2 values | tests/test_p1_wp_d.py:356-390(W1_SNAP china/global facts) | {MB-1:6.64,MB-2:33.08,MB-3:23294.42,MB-4:132.49}+G-P1 编号子串 |
| t21-t23 档案绑定 | tests/test_p1_wp_d.py:393-445(W1_SNAP) | DIGEST_W1=758ad6f9ef881eb1[预计算字面量@L132] |
| t24-t29 校验/约定 | tests/test_p1_wp_d.py:447-478(_record@L170-186) | issue 子串+零 issue 字面量 |

**AC-03.7 判定**: 不适用——登记清单(M 四件+A 三件)零外部服务调用面实现(无 GLM/LLM 客户端/网络编排/数据源客户端类文件;scripts 四件 import 面纯标准库+项目既有模块);测试注入点=显式参数注入(registry=/snapshot=/archive_dir=,mapper D-B1-11/executor D-B2-01 既有注入面),fixture 构造处 tests/test_p1_wp_d.py:38-133。

## §六 zip 哈希终笔登记

(装配后回填: zip 整体 sha256+成员数+装配 UTC 时刻)

## §七 参考

- 合同: IA-P1-WP-D-AC-v1.1(提示词附录A;存档=contracts/IA-P1-WP-D-AC-v1.1.md,引擎侧)
- 设计: docs/P1_DESIGN.md §六 L172(WP-P1-D 行)+§三(c)(d)+§四衔接设计 L130-143+§七
- 上游: docs/P1_WP_A_REPORT.md §零.2/§零.3、docs/P1_WP_B_REPORT.md §零.3-§零.4、docs/P1_WP_C_REPORT.md §零.2-§零.3(在场实读)
- 配套: docs/P1_WP_D_REPORT.md(§零 登记+§一 实录)
