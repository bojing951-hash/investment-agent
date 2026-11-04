# IA-P03-E2EB-WP-B4 DELIVERY — 共享研究档案与查询历史(append-only)交付说明

> 包: IA-P03-E2EB-WP-B4 · 分支 `dev/p03-e2eb-b4` · 基线 b5c33f85c42e12b4f04e2a80faa1131244997c70(main 尖端,含 E2E-A/B1/B2;B3 停泊不入基线)
> 详细 REPORT: `docs/P03_E2EB_B4_REPORT.md`(规格抄录/参数登记 D-B4-01..12/映射表/AC 自检/数值六项清单)
> 证据包: `/tmp/p03-e2eb-b4-evidence/IA-P03-E2EB-WP-B4-EVIDENCE.zip`
> 时区: 本文件时刻均为 UTC

## §一 改动清单(What)

- **新增(纯 A 行,白名单 k=4)**: `scripts/research_archive.py`(395 行档案存储模块: query_history 集合一记录一文件 append-only,重复写入/改写一律拒+零 update/delete API;ID 引用约定四 ID 校验[QB 严格格复用 qir.QUERY_ID_RE/RT- 前缀族/echo/日期段一致性];snapshot_id+digest 内容级绑定[R5 模块内重算 FIX-01 纪律,API 无 digest 入参,FIX2-04 版本规范,R1 身份纪律,verify 单档+全档案复算,篡改→拒绝];同日单调跨日独立配号 allocate_query_id[D-B1-10 承接];确定性 answer_summary;双阶段 IR 探测复用 qir.validate_ir)+ `tests/test_p03_e2eb_b4.py`(675 行 50 用例,七类 T0..T6)+ `docs/P03_E2EB_B4_REPORT.md`(§零-§九)+ 本 DELIVERY;
- **零改动**: B1 两模块(只读复用 qir.QUERY_ID_RE/validate_ir/make_query_id)/research_provenance(只读复用 rp.digest_snapshot,签名零改动)/E2E-A 六文件/registry/workflows/既有任何文件(diff 零 M/D);
- **无并入步**: 设计三件经 B1 指定并入步已在基线祖先谱系(开工步骤4 实测 merge-base 可达+三件 blob 等值)。

## §二 证据(Evidence)

- 本地 CI 同构: 63 个 test 文件→62 运行套件(排除 test_glm_live 跳过),**61 绿+1 既有红**(test_p4_fixes,基线同款「39通过/4失败」DEV data/daily 真实副本触发 real 分支所致,CI fresh checkout 绿,零导入关系);新套件 `test_p03_e2eb_b4` exit=0(Ran 50 tests OK);计数与冻结合同「58+1=59」不符的谱系分解如实登记(REPORT §七.5: 58=B2 谱系计数,基线经两次 merge 合入 main 侧 3 个 GLM 测试文件→62+1=63);
- 负向敏感性: D1-D4 真实注入定向红(3/4/1/1)→还原→50 全绿→模块 sha256 逐字节一致(`635d9a3e…4aeb3`,4 次比对);
- 证据包八类成员+SHA256SUMS(zip 整体 sha256 见 §五自指豁免行与证据目录 08-sidecar/final-state.txt);
- CI dispatch: 操作者 CHECKPOINT 登记件 `rounds/024/E2EB-WP-B4-CI-dispatch-evidence.md`(执行Agent 未自行 dispatch);
- 运行产物: **零运行产物**(DESIGN 未为 WP-B4 指定真实运行面,端到端走查属 WP-B5;全部验证走合成 fixture/tempdir,data/research/ 与 data/daily 零真实读写)。

## §三 逐AC自评(Assessment)

AC-01 PASS(规格逐字抄录 L228-232 行号零偏差+清单 k=4 零重合+推导无越界)/AC-02 PASS(L232①②③+六补充要点映射全落;④本地侧 61 绿+1 既有红归因,Actions run=操作者派发面)/AC-03 PASS 生效(50 用例全绿,合成 fixture 唯一数据源,预期值字面量硬编码+hashlib 独立旁证,专节三要素+映射节齐备)/AC-04 PASS(引用可寻,实现件行号 08f0dcc 工作树实取复核)/AC-05 PASS(纯 A diff+纯线性+reflog 无 reset/amend+ls-remote 34 支不变+LIVE 零写入+复用禁分叉 T5 锁)/AC-06 本地侧 PASS+CI run 待操作者登记(①=操作者 CHECKPOINT 面 NOT VERIFIED)/AC-07 PASS(原始采集档结构性不可达+零填0+零 GLM/网络/凭证+W4/W5 零链+白名单外零实施)。详见 REPORT §八。

## §四 如实偏差(Deviations)

1. DESIGN §4.1 RT 严格格(RT-YYYYMMDD-NNN)与 E2E-A 实况形态(RT-{start}~{end}-{rule}-{hash8})分歧→采 RT- 前缀族(严格格=真子集),登记型发现不擅改设计,处置权操作者(REPORT §七.1);
2. 重复写入选严格拒绝(要点①字面)与 E2E-A 幂等跳过分歧,运行前登记 D-B4-05(REPORT §七.2);
3. D-B4-02 实现期一次性正则收紧(`^RT-.+$`→`^RT-\S+$`),发生于任何真实运行/测试定稿前,非运行后回改(REPORT §七.4);
4. CI 套件计数 63 文件/62 套 vs 冻结「58+1=59」=谱系事实(main 侧 3 GLM 测试经 merge 入基线),零回归判据逐套对照成立(REPORT §七.5);
5. test_p4_fixes 本地既有红(基线同款环境红,零导入关系,REPORT §七.6);
6. Actions run gh api 核验两次被拒(环境授权限制),run 归属以本地 git 事实链佐证,操作者可复核(REPORT §七.7);
7. /tmp 一次性工具(precalc/inject/ci-runner)入证据包不入白名单(REPORT §七.8);
8. 无其他偏离;未触发情形(b)/(c)/PREEMPT-STOP(REPORT §七.9)。

## §五 参考与登记(References)

- 规格锚: `docs/P03_E2EB_DESIGN.md` §六 WP-B4 行(L228-232)/§4.1(L180-185)/§四行3-6(L173-176)/§七(L244-249)(基线工作树实读);
- 对齐既有件: 复用调用 e2eb_query_ir(QUERY_ID_RE/validate_ir 双阶段/make_query_id)/research_provenance(digest_snapshot R5/_version_of FIX2-04/select_snapshot R1 先例),零复制分叉;E2E-A rtm 原子写/一档一文件=机制同构先例非逻辑复制;
- 模块 SHA 与提交链登记: REPORT §五;zip 整体 sha256 实测值(装配后追加行,自指豁免沿 B1/B2/G1/G2 先例):

```
(装配后追加行)
```

> 自指豁免: zip 内 DELIVERY 副本(成员②)=终版提交版无上行实测值,固定点不可内含自身哈希;推送终态(最终尖端/最终 ls-remote)见证据目录 08-sidecar/final-state.txt(zip 外),B1/B2 同款先例。

---

## 专节 漂移维护策略与 fixture→预期值映射(D-B4-12)

**漂移维护策略(合同 AC-03⑥ 三要素按名目声明)**:

1. **①测试预期值唯一来源=仓库内版本化合成 fixture**: 全部预期值字面量硬编码于 `tests/test_p03_e2eb_b4.py` L129-146(合成 fixture 定义 L43-125 与预期值字面量同文件,随本包提交链版本化);
2. **②fixture 演进时预期值与 fixture 同一 commit 变更**: fixture 定义与预期值同处一文件(tests L43-146),物理不可分离——任何 fixture 变更必然与对应预期值变更落在同一 commit(结构性保证,零人工纪律依赖);
3. **③真实数据档(`data/daily/`、`data/research/` 既有档)永不进入测试预期值来源**: 测试零读取真实数据档(全合成 fixture 唯一源;T5 纯度锁用例反证: 源码 open( 面恰 3 处白名单函数+原始采集档文件名模式零存在+DEFAULT_ARCHIVE_DIR 隔离)。

补充维护条款: 上游接口漂移(qir schema 枚举/rp.digest_snapshot 算法或 rp.select_snapshot 语义)→ 按合同情形(b)如实报告主Agent 禁当场改;T0/T3/T5 接线锁将定向红,红即信号非误报;本包登记参数 D-B4-01..12(REPORT §六)运行后禁回改,后续包(WP-B5 编排面)如扩展档案集合(research_tasks/anomaly_events)属新包登记面,不回写本包模块。

**fixture→预期值映射**(逐断言组;全部字面量硬编码于 tests L43-146,快照 digest 经 /tmp/b4_precalc.py R5 真实管线预计算+hashlib 独立旁证后誊写,零自证恒真):

| 断言组 | fixture输入(发明字面量) | 预期值字面量 | 语义锚 |
|---|---|---|---|
| T0 fixture 自检 | SNAP_A(SNAP_ID=research_snapshot_20261105,PASS,USDJPY=157.8@2026-11-04)/SNAP_B_V2(_v2,DEGRADED,158.2@2026-11-05) | L_DIGEST_A=`756c258d9943841d`/L_DIGEST_B_V2=`2418e26ca8294e02` | R5 canonical JSON sha256 前 16 位(rp.digest_snapshot:1297-1301) |
| T1 append 落盘 | IR_M(QB-20261105-001,mapped,MB-1 PENDING/MB-2 ABSENT_REGISTRY,OP-1 NO_DATA)+SNAP_A | 状态 `written`/记录十三键/digest=L_DIGEST_A/archived_at=L_ARCHIVED_AT=`2026-11-05T02:00:00+00:00` | D-B4-03 schema+D-B4-05 步⑧原子落盘 |
| T1 重复写入拒绝 | 同 query_id 二次 append(同内容/异内容)+预置同 id 文件 | 状态 `rejected-duplicate-query-id`+既有文件字节不变 | 要点①严格读法(D-B4-05) |
| T1 同日单调/跨日独立 | seq 001→再写 001/跨日 20261104-001 | `rejected-non-monotonic-seq`/跨日 written | D-B4-06(L183 单调,允许空洞) |
| T2 ID 约定 | QB 严格格/RT-YYYYMMDD-001(DESIGN 严格格)与 RT-2026-06-30~2026-09-30-RD-DIV-001-17788777(E2E-A 实况形态)双合法族+尾随空白 id | issues 空/非法项逐一入 issues | D-B4-02(RT-前缀族=G3 先例,严格格=子集) |
| T3 digest 绑定 | 篡改快照文件/删快照/坏 JSON/内部 snapshot_id 不符/记录携错 digest | verify ok=False,issues 含「digest不匹配(快照内容与档案绑定漂移/篡改嫌疑)」等结构化原因 | 要点③+D-B4-08(R1 身份纪律) |
| T3 v2 解析 | SNAP_B_V2(research_snapshot_20261105_v2) | 文件名解析 research_snapshot_20261105_v2.json+L_DIGEST_B_V2 | FIX2-04 版本规范(rp._version_of:1212-1227) |
| T4 摘要确定性 | EXEC_OK(values={MB-1:157.8})/EXEC_REFUSAL(gate FAIL) | L_SUMMARY_EXEC={ABSENT_REGISTRY:1,RESOLVED:1,NO_DATA:1,values={MB-1:157.8}}/L_SUMMARY_REFUSAL(refusal=L_REFUSAL 上浮)/L_SUMMARY_MAPPED | D-B4-04(计数+仅成功 values+refusal 原样) |
| T4 echo/日期一致性 | IR_M echo 四字段+query_id 日期段 | 与 ir 同名字段相等/QB-20261105↔created_at 2026-11-05 | D-B4-03 echo/D-B4-02④ |
| T5 纯度锁 | 模块源码文本 | 无 `hexdigest()[:16]`/无原始档前缀/open( 恰 3 处/零网络 import/API 白名单/LIVE 路径零涉 | D-B4-10/11(复用禁分叉+AC-07.1) |
| T6 fail-loud | 坏 IR(双阶段皆败)/snapshot 缺 snapshot_id/target 不一致/execution.ir 不等 | ValueError 定向异常 | D-B4-05 步①②④ |

> 表中字面量均为 tests 实登记值的转录(源: tests/test_p03_e2eb_b4.py L43-146);语义锚对应模块路径(REPORT §二);L_REFUSAL=`Gate A状态'FAIL'不放行正式研究查询(R3)`(B2 D-B2-03 refusal 原样上浮,EXEC_REFUSAL fixture L123-125 与预期 L131 同源誊写)。
