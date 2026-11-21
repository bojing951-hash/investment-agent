# R5 阶段证据覆盖面盘点与修复(2026-11-11,HKT)

> 轮次: autonomous-rd R5(分支 `dev/rd-r5-stage-coverage`)。
> 任务来源: RESUME R5 候选①「阶段A 指标快照缺席——views 引用→snapshot facts
> 映射缺口;不造数,先盘点缺口面再定接入或注记」(OPEN_ISSUES R1 发现项)。
> 纪律: 零手工造数;引擎只暴露本地已有数据+如实注记;C 层契约零变动。

## 一、盘点结论: 「16 指标快照缺席」分解为四类缺陷

17 份 VP sidecar 的 `stages.missing` 全量分解(阶段A 39 distinct/117 refs;
阶段B 11 distinct/23 refs;快照基准 `research_snapshot_20261110_v5`,103 facts):

| 类 | 缺陷 | 指标(阶段面) | 处置 |
|---|---|---|---|
| ① | 假设引用超出该观点 subjects 映射面——引擎把证据面钉死在 `view_metric_map.subjects`,面外引用永不出行也永不入 missing(build_vp 回退注记「快照无该指标事实」误导) | 阶段B: EEM/INDPRO/NDX/BEI_10Y/BRENT_F/DAX/SPX/UST_10Y(8 指标) | **已修**: 证据面=subjects 映射 ∪ 假设 metric_refs(`subject='hypothesis_ref'` 标记来源) |
| ② | 假设引用不在注册表(语义层 id 错配) | `CPI_YOY`(4 观点;注册表实有 `CPI`/`CORE_CPI`,US 面) | **已修注记**: missing 原因改精确「不在注册表(语义层映射缺口,Agent 层待修,禁猜)」;语义重指=Agent 层待办,引擎不猜 |
| ③ | mode A 事实面截断过杀——`verify_at_publish` approx_filtered 支把 `observation_date>publish` 的事实整个丢弃,尽管截断后 `series_store` 仍含 ≤publish 观测(市场日频指标典型: 15 指标有序列) | 阶段A: BRENT_F/WTI_F/IEF/NDX/SPX/DAX/NIKKEI225/VIX/EEM/GOLD_F/DXY/SHCOMP/TLT/USDJPY/USDCNY(15 指标有序列可恢复);UST_10Y/HY_OAS/BEI_10Y/TIPS_10Y/CN_LPR_1Y 等无序列=真缺席 | **已修**: 截断序列尾值近似 level(`level_source=series_tail_le_publish`,`quality_status` 压 DEGRADED,原观测日留 `fact_observation_date`);序列无 ≤publish 观测仍如实缺席;锚注记随行披露 |
| ④ | 真数据缺席(源端) | `BUND_10Y`/`BUND_2Y`(BBK RemoteDisconnected)、`CN_OMO_7D`(china 采集器 macro 段无 OMO 字段,源文件在场≠有数据)、`JP_CPI_TOKYO_YOY`(ECB/源站 504 类)、HY_OAS 族(ICE 授权窗) | 台账维护(`docs/P2_DATA_GAP_LEDGER.md`);不造数 |

## 二、修复实现(最小改动)

- `scripts/view_verifier.py`
  - `metric_evidence_table(..., extra_metric_ids=None)`: 假设引用并面;
    不在注册表/非 active 的进 missing 且原因精确化;去重+确定性(sorted)。
  - `verify(..., extra_metric_ids=None)` 透传;CLI 缺省 None=原契约。
  - `verify_at_publish(...)`: approx_filtered 支事实面尾值恢复(见类③);
    `level_source` 条件透传进证据行(既有行键序不变,零串改)。
- `scripts/view_plausibility.py`(build_vp)
  - 汇总假设 metric_refs 传入 A/B 两型;stage-A 行条件带 `level_source`;
    `generation_basis`/`generated_by`/`lineage` 记 R5 覆盖面升级。
- schema_version 维持 `1.1`(增量键,validate_vp 兼容);C 层
  (`view_label`/`hypotheses[].label`/mode C)零改动。

## 三、验收证据

### 3.1 新套件 `tests/test_rd_r5_stage_coverage.py` — 38 判定全绿

[1] 并面单元(合成 registry/map/snapshot): 并面出行/来源标记/去重/
    语义层缺口注记/非 active 注记/缺省契约/确定性(逐字节)。
[2] 截断尾值恢复(合成临时树,指标用真实注册表 id——interval_table 走
    模块级真实注册表): 尾值=level、obs=尾值日期、DEGRADED、level_source、
    1m 窗 end_date≤publish(无前视)、序列全>publish→真缺席、无序列→
    真缺席、obs≤publish 事实原样、锚注记披露、①×③联动、CLI 缺省契约。
[3] 真仓集成: SPX stage-A 恢复(VIEW-008)、INDPRO/EEM mode-B 并面
    (VIEW-009)、BUND_10Y 仍如实缺席(不造)、CPI_YOY 注记精确化(VIEW-001)。
[4] C 层零变动: 3 视点 dry-run ok+validate_vp 过、view_label/stage_summary.C
    与在档一致、dry-run 不落盘。

### 3.2 17 份 VP 全量重建对照(备份 `/tmp/r5_vp_before`)

- **既有行零丢失/零变动**(A/B 逐行 JSON 相等);C 层零变动。
- **新增 64 行**: 阶段A 51 行(15 指标)、阶段B 13 行(8 指标)。
- **7 条假设 stage 标签迁移,全部 INSUFFICIENT_EVIDENCE→有判**
  (A: 3 SUPPORTED + 3 CONTRADICTED;B: 1 CONTRADICTED)——方向全部是
  「获得判断」,无既有判断翻转。抽验语义正确(例: VIEW-003 hyp3
  「中东冲突推高能源价格」BRENT_F 尾值 100.58@2026-10-06 trailing 净上行
  vs hint=up → supports;hyp12「能源价格随时间回落」同窗净上行 vs hint=down
  → against)。方向全部来自机构明示文本(metric_ref/词表),窗界≤publish。

### 3.3 回归

- R1 套件 `test_rd_r1_vp_stages.py`: 52 判定绿(无回归)。
- R2/R3 编排器套件与全套回归: 见 ITERATION_LOG 本轮行(全套 exit 0)。

## 四、新发现(登记,不在本轮修)

1. **[P0 观察] CN_CPI_YOY=0.0@2025-08-09 / CN_PPI_YOY=-3.6@2025-08-09**
   (快照 v5,DEGRADED): akshare_jin10 源 2025-08 后停更,采集器持续写
   最后值;两值同日期且周六(疑似发布日解析错位)。**证据引擎仍采信该事实**
   (DEGRADED 只披露不拦截)——VIEW-003/007 的 CN_CPI_YOY 证据行建立其上。
   处置: 下一轮采集器修复(jin10 通道换源/日期解析)+新鲜度政策议
   (DEGRADED+陈旧>N 月是否拦截出判)。修复需网络验证,本轮无头环境禁外发。
2. **CN_OMO_7D 采集缺口属「字段从未采集」**而非提取遗漏: china 采集器
   macro 段仅 LPR/CPI/PPI/PMI/新增贷款——gate_a 的「来源文件在场而指标
   缺席(采集遗漏)」注记对此指标误导,待采集器补 OMO 端点(akshare)。
3. CPI_YOY(US) 语义重指 = Agent 层待办(编排层 v1.0 映射质量),引擎禁猜。
