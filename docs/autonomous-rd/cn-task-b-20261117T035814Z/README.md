# 中国任务 B 复算与重放包(Audit-R5 条目5)

对象: `20261117T035814Z_中国宏观信用与制造业景气_CN_NEW_LOANS_新增贷款与_CN_PMI_M`
——第五轮审计条目5 要求的中国任务 B: 补齐 CN_PMI_MFG/CN_NEW_LOANS 必要历史后
完成的真实研究(判定档 L3/L4 + 报告),及其计算原件与本包重放。

## 数据接入(条目5 前半)

- **CN_PMI_MFG**: akshare `macro_china_pmi`(东方财富)「制造业-指数」列,
  **226 个月全史 2008-01..2026-10**;2026-10=49.3 与统计局发布一致(锚点核验)。
- **CN_NEW_LOANS**: akshare `macro_china_new_financial_credit`(东方财富)「当月」列,
  **226 个月全史**;实际口径=**对实体经济发放的人民币贷款**(央行社融口径,非全口径):
  累计 2026-10=109149 亿与央行「前十个月对实体 10.91 万亿」逐位一致;
  全口径对照 2026-10=-1000 亿/2026-09≈1.08 万亿(央行)vs 本列 -5846/12734 亿,
  口径差在 `config/metric_registry.json` calc 字段如实注记。
- 接入通道=既有 R25 `history_source: macro_collector` 机制(macro 采集档
  `data.<key>.series`),零加载器代码改动;事实通道(china 采集快照)与历史通道
  发布滞后(事实当期=2026-09-01,序列末=2026-10)在判定档 basis 如实披露。
- 月度锚=统计期月首(YYYY-MM-01),与 FRED 月频及 china 采集档月份锚规则同构;
  修订口径: PMI 不追溯修订(统计局),贷款按央行初值。

## 口径台账(研究实际执行口径,全部冻结)

| 项 | 值 |
| --- | --- |
| 股指月频化 | 每日历月最后可得收盘=月末价,月收益=环比;2026-11 残月(月末观测=11-11)剔除 |
| 样本窗 | 月收益 2016-12..2026-10 n=119;宏观全史 n=226;跨资产统计只用重叠窗 |
| 先行定义 | lead-k = 宏观(M) vs r(M+k);PMI k=1 干净(月末公布),贷款 k=1 含月中公布污染已披露、k=2 起干净 |
| 防前视 | CI(M)=sum(M-11..M)−sum(M-23..M);YoY 差分用 M-12;12 月均值比用 M-11..M |
| 统计方法 | Pearson+Spearman;t 与 p=不完全 Beta 精确;相位组间=Welch t(Satterthwaite df)+Mann-Whitney 正态近似;回归 OLS+Newey-West HAC(lag=4) |
| PMI 相位分组 | 荣枯线 50 **严格两侧**(PMI>50 vs PMI<50),PMI=50.0 持平月 3 个(2018-11/2020-01/2026-05)不入任一组——修订 v2 全文统一口径(首轮审查 MF-2: 原相位块为 ≤50 与稳健性块严格 <50 混用) |
| CI 百分位 | 100×count(CI 史 ≤ 当前)/n(n=203) |
| 同期 vs 先行 | 同期相关仅描述性(公布时点晚于当月收益),不用于任何预测表述 |

## 文件

| 件 | 说明 |
| --- | --- |
| `research_seat_calc.py` | 研究席自算脚本(v2: 相位块严格分组修订;标准库 only;输入=同目录 seat_data/,相对路径,无本机绝对路径依赖) |
| `seat_data/` | 原始输入切片(4 指标 ia_cli history 原始输出: CHINEXT/FXI 日频,CN_PMI_MFG/CN_NEW_LOANS 月频全史) |
| `seat_calc_output.txt` | 冻结输出 **v2**(修订后;重放逐字节比对锚,仓内重放已验证逐字节一致) |
| `independent_recompute.py` | 操作者席独立复算脚本(零引用研究席代码路径,自写实现),判定档/报告关键统计值逐项判定(修订后口径 57 项全 PASS) |
| `prerevision/` | **被审原件快照**(首轮独立审查所审内容: 判定档四源件+冻结输出 v1+研究席脚本 v1)——REVISE 裁决 content_sha256 的可复核锚 |
| `review_seat/` | 独立审查席(r5-b-review)工件: verdict.json(REVISE,5 必修)/review.md/recompute.py(独立席自写)/recompute_out.txt |

## 输入哈希(sha256)

```
2d3596bcf88098c3ea08ccdac4f32e2437b5b4641e4ed5bc5928d5372a8ece19  seat_data/CHINEXT.json
37e90b1cb842a54b218f6c91f84aae0d9cdaa6c8d55beaf4aa9d2d221dd99524  seat_data/CN_NEW_LOANS.json
42507d2d2b77321a1a45990124244d30a02028b9c025097abe1ff26f2177b744  seat_data/CN_PMI_MFG.json
614cbe97abf1a586e5bd983ab86125f1b9a7c1a99fb966fe18e3b8b21b79ddcb  seat_data/FXI.json
```

上游: 宏观=引擎 macro 采集档(macro_20261117.json=20261114 全量+CN 两指标全史
新增,见其 `cn_history_addendum` 注记);股指=research_snapshot_20261112_v2。

## 空目录重放

克隆本仓后,仓库根执行:

```sh
python3 docs/autonomous-rd/cn-task-b-20261117T035814Z/independent_recompute.py
python3 docs/autonomous-rd/cn-task-b-20261117T035814Z/research_seat_calc.py | diff - docs/autonomous-rd/cn-task-b-20261117T035814Z/seat_calc_output.txt && echo BYTE-IDENTICAL
```

依赖: 仅 Python 3 标准库。

## 审查链

真实研究→attach(契约门 VERIFIED 6/0/0)→**独立审查席 r5-b-review**(未参与
研究,自写复算实现 /tmp/sr5b/recompute.py,抽核 99 项=96 一致+5 必修,仓内副本
`review_seat/`)→REVISE(verdict 链 rev1,被审原件快照 `prerevision/`)→
必要修订(MF-1 极值月相位归属/MF-2 边界严格化+脚本源头修/MF-3 贷款族 t 断言/
MF-4 方差派生/MF-5 时间框;判定档 17 处+脚本相位块 5 处+冻结输出 v2 重生成,
契约门复验 VERIFIED 6/0/0,生产 re-attach 通过)→操作者席独立复算 57 项全
PASS→同一独立席闭环复验→UPHELD(rev2)→归档 `research_archive/`(链
REVISE→UPHELD)。修订历史完整保留: 裁决链两档+prerevision 原件+本 README。
