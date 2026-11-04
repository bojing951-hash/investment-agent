# IA-P03-E2EB-WP-B2 DELIVERY — 查询执行器交付说明

> 包: IA-P03-E2EB-WP-B2 · 分支 `dev/p03-e2eb-b2` · 基线 3e7c300b85a38ab2f60990397751e2f3b44a997f(含B1并入)
> 详细 REPORT: `docs/P03_E2EB_B2_REPORT.md`(规格抄录/参数登记D-B2-01..14/映射表/自检清单)
> 证据包: `/tmp/p03-e2eb-b2-evidence/IA-P03-E2EB-WP-B2-EVIDENCE.zip`

## §一 改动清单(What)

- **新增(纯A行,白名单k=4)**: `scripts/e2eb_query_executor.py`(359行查询执行器: 快照绑定R1→S1降级+门禁R3拒答+引擎口径复用E3/E5/E11+spread/level_diff查询期派生+按需配对相关性C3/C4+as_of时点只读锚定+executed两阶段fail-loud)+ `tests/test_p03_e2eb_b2.py`(1065行63用例,十类T0..T9)+ `docs/P03_E2EB_B2_REPORT.md`(§零-§九)+ 本DELIVERY;
- **零改动**: B1两模块(执行器只读复用 `qir.validate_ir` 两阶段校验)/fact_engine/snapshot_builder/research_provenance(既有函数签名零改动,DESIGN L218复用调用)/registry/workflows/既有任何文件(diff零M/D);
- **无并入步**: B1证据三件已于基线3e7c300在main(与B1包的指定并入步不同,本包直自基线切出)。

## §二 证据(Evidence)

- 本地CI同构: 59个test文件→58 CI套件(排除test_glm_live),57绿+1既有红(test_p4_fixes,基线同款4项归因「39通过/4失败」,零导入关系)+1跳过;新套件 `test_p03_e2eb_b2` exit=0(63用例);
- 负向敏感性: D1-D4真实注入定向红(1/15/3/1)→还原→63全绿→模块sha256逐字节一致(`54d1fe0c…a4ba`,4次比对);
- 证据包八类成员+SHA256SUMS(zip整体sha256见§五自指豁免行与证据目录08-sidecar/final-state.txt);
- CI dispatch: 操作者CHECKPOINT登记件 `rounds/022/E2EB-WP-B2-CI-dispatch-evidence.md`(执行Agent未自行dispatch);
- 运行产物: 零运行产物(验收要点无真实运行面;全部取数走合成fixture/tempfile,零真实数据档读取)。

## §三 逐AC自评(Assessment)

AC-01 PASS(规格逐字抄录L216-220+清单k=4零重合)/AC-02 PASS(要点①-⑤映射全落+4补充行)/AC-03 PASS生效(63用例全绿,合成fixture唯一数据源,预期值字面量硬编码)/AC-04 PASS(引用可寻,注入快照=依赖注入语义已登记)/AC-05 PASS(纯A diff+分支拓扑合规+LIVE零写入)/AC-06 本地侧PASS+CI待操作者登记/AC-07 PASS(零open零glob零墙钟零填0,门禁FAIL拒答零部分执行)。详见 REPORT §八。

## §四 如实偏差(Deviations)

1. 要点①数据源差异(DESIGN草案DEV授权副本 vs 冻结合同AC-03合成fixture,依DESIGN L206以冻结合同为准,REPORT §七.1);
2. 双层注册表纪律=结构事实非偏离(执行器绑定身份用注入fixture注册表;S1管线内部沿用真实registry,test_snapshot.py先例同构,REPORT §七.2);
3. level_diff语义登记(D-B2-10: level绑定+derived_window绑定,result=level值−E3窗口基准值,先登记后实现,REPORT §七.3);
4. correlation/level_diff的IR生产面: 映射器v1只发射spread,本包以hand_ir覆盖两类op执行语义,映射器扩展属WP-B3+(REPORT §七.4);
5. macro序列不经series_store→相关性对macro通道结构性NO_DATA,白名单外不实施仅登记(REPORT §七.5);
6. fixture gate=DEGRADED如实(蓄意缺席非核心块+CURVE_2S10S+BTC滞后;PASS路径由R1文件/注入快照覆盖,REPORT §七.6);
7. test_p4_fixes本地既有红(基线同款,零导入关系,REPORT §七.7);
8. /tmp一次性工具脚本(precalc/inject/ci-runner)入证据包不入白名单(REPORT §七.8);
9. 无其他偏离;未触发情形(b)/(c)/PREEMPT-STOP(REPORT §七.9)。

## §五 参考与登记(References)

- 规格锚: `docs/P03_E2EB_DESIGN.md` §六WP-B2(L216-220)/§二R1·R3/§四E3·E5·E11·C3·C4·D6(基线工作树实读);
- 对齐既有件: 复用调用 fact_engine(E3/E4/E5经make_fact/compute_derived)/snapshot_builder(S1,write=False)/research_provenance(R1/R3)/corr_calcs(C3/C4)/e2eb_query_ir(两阶段校验),零复制分叉;
- 模块SHA与提交SHA登记: REPORT §五;zip整体sha256实测值(装配后追加行,自指豁免沿G1/G2/B1先例):

```
IA-P03-E2EB-WP-B2-EVIDENCE.zip sha256 = 14d8e80b054a5a6df711d66916e35d52fdf62cae434a98eb52c9129096145235 (91成员/301343字节, 装配后实测)
```

> 自指豁免: zip内DELIVERY副本(成员②)=c2d473f版无本行, 固定点不可内含自身哈希; 推送终态(最终尖端/最终ls-remote)见证据目录08-sidecar/final-state.txt(zip外), B1/G1/G2同款先例。

---

## 专节 漂移维护策略与fixture→预期值映射(D-B2-14)

**漂移维护策略**:

**合同 AC-03⑥ 三要素按名目声明(B2-fix1,2026-11-05,依审计处方补齐;原专节三条款保留于后)**:
1. **①测试预期值唯一来源=仓库内版本化合成 fixture**: 全部预期值字面量硬编码于 `tests/test_p03_e2eb_b2.py` L89-139(合成 fixture 定义与预期值同文件,随本包提交链版本化);
2. **②fixture 演进时预期值与 fixture 同一 commit 变更**: fixture 定义与预期值同处一文件(tests L89-139),物理不可分离——任何 fixture 变更必然与对应预期值变更落在同一 commit(结构性保证,零人工纪律依赖);
3. **③真实数据档(`data/daily/` 等)永不进入测试预期值来源**: 测试零读取真实数据档(全合成 fixture 唯一源+源码边界锁用例在案,审计独立核验)。

1. **上游接口漂移**(fact_engine引擎口径/snapshot_builder build_snapshot返回结构/research_provenance门禁与select_snapshot/e2eb_query_ir schema枚举)→ 按合同情形(b)如实报告主Agent,禁当场改;套件(T5/T6/T8接线锁)将定向红,红即信号非误报;
2. **后续包承接纪律**: 本包登记参数D-B2-01..14(REPORT §六)运行后禁回改;WP-B3+如扩展映射器发射correlation/level_diff或将macro序列纳入series_store,属新包登记面,不回写本包模块;
3. **SHA与证据链维护**: 模块sha256 `54d1fe0c…a4ba` 与提交链(REPORT §五)为固定点;证据包成员逐件SHA256SUMS,zip整体sha于本文件§五追加行+08-sidecar/final-state.txt(zip外终态)双落档。

**fixture→预期值映射**(逐断言组;全部字面量硬编码于 tests L89-139,手算+/tmp/b2_precalc.py引擎原语预演核验后誊写,零自证):

| 断言组 | fixture输入(发明字面量) | 预期值字面量 | 语义锚 |
|---|---|---|---|
| T1黄金E2E·D2值断言 | DAY_D2(dfedtarl=4.25/dfedtaru=4.50/dff=4.33/ust2=4.58/ust10=5.04/usdjpy@152.75/黄金对数比0.8251/油价差1.8333) | V_D2={MB-1:4.25,MB-2:4.50,MB-3:4.33,MB-4:4.58,MB-5:5.04,MB-7:152.75,MB-10:0.8251,MB-11:1.8333} | level值直取(make_fact管道) |
| T2 as_of锚定·D1值断言 | DAY_D1(as_of=2026-11-01;ust2=4.50/ust10=4.90/usdjpy@152.10/MB-10=0.1317/MB-11=1.4) | V_D1(同构8键) | 时点只读锚定,两日零混采 |
| T1/T2 OP-3期限利差 | ust10=5.04−ust2=4.58(D2);4.90−4.50(D1) | OP3_D2=0.46/OP3_D1=0.40 | spread=v[0]−mean(v[1:]),期限匹配披露 |
| T3引擎一致性·MTD | usdjpy D2序列末日152.75 vs 2025-12-31基准150.00 | USDJPY_MTD_D2=1.0251(%) | E3 mtd=前一自然月末基准 |
| T3引擎一致性·WEEK | ust10 [5.01,5.04]/ust2 [4.66,4.58]周两值 | UST10_WEEK_PP=0.03/UST2_WEEK_PP=−0.08(pp) | E3 week=ISO周起始前最后观测 |
| T3引擎一致性·周%(黄金) | gold 2440(D1)→2450(D2) | GOLD_WEEK_PCT=0.4098(%) | E3 pct_change |
| T3/T7 level_diff | gold level=2450(D2) vs derived_window基准2440(D1路径) | GOLD_LEVELDIFF=10.0 | 同指标两时点差(D-B2-10) |
| T7相关性 | usdjpy/gold共同窗日收益率3样本(D2序列) | CORR_USDJPY_GOLD=0.4675 | C3 paired_returns+C4 pearson复用 |
| T7 JP在场变体 | JP_POLICY_RATE=0.75/JGB_10Y=1.70 | JP_OP1=−3.625(0.75−(4.25+4.50)/2)/JP_OP2=−3.34(1.70−5.04) | 在场身份自动解析+spread口径 |

> 表中数值为tests实登记字面量的转录(源: tests/test_p03_e2eb_b2.py L89-139);语义锚对应执行器路径(REPORT §二);两日其余键(MB-1/2/3 DFEDTARL/U/DFF三日恒定4.25/4.50/4.33)同表首行管道。
