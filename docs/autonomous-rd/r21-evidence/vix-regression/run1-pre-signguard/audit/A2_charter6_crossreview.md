# Charter 6 架构交叉审查(A2): B 实现忠实度 + 工程质量

- 审查人: A2(审计① 作者) | 范围: dev/deep-macro-v1, 0f92151..d661deb(5 commit, 48 文件 +3314/−130)
- 方法: diff 逐文件读 + 关键数值独立重算(窗口默认值/回落/闰日/保留策略边界/coverage 语义)+ 6 关键套件实跑
- 只读审查,未改任何代码;红线遵守(未动 LIVE/未合并 main/零付费 API)

## 总判定: **PASS-WITH-DEFERRED**(4 项延期,无阻断)

关键套件实跑: test_charter6_p0_windows / p1_missing_series / p2_shiller / p4_analog / e2e_frozen14 / oss_product 全部 rc=0。B 自报 109/109 与抽查一致。

---

## 一、8 项重点复核(逐项判定)

### 1. ECB_DFR 走 ea-collector 而非 FRED —— 判定: **取舍成立**
- 实况: ea 通道 startPeriod 2024→1999(ECB Data Portal 全史),policy_rates 通道增 keep_series 全行入 series 节;snapshot_builder.merge_series_sections 以 **registry source 权属门**(m.source==collector)收 series_store——若改走 FRED ECBDFR,registry source 须翻成 macro_collector,macro_/ea_ 两族冻结 fixture 同时翻转。
- 判定理由: ①我的规格原文即"双路取一即可"(audit① §2#2),ea 路满足全史+免Key+单解析器增量;②单指标单权威源=项目既有身份纪律(merge 门本身以此设计),FRED 双源反而引入"两源谁的值算数"的新问题;③冻结面稳定性是真实工程成本。**非偏差,是合理选择。**
- 附带核实: BBK 断供修复=仅网络层异常重试(0/2/5s 退避),HTTPError 不重试不放大请求面——正确;BUND 历史化未做(audit① 标 P2#12,本轮不在)。

### 2. jp_market 窗口参数化虚设 —— 判定: **部分成立,列延期①**
- 实况: jp 的 NIKKEI225 走 FRED fredgraph(非 yfinance),SERIES_WINDOW=251 硬截断(jp_market_collector.py L47/225),注释依据="对齐既有 global 档"。
- B 理由"已在既有窗口内"不完整: global 默认已 10y,该对齐依据已过期——SPX 2510 点 vs NIKKEI225 251 点的深度不对称。非阻断(六维 analog 向量以 US 序列为输入;NIKKEI 服务跨经济体页),但属遗留不一致。
- **延期①: SERIES_WINDOW 扩到与 global 窗口同源(如 ~2510 或读 GLOBAL_HISTORY_PERIOD 派生),或在 docstring 显式声明不对称为有意。**

### 3. 'active' 语义收紧(!= 'deprecated' → == 'active') —— 判定: **正确,无连锁漏算**
- 独立核查 registry 现状: 106 条 = 104 active / 1 unavailable(SPX_PB) / 1 deprecated(REAL_SHORT),**无缺 status 键、无其他状态词**——语义变化只影响 SPX_PB 一条(旧码会把"不可得"虚报为已覆盖,新码不报)。
- 方向正确且与其他消费者对齐: fe.snapshot_quality_grade 与 rp.active_registry_metrics 本就按字面 'active' 过滤(registry_semantics L172-175 注释即为此锁)——旧 assembler 是**多算**,非少算。
- 消费面核查: reg_counts 仅进数据包 markdown 覆盖行(data_assembler L304),无数值断言依赖旧口径;STATUS_VALUES/EVOLUTION_LEGAL_STATUS 同步 +unavailable,词汇锁闭合。**无漏算无多算。**

### 4. Shiller 采集器 code-only —— 判定: **代码路径正确;live 首跑列延期②**
- 逐行审读(scripts/shiller_collector.py): 表头驱动定位(前15行找'date'列,不按位置猜列);CAPE 列=表头恰为'cape'('tr cape'/'cape10' 变体字典键不同天然排除);P/E 双路(源列直用/逐行 P÷E,e≠0 守卫,meta.columns_used 登记口径);日期 YYYY.MM→月首日(round 吸浮点尾差,月份 1-12 校验,布尔守卫);重复月保留最后;缺格如实缺席不插值;全序列缺席→exit 1 不产空壳;原子写(tmp+os.replace);source_version(sheet/表头行/首末月)随档落盘;源注记含 latest_vintage_asof_collected(呼应 audit① §3.1 披露)。
- 依赖: xlrd>=2.0.1(2.x 专读 .xls,与 ie_data.xls 匹配);requirements.txt 与 CI workflow 同步登记 ✓。
- fixture 覆盖面核查: **三条解析路径全覆盖且预期值独立手算非自证**——min=P÷E 计算路(7/8 值手算+缺月缺席+重复月末值+TR CAPE 排除)、pe_col=直用列路(设计成"若误算 P÷E 则值不同,可证")、nocol=无估值列诚实缺席;另含非 xls 字节/exit-1/原子写/快照 lift/权属门/质量 WARN。
- **延期②: 对 Yale 真实 URL 的首次实跑未发生(步骤9 code-only)。上线前须 live 跑一次验证表头实形态(容错设计已备,但未实证);run_weekly 已置其为非关键,源失败只降级不阻塞——风险受控。**

### 5. 保留策略(data_retention.py) —— 判定: **实现正确**(独立模拟验证)
- 独立重算(手工构造 2026-11-09 时点 90 天窗): cutoff=2026-08-11,**边界日档保留**(obs≥cutoff kept);cutoff 前按 (prefix, ext, YYYYMM) 每月最后一份 gzip 入 data/daily/archive/、其余删除;不同前缀同月独立归档;anchors_ 等研究层文件正则不匹配=untouched;`*_v2.json` 变体不匹配不动;二次运行幂等(已归档月份零动作);空目录零动作报告。
- data/research 永不触碰(不同目录);data/ 整体 gitignored→archive/ 一致忽略;dry_run 只报告。全量重拉可重建=删除无损失,与 audit① §1.3 结论自洽。

### 6. P0 窗口默认值与 env 回落 —— 判定: **PASS,一处小缺口列延期③**
- 独立重算: MACRO_HISTORY_YEARS——缺省→10y;15→2011 起;'abc'→告警回落 10y;'0'→clamp 至 1 年;闰日 2028-02-29→2018-03-01(窗口多含一天,口径无影响)。旧环境无变量=安全默认 10y(首次采集变慢变大,属预期行为变化)。GLOBAL_HISTORY_PERIOD——缺省/空白→'10y';显式传参优先(测试缝)。
- auto_adjust=True 显式固定(audit① §3.2 要求)✓。
- **延期③: GLOBAL_HISTORY_PERIOD 不做合法性校验,任意字符串(如手误)直通 yfinance→关键步骤1整体失败;macro 侧有校验回落而 global 侧没有,不对称。建议补同款白名单校验(如 ^(1|2|5|10)y$|^max$)或非法回落+告警。**

### 7. fixt 8 通道 + e2e_frozen14 名单变化 —— 判定: **合法基线演进,非弱化;一处不一致列延期④**
- 实质: 名单仍为**精确等值断言**(锁的强度不变),变化来源真实——shiller 新通道 fixture 已造(SPX_CAPE/PE 在场→不入缺席名单);US_REAL_GDP 新登记而 fixture 宏观面未造 GDPC1→如实入缺席名单(12→13 项,协调方口径"14→13"有误,实为 12→13)。B 注释"真实采集后即补齐"成立。
- 弱化判定: 否——精确锁保留,新条目如实反映 fixture 内容,且 shiller 反向证明了"fixture 补齐则名单收缩"的方向正确。
- **延期④: 与 shiller 处理不一致——GDPC1 未进 fixture 宏观 payload(齐备日不再宏观齐备)。建议 B 给 fixture macro 面加 US_REAL_GDP 序列并把名单收回 12 项,恢复"齐备研究日"语义。**

### 8. 全量重拉语义未变 —— 判定: **确认无增量合并**
- macro 仍每次 get_series 全窗口重拉+整档覆盖写(diff 未触取数循环);global 仍全量 download;新增的只有"删旧档"(retention),无任何"读旧档 append/merge"逻辑。与 audit① §1.3"保持全量重拉,不做增量合并"完全一致。

---

## 二、规格忠实度对照(audit① §4 清单 → B 实现)

| P0 | 状态 |
|---|---|
| #1 macro 窗口参数化 | ✅(含闰日/校验回落) |
| #2 global+jp 窗口参数化 | ✅global / ⚠️jp 延期① |
| #3 长序列下游回归 | ✅(B 109/109+我抽查 6 套件;compare/correlation 既有 --start/--end 与月网格不受全长影响) |
| #4 保留策略 | ✅(90天全量+月度gzip,边界/幂等/研究层免疫均独立验证) |
| P1 #5 GDPC1 | ✅(FRED_SERIES+quarterly 频率词汇+QoQ/YoY 派生分支+registry billion_usd) |
| P1 #6 日政策利率全史 | ✅(fredgraph 全行解析→series 节→snapshot merge) |
| P1 #7 ECB_DFR 全史+BUND 修复 | ✅(ea 路,见判定1;BBK 重试✓,BUND 历史化=P2#12 未做,符合排期) |
| P1 #8 BTC 深度 | ✅(随 global 窗口自动获得) |
| P2 #9 Shiller CAPE | ✅ 代码+fixture(延期② live 首跑) |
| P2 #10 SPX_PB 不可得登记 | ✅(status=unavailable+coverage 语义收紧+词汇锁同步) |
| P2 #11 CN SH_PE 历史 | ❌ 未做(audit① 标 P2,与案例B 解耦,B 自报偏差清单含此项?) |
| P2 #12 JGB 全史/EA HICP/CN 宏观历史化 | ❌ 未做(P2 后段,排期外) |
| P3 #13 revision_semantics 披露 | ✅ 部分(shiller 源注记已带 latest_vintage_asof_collected;registry 级通用字段未加) |
| P3 #14 ALFRED | 未做(条件触发项,正确) |
| P3 #15 catalog 别名去重 | 未做(卫生项) |

超出我规格的部分(P4 analog 引擎/P5 Skill 修订): 架构与泄漏防护属引擎侧评审域,非本审计范围;其 593 行测试套件实跑 rc=0,数据消费面(六维向量输入=US_REAL_GDP/SPX_CAPE 等新序列)接线经 snapshot merge 门正确隔离(权属校验)。

## 三、独立重算记录(供复核)

1. macro_observation_start: 2026-11-09→'2016-11-09'(默认)/env=15→'2011-11-09'/'abc'→告警+'2016-11-09'/'0'→'2025-11-09'/2028-02-29→'2018-03-01' —— 全部与实现一致。
2. retention 边界: now=2026-11-09, keep=90 → cutoff=2026-08-11;08-11/08-12 保留,08-10 归档(当月最后一份),跨前缀同月独立,anchors untouched,幂等 —— 与实现一致。
3. registry: 106 条=104/1/1,无缺失 status —— 'active' 收紧仅影响 SPX_PB 一条显示计数。
4. 首次模拟中我方两次日期手算错误(90 天窗),模块两次均正确——边界行为以模块为准。

## 四、结论

**PASS-WITH-DEFERRED**。B 对 audit① 数据覆盖规格的落地忠实(16 项对照 11✅/1 部分/4 排期外),两处自报偏差(ECB_DFR 路线/jp 虚设)一判合理一判部分合理,工程质量(原子写/权属门/诚实缺席/独立手算断言/幂等重入)高于规格要求。四项延期均不阻断合并与案例B 启动:

- 延期① jp SERIES_WINDOW 与 global 10y 对齐(或声明有意不对称)
- 延期② Shiller Yale 源 live 首跑实证(上线前)
- 延期③ GLOBAL_HISTORY_PERIOD 合法性校验+回落(补 macro 同款)
- 延期④ fixture macro 面补 US_REAL_GDP 序列,frozen14 名单收回 12 项
