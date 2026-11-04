# IA-P03-E2EB-WP-B5 DELIVERY — E2E-B场景端到端验收(接地强制渲染+走查固化)交付说明

> 包: IA-P03-E2EB-WP-B5(E2E-B 第 5 实现包·B 族末包) · 分支 `dev/p03-e2eb-b5` · 基线 ac01d0726228f4c2196a0618218332717829575f(dev/p03-e2eb-b4 最终交付尖端;含 E2E-A/B1/B2/B4;B3 停泊不入基线)
> 详细 REPORT: `docs/P03_E2EB_B5_REPORT.md`(规格抄录/参数登记 D-B5-01..16/映射表/AC 自检/数值六项清单)
> 证据包: `/tmp/p03-e2eb-b5-evidence/IA-P03-E2EB-WP-B5-EVIDENCE.zip`
> 时区: 本文件时刻均为 UTC

## §一 改动清单(What)

- **新增(纯 A 行,白名单 k=4)**: `scripts/e2eb_answer_renderer.py`(约260行渲染/校验模块: 接地标识三形态校验[形态①metric_id+fact_id 复用 qir.FACT_ID_RE/②snapshot_id+字段路径/③source_file+observation_date,至少一种完整,渲染层独立复验纵深防御]+派生值 calculation_ref+operand 观测链校验+GroundingError fail-closed 零部分输出[L115]+缺席文本化 A1-A4 逐字措辞[L124-127,A4 引擎 reason 原样转述]+NO_DATA 不部分计算[L129]+质量披露[L116]+禁语守卫复用 eqm.OUT_OF_SCOPE_PATTERNS 禁复制[§七3/L248,豁免 unresolved/footer 行登记]+refusal 渲染[B2 D-B2-03 消费面];零文件 IO 零网络,依赖面恰 qir+eqm)+ `tests/test_p03_e2eb_b5.py`(约810行 56 用例,八类 T0..T7)+ `docs/P03_E2EB_B5_REPORT.md`(§零-§九)+ 本 DELIVERY;
- **零改动**: B1 两模块(只读复用 qir 正则/eqm 词表)/B2 执行器(输入面只读消费)/B4 档案(测试链复用调用 append_query_record/verify_query_record)/E2E-A 六文件/registry/workflows/既有任何文件(diff 零 M/D);
- **无并入步**: 设计三件经 B1 指定并入步已在基线祖先谱系(开工步骤4 实测 merge-base 可达+三件 blob 等值)。

## §二 证据(Evidence)

- 本地 CI 同构: 64 个 test 文件→63 运行套件(排除 test_glm_live 跳过),**62 绿+1 既有红**(test_p4_fixes,基线同款「39通过/4失败」DEV data/daily 真实副本触发 real 分支所致,CI fresh checkout 绿,零导入关系);新套件 `test_p03_e2eb_b5` exit=0(Ran 56 tests OK);计数与冻结合同基线 62 精确吻合(62+本包新增 1=63);
- 负向敏感性: D1-D4 真实注入定向红(5/3/1/2)→还原→56 全绿→模块 sha256 逐字节一致(`af467a33…f945`,5 次比对含基线);D4 首试注入器语法缺陷(收集期 IndentationError,非被测件缺陷)如实登记并原样留存(REPORT §三/§七.4);
- 证据包八类成员+SHA256SUMS(zip 整体 sha256 见 §五自指豁免行与证据目录 08-sidecar/final-state.txt);
- CI dispatch: 操作者 CHECKPOINT 登记件 `rounds/025/E2EB-WP-B5-CI-dispatch-evidence.md`(执行Agent 未自行 dispatch);
- 运行产物: **零运行产物**(DESIGN 未为 WP-B5 指定编排入口/真实运行面;要点②测试数据源按 AC-03 合成 fixture 纪律处理=结构参照注记,REPORT §七.1;全部验证走合成 fixture/tempdir,data/research/ 与 data/daily 零真实读写——数据面 sha256 锚定清单 27 文件入证据包⑥,测试前后不变)。

## §三 逐AC自评(Assessment)

AC-01 PASS(规格逐字抄录 L234-238 行号零偏差+清单 k=4 零重合+推导无越界+要点③ B3 条件款按合同 §0 处置)/AC-02 PASS(L238①②④+③情形(c)登记映射全落;④本地侧 62 绿+1 既有红归因,Actions run=操作者派发面)/AC-03 PASS 生效(56 用例全绿,合成 fixture 唯一数据源,预期值字面量硬编码+/tmp/b5_precalc.py 真实管线预演核验誊写,专节三要素+映射节齐备)/AC-04 PASS(引用可寻,实现件行号 a0c0039 工作树实取复核)/AC-05 PASS(纯 A diff+纯线性+reflog 无 reset/amend+ls-remote 35 支不变唯一新增本支+LIVE 零写入+复用禁分叉 T7 锁)/AC-06 本地侧 PASS+CI run 待操作者登记(①=操作者 CHECKPOINT 面 NOT VERIFIED)/AC-07 PASS(渲染器零文件 IO+零采集档路径源码锁+write=False 零持久化双断言+零填0+守卫 fail-closed+零 GLM/网络/凭证+W4/W5 零链+白名单外零实施)。详见 REPORT §八。

## §四 如实偏差(Deviations)

1. 要点②「DEV授权副本上全链路/数据档引用」按冻结合同 AC-03(合成 fixture 唯一数据源,R014-D3)处理为 fixture 结构参照注记——B2 §七.1 审计 PASS 同款先例,依 DESIGN L206「验收要点=草案」以冻结合同为准(REPORT §七.1);
2. 要点③=B3 条件款: B3 三段(d)停泊(v1.3 处置待用户)→「升级版待 B3 落定,由后续轮承接」情形(c)如实登记,非静默跳过、不构成情形(d)(REPORT §七.2);
3. commit 信息 T1 用例数笔误(写 12,实测 13): git 信息禁原地改,以 REPORT §二/§九 实取计数为准(REPORT §七.3);
4. D4 注入器首试语法缺陷→修正后合法定向红,首试输出原样留存(REPORT §七.4);
5. test_p4_fixes 本地既有红(基线同款环境红,零导入关系,REPORT §三);
6. Actions run 由操作者 CHECKPOINT 派发登记,执行Agent 侧按本地同构 CI+终态 git 事实链佐证(REPORT §七.6);
7. /tmp 一次性工具(precalc/inject/ci-runner/anchor)入证据包不入白名单(REPORT §七.5 注);
8. 无其他偏离;未触发情形(b)/(c)[要点③属合同 §0 预置处置非本轮触发]/PREEMPT-STOP(REPORT §七.5)。

## §五 参考与登记(References)

- 规格锚: `docs/P03_E2EB_DESIGN.md` §六 WP-B5 行(L234-238)/§三(b) 接地规则(L111-116)/§三(c) 缺席四级(L118-129)/§三(d) 走查(L131-163)/§四(L167-185)/§五 GAP-05/08(L197/L200)/§七(L244-249)(基线工作树实读);
- 对齐既有件: 复用调用 e2eb_query_ir(FACT_ID_RE/SNAPSHOT_ID_RE/ISO_DATE_PREFIX_RE/ANSWER_CONSTRAINTS)/e2eb_query_mapper(OUT_OF_SCOPE_PATTERNS 词表)/e2eb_query_executor(输入面消费)/research_archive(测试链 append/verify)/snapshot_builder(write=False,测试链),零复制分叉(T7 源码锁反证);
- 模块 SHA 与提交链登记: REPORT §五;zip 整体 sha256 实测值(装配后追加行,自指豁免沿 B1/B2/B4 先例):

```
IA-P03-E2EB-WP-B5-EVIDENCE.zip sha256 = 38dca49279e930772162ba18ef50ff6cce19a976be087425bdfb069b5256d80f (装配后实测,assemble TIP=191efff,32成员/112410字节)
```

> 自指豁免: zip 内 DELIVERY 副本(成员②)=终版提交版无上行实测值,固定点不可内含自身哈希;推送终态(最终尖端/最终 ls-remote)见证据目录 08-sidecar/final-state.txt(zip 外),B1/B2/B4 同款先例。

---

## 专节 漂移维护策略与 fixture→预期值映射(D-B5-14)

**漂移维护策略(合同 AC-03⑥ 三要素按名目声明)**:

1. **①测试预期值唯一来源=仓库内版本化合成 fixture**: 全部预期值字面量硬编码于 `tests/test_p03_e2eb_b5.py` L93-119(V_GOLDEN 九值/OP3_RESULT/八条行文本)与各断言组内字面量(合成 fixture 定义 L44-278 与预期值字面量同文件,随本包提交链版本化);
2. **②fixture 演进时预期值与 fixture 同一 commit 变更**: fixture 定义与预期值同处一文件,物理不可分离——任何 fixture 变更必然与对应预期值变更落在同一 commit(结构性保证,零人工纪律依赖);
3. **③真实数据档(`data/daily/`、`data/research/` 既有档)永不进入测试预期值来源**: 测试零读取真实数据档(全合成 fixture 唯一源,写 tempdir;T7 纯度锁用例反证: 被测模块零 open( +零采集档路径模式+依赖面恰 qir+eqm;数据面锚定清单 27 文件 sha256 前后不变,证据包⑥)。

补充维护条款: 上游接口漂移(B1 IR schema 枚举/词表/B2 产出结构/DESIGN 措辞)→ 按合同情形(b)如实报告主Agent 禁当场改;T4/T7 接线锁将定向红,红即信号非误报;本包登记参数 D-B5-01..16(REPORT §六)运行后禁回改;B3 落定后的「双端闭合版升级」(要点③)属后续轮新登记面,不回写本包模块与测试。

**fixture→预期值映射**(逐断言组;全部字面量硬编码于 tests L93-119 与断言内,经 /tmp/b5_precalc.py 真实管线[S1+B2+B5]预演核验后誊写,零自证恒真):

| 断言组 | fixture输入(发明字面量) | 预期值字面量 | 语义锚 |
|---|---|---|---|
| T0 fixture 自检 | DAY(ymd=20261102;usdjpy 149.20/序列 [144.00,146.50,148.10,149.20];ust10 4.72/ust2 4.31/curve 0.42/dfedtarl 4.00/dfedtaru 4.25/dff 4.11) | gate=DEGRADED+core_missing=[];CURVE_2S10S 事实在场;store USDJPY values 同 fixture | S1 核心覆盖+GAP-05 范式 |
| T4 美端九值 | 同 DAY 经 S1 write=False+B2 执行 | V_GOLDEN={MB-1:4.0,MB-2:4.25,MB-3:4.11,MB-4:4.31,MB-5:4.72,MB-6:0.42,MB-7:149.2,MB-10:0.7427,MB-11:3.6111} | E3/E5 引擎口径(手算旁证: 149.2/148.1−1=0.7427%…);要点② |
| T4 派生 | OP-3 operands MB-5/MB-4 | OP3_RESULT=0.41(4.72−4.31)+L_OP3 行文本含 calculation_ref(输入观测日 2026-10-29,2026-10-29+期限匹配) | D3/E11 纪律(B2 D-B2-09) |
| T4 日端缺席 | fixture 注册表八条(零日端身份) | L_MB8/L_MB9 行文本(ABSENT_REGISTRY+「该指标不在注册表(无身份定义),无法取数」+登记「8指标」) | §三(c) A1(L124)+B1 D-B1-05 |
| T4 OP-1/OP-2 | MB-8/MB-9 缺席传导 | L_OP1/L_OP2(「不可计算(NO_DATA,operand缺席不部分计算)」+result=None) | §三(c) L129;要点② |
| T4 行文本 | 黄金链渲染 | L_HEADER/L_MB1/L_MB7/L_MB10(含「口径: 窗口week.pct_change;基准2026-10-23(E3口径)」)/L_FOOTER(无数据2项/不可计算2项) | D-B5-10 模板逐字 |
| T1 接地负向 | 黄金产出深拷贝定向篡改(provenance=None/三形态全破/仅形态③) | GroundingError(前二者)/grounded(后者) | 要点①+L113「之一以上」 |
| T2 四级缺席 | 手造快照(通道 MISSING/零事实/窗口 available=False) | A2「指标已注册但当日采集缺失(登记: …通道global状态MISSING)」/A3「本期无该指标事实(登记: 本期无该指标事实)」/A4 reason 原样+E3窗口不可用前缀 | §三(c) L125-127 |
| T3 质量披露 | 手造事实 quality=DEGRADED/WARN/PASS | 行尾「 \| 质量披露: {status}(非PASS降级披露,A4纪律)」/无披露 | L116 |
| T6 守卫 | eqm.OUT_OF_SCOPE_PATTERNS 21 词逐一 | 命中即 GroundingError;豁免行(unresolved/footer)过 | §七3/L248+D-B5-08 |
| T7 纯度锁 | 模块源码文本 | import 面恰 4(os/sys/qir/eqm)/无逻辑副本函数名/词表复用无本地副本/公共 API 恰 5 | D-B5-01/12 复用禁分叉 |

> 表中字面量均为 tests 实登记值的转录(源: tests/test_p03_e2eb_b5.py L44-119);语义锚对应 REPORT §六参数与 §二实现路径。
