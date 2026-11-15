# R41 — T8-R2 余留①②③收口报告(T-R41-1,RDG-20261116-011)

> 分支 `dev/rd-r41-t8r2-leftovers`(基点 main=2798d8a,R40 盖章)。
> 日期 2026-11-16(HKT)。三项=T8-R2 独立审计遗留清单§七 1/2/3。

## ① 真实面 0/3 定性收口(诊断实验)

### 方法

复跑器 `tests/r41_realface_runner.py`(非 CI 套件,同 t7_parallel_harness 惯例):
T7 三份真实周报(V1=20261114_UNVALIDATED/V2=20261108_UNVALIDATED/V3=20261024,
LIVE 树只读)用当前引擎全文重跑 `tc.check_text`,对照冻结基线
`audit/arch-reform/T7/t7_results.json`(实际冻结时点=e81d363,T8-R2 审计席复跑
副产品——非 0fbd812 原跑;对照以该文件 stats 为准)。CONTRA **全量**列出
(基线只记前 40 条/报告)。裁定面=唯一 (family,metric,token) 三元组全量
(≈95 簇)对报告原文 ±30 字语境逐簇人工复核,簇内同族形态同判。

### 结果

| 报告 | 基线 contra | 当前 contra | 漂移 |
|---|---|---|---|
| V1 | 53 | 53 | 0 |
| V2 | 175 | 175 | 0 |
| V3 | 98 | 98 | 0 |

基线已记录子集(33/39/38 唯一三元组)⊆ 当前全量,零消失。**零漂移口径=
contra/verified/unbound 三计数逐位同**(checks 总数 V2 +3/V3 +2=后继轮
新增 INSUFFICIENT 类披露行,工件 baseline_stats 如实在档;独立审计 MINOR-2
点名后补此披露)。**真实面通过率
维持 0/3,全量迁移口径未闭合——T7 deployment_implication 原判维持
(自由文本面 FK 硬化前不接管,Gate B 继续值守)。**

### 逐簇裁定(326/326 全覆盖,零真错)

机械件=`audit/arch-reform/T7/t7_realface_r41.json`(runs+adjudication 双面)。
机制族滚存(按 token 数):

| 族 | n | 说明(代表证据) |
|---|---|---|
| A 元数据/序号/引用ID/切分碎片泄漏 | **154** | `<!-- 生成: 2026-11-08 16:22:44 \| glm-5.3 \| … -->`注释数字被抽 token 承前绑指标;`[art_9456078…]`引用ID;`3.8775%`→`8775%`小数误切分;报告内嵌 JSON provenance(`"value":2.5658`);列表序号`1./2./3.` |
| B 评分卡表分值列/表内碎片 | 40 | `\| WTI期货 \| 90.83美元 \| … \| +2 \|`行尾分值列(+1/+2/0/−1/−2)绑该行(或跨行)指标水平 |
| D 别名缺席/子串吞并/同名与期限歧义 | 38 | 日债2Y/5Y/10Y→UST(FK-3);非农存量159,293千→UNEMPLOYMENT;BEI 10Y 内「10Y」;CN CPI→US CPI;MRO→DFR;上证PE→SHCOMP;5Y TIPS/BEI→10Y 族 |
| G 条件句/失效触发阈值/疑问推测 | 28 | 「失效条件 DXY>105」「CCC<1000bp」「金价<4200」「SPX 跌破7400」「信心反弹>50」「是否…甚至倒挂」(疑问句;基线 e81d363 同判亲证=**非 R38 后回归**,临时 worktree 0fbd812/e81d363 双点归因) |
| C 前瞻/路径值绑当期(FK-7) | 23 | 期货隐含路径逐月值 3.8775%→4.07%→…→4.715%;V3「从3.885%升至4.575%」曲线路径;「未来6个月加息约70bp」 |
| K 检查器误触发族 | 16 | 常量复述容差未中(850bp/5.29%);距离碎片「距离仅1」;反推复述「约25.6」;排名同值复述;跨资产差异当利差;`nan` 字面 |
| F 枚举错位/跨指标串绑(FK-2) | 13 | GLD→黄金;FXI/恒生国企→恒指/上证;NVDA→NDX/SPX;表列周变化错列 |
| I 上期值/历史周/旧观测日 | 5 | 「BEI 从2.34%回落至」「10/15当周2.84%、10/22当周2.64%」;表内显式 2026-09-01 旧观测 |
| H 检查器长距取数(FK-8) | 5 | VIX 25.64 桥式复述;相关系数 −0.35/+0.72 |
| E 单位换算缺口(FK-5) | 4 | 「16.5万人」=+165千;1340bp=13.40% |

**结论**: 三份真实报告的全部 CONTRA=引擎绑定面误报(报告文本本身无误),
零真错拦获、零真错漏判证据;真错面(数值与快照矛盾的真陈述)在 T8 后的
三轮修复中未被误放行(基线子集零消失)。最大单一可治面=**A 族(154/326,
47%)**:HTML 注释/元数据/引用 ID/小数切分碎片——一个「检查面预处理:
注释剥离+碎片 token 过滤」即可腰斩误报面,属后续硬化首位(登记见 RDG-011
回看,不动本轮)。

R27 修的是旧 Gate B 提取器(不动 tc);R35 利差披露/R38-R40 叙事族不触
FK 绑定面——真实面零漂移与该因果链一致。

## ② band_label 双报去重提示(最小修)

`check_text` 聚合前加派生标记(状态零变动,「宁多报不漏报」取向保持):
同指标存在 `level` CONTRA 时,`band_label` CONTRA 增 `co_anchor:
'level_contradicted'` 字段+注记后缀——报告层可据此把带判定渲为
「随 level 已另报(按快照落带)」单行,不再双行独立报错。纯 band 面
(值对标签错)与纯 level 面零触碰。T8R2 审计原句形态冻结入新套件 B1-B3。

## ③ _check_score_total 硬编码维度→规格表单源(设计先行)

设计变更: 维度组成从「tc 与 macro_scorecard 双处控制流枚举」改为
**单源规格表** `scripts/research_contract/scorecard_spec.py`(契约内件,
零 import,纯度律内):

- `SCORECARD_DIMENSIONS`: 2 维度×8 行,行=(metric, source, band, keys);
  source=('level',)或(period,field);band='std'/'rev';keys=4 签字 stable_key
  (值权威仍=config/thresholds.json,本表只声明结构)。
- 消费面①: `text_consistency._check_score_total` 改表驱动循环
  (i_parts/g_parts 字面枚举退役),行为逐值保持(整型和=顺序无关;
  INSUFFICIENT/regime 段原样)。
- 消费面②: `macro_scorecard.SCORECARD_THRESHOLD_KEYS` 35 键平行枚举退役,
  改由 spec `threshold_keys()`∪REGIME∪EXTRA 推导(集合逐位等价亲证,
  fail-closed 缺键门原样)。
- 对账门 G2(`thresholds_gate.g2`)静态锚随迁: 声明面=spec 源码三处字面量
  (维度行键 `.scorecard.` 族+REGIME/EXTRA 元组)+macro_scorecard 推导式
  在场核验;**强度不降**——差集双侧为空语义原样,变异测试随迁
  (声明键被删→红;退回硬编码+裸常量→G2+G4 双红),t1t2 90/0。

新增评分卡指标自此只改规格表一行+签字注册表重走金融席签字,两消费面
自动生效(维护性风险消除=审计遗留③原诉)。

## 验收

- 新套件 `tests/test_rd_r41_t8r2_leftovers.py`(②③+单源行为锁+变异自证)。
- 受影响面回归: t8r/t6c/phase4/t1t2/phase3 等(见 ITERATION_LOG R41 行)。
- 独立审计: 未参与席四维(代码正确性/诚实纪律/契约不变性/测试真实性),
  报告落 `audit/arch-reform/R41/`。
