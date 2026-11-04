# IA-P03-E2EB-WP-B1 DELIVERY — NL→查询映射层交付说明

> 包: IA-P03-E2EB-WP-B1 · 分支 `dev/p03-e2eb-b1` · 基线 a6d086b8b184067d530815e0bf8963d959275743
> 详细 REPORT: `docs/P03_E2EB_B1_REPORT.md`(规格抄录/参数登记/映射表/自检清单)
> 证据包: `/tmp/p03-e2eb-b1-evidence/IA-P03-E2EB-WP-B1-EVIDENCE.zip`

## §一 改动清单(What)

- **新增(纯A行,白名单k=5)**: `scripts/e2eb_query_ir.py`(IR schema定义与两阶段字段级校验)+ `scripts/e2eb_query_mapper.py`(NL→IR v1约束式映射器: 4概念规则/三阶段发射/缺席A1=注册表检索发现/out_of_scope拦截/as_of检测)+ `tests/test_p03_e2eb_b1.py`(59用例)+ 本 DELIVERY + `docs/P03_E2EB_B1_REPORT.md`;
- **指定并入步**: merge --no-ff f1fe593(恰1个merge提交800960e,merge-base=1ddfb65,结构性零冲突,E2E-B设计三件入工作树);
- **零改动**: E2E-A六文件/主流水线/registry/workflows/既有任何文件(diff零M/D)。

## §二 证据(Evidence)

- 本地CI同构: 58个test文件→57 CI套件(排除test_glm_live),56绿+1既有红(test_p4_fixes,基线同款4项归因,零导入关系)+1跳过;新套件 `test_p03_e2eb_b1` exit=0(59用例);
- 负向敏感性: D1-D4真实注入全红(1/1/1/2)→还原→59全绿→模块sha256逐字节一致;
- 证据包八类成员+SHA256SUMS(zip整体sha256见§五自指豁免行与证据目录08-sidecar/final-state.txt);
- CI dispatch: 操作者CHECKPOINT登记件 `rounds/021/E2EB-WP-B1-CI-dispatch-evidence.md`(执行Agent未自行dispatch);
- 运行产物: 零运行产物(验收要点无真实运行面;映射器只产IR不取数)。

## §三 逐AC自评(Assessment)

AC-01 PASS(规格逐字抄录L210-214+登记清单k=5零重合)/AC-02 PASS(4要点映射表全落点实取)/AC-03 PASS生效(59用例全绿,合成fixture唯一数据源)/AC-04 PASS(引用可寻,注入已标注)/AC-05 PASS(纯A diff+分支拓扑合规+LIVE零写入)/AC-06 本地侧PASS+CI待操作者登记/AC-07 PASS(零直读零网络零建议文案)。详见 REPORT §八。

## §四 如实偏差(Deviations)

1. tests文件名以冻结合同实值名 `tests/test_p03_e2eb_b1.py` 为准(DESIGN L214草案glob差异公开登记,REPORT §七.1);
2. test_p4_fixes本地既有红(基线同款,零导入关系,REPORT §七.2);
3. 生命周期哨兵PENDING_EXECUTION=映射期新增词汇(D-B1-01运行前登记,终态枚举不动,REPORT §七.3);
4. 其余无偏离;零调参/零造数/零静默绕过。

## §五 参考与漂移维护策略(References)

- 规格锚: `docs/P03_E2EB_DESIGN.md` §三(a)/(c)/(d)/§六WP-B1/§七(并入后工作树实读);
- 对齐E2E-A: 复用调用 fact_engine(E1/E2/E4/单位常量),零复制分叉;
- 漂移维护: 上游registry/fact_engine接口漂移→情形(b)如实报告禁当场改;WP-B2实现时按REPORT §六登记参数承接(哨兵语义/发射序/缺席模板),运行后禁回改;
- 模块SHA与提交SHA登记: REPORT §五;zip整体sha256实测值(装配后追加行,自指豁免沿G1/G2先例):

```
(待装配后追加: IA-P03-E2EB-WP-B1-EVIDENCE.zip sha256 = <实测值>)
```
