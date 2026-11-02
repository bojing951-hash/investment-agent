# IA-DATA-W2 指标覆盖全量审计报告(只读诊断)

> 工作包: IA-DATA-W2(合同 IA-DATA-W2-AC-v1.0, FROZEN 2026-11-02)
> 执行分支: `dev/data-coverage`(基点 `7cbef4c9` = origin/dev/data-inventory 实取尖端)
> 工具: `scripts/metric_coverage_audit.py`(仅标准库,对 registry 与数据目录只读)
> 本报告为**只读诊断**: 发现问题、如实登记,**未实施任何修复**(修复属数据线第2包,须待 R007 完成后另立合同)。

---

## 一、审计窗口构成(以 baseline 清单为准)

baseline 取得时点 **2026-11-02T03:14:33Z–03:14:44Z**(先于分支创建与一切开发动作,证据包 `baseline_data_inventory_tool.txt` + `baseline_shasum_raw.txt`):

窗口 = `data/daily/` 全部现存 12 文件;其中 8 个通道 JSON 进入工具审计窗口,4 个 `.md` 为同源摘要(非任何 registry 指标的数据面,不入窗):

| 文件 | sha256 | size |
|---|---|---|
| china_20261101.json | 74e043083f86c6e672b243f1d7b78de7ff11c0a298dc203c097332fa4c37ad08 | 28681 |
| china_20261102.json | e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | 28681 |
| global_20261101.json | c8965a6a979df78148e321d8f381945a2add53ba63d79322a92f613dfe2cbd05 | 380047 |
| global_20261102.json | 624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 380055 |
| macro_20261101.json | ed02b8c30a9206982bcd414b0d73f51bf24f00772c9dd91e29ccbb3b0be8b4bf | 290370 |
| macro_20261102.json | 6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 288933 |
| rate_economy_20261101.json | 33ceb929927c9c0a33b3e47a1eafc24d4c86e580fa327cd41ce765167ecaaa68 | 5691 |
| rate_economy_20261102.json | 4be746da89c6ca26b3697b4e25033cfe62269a3f295f3542f9d56a795350d598 | 5691 |
| global_20261101.md / global_20261102.md / rate_economy_20261101.md / rate_economy_20261102.md | 见 baseline 清单(a4758cf7… / 90995e5d… / 78cb3b8f… / 0e6bac79…) | 各 2029/1854 |

registry 实取: `config/metric_registry.json` sha256=`60ef058a2fb1e12cb0786f0d4b977e3e084c0ca4aa7798debdbe0266b18097ed`, version 2.0.0, **metrics 条目数 = 81**(与交接口径"约 81"一致,无出入), metric_id 零重复; status: active 80 + deprecated 1(REAL_SHORT)。

## 二、主状态分类学与判定口径

分类学(N/S/B/C/U)定义见合同;判定口径 = 工具机械状态 → 主状态的映射规则(详见 DELIVERY §分类规则),要点:

1. 机械状态 `PRESENT`/`DERIVED_READY` → **N**(判定与工具机械事实零偏离,无需代码侧证据)。
2. 机械状态 `PRESENT_NULL`/`PATH_NULL`(引擎路径在档但值为 null)→ **S**;`KEY_ABSENT` 且容器在档(采集已尝试,失败路径不写键)→ **S**。S 判定依赖采集端"失败即不写键"的代码侧事实,逐指标附 文件:行。
3. **B 优先于 S 的裁决规则**: 当映射断裂在代码侧独立成立(引擎期望的键在采集端**任何成功路径上都不写**——即令当日源端成功,引擎仍取不到值),主状态判 **B**,当日源端失败记为次级现象(S 层)。本窗 MARGIN_BAL、SH_PE 适用(与 R008 双层/三层断点诊断一致)。
4. 通道文件缺席或容器从未在档 → **C**;本窗 4 通道文件均在、容器均在,无 C。
5. 离线无法定夺 → **U**;本窗 81 项全部可由数据面机械事实+代码侧实读定夺,**U = 0 项**。

工具对窗口的机械计数(证据包 `audit_real_data_daily.json`): `PRESENT 66 / DERIVED_READY 5 / PATH_NULL 5 / KEY_ABSENT 5`,合计 81。

**主状态计数: N=71 / S=8 / B=2 / C=0 / U=0(合计 81 = registry 条目数)。**

## 三、全量覆盖表(81 行 = registry 全部指标;每指标恰一个主状态)

| 指标ID | 主状态 | 工具机械状态 | 数据侧证据(最新档@档日 sha256) | 观测日 | 值 | 代码侧证据/附注 |
|---|---|---|---|---|---|---|
| SPX | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 7580.07 |  |
| NDX | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 28384.85 |  |
| RUT | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 2811.84 |  |
| VIX | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 19.42 |  |
| NVDA | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 204.64 |  |
| AAPL | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 344.63 |  |
| MSFT | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 521.91 |  |
| TLT | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 81.84 |  |
| IEF | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 91.76 |  |
| SHY | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 81.7 |  |
| HYG | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 77.43 |  |
| LQD | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 104.27 |  |
| DXY | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 101.88 |  |
| EURUSD | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 1.12 |  |
| GBPUSD | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-11-01 | 1.34 |  |
| USDJPY | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 157.8 |  |
| USDCNY | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-11-01 | 6.64 |  |
| GOLD_F | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 3898.9 | 文件键 GOLD→注册表 GOLD_F(fact_engine.py L244-245) |
| SILVER_F | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 49.28 | 文件键 SILVER→SILVER_F(同上) |
| WTI_F | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 104.12 | 文件键 WTI→WTI_F(同上) |
| BRENT_F | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 113.43 | 文件键 BRENT→BRENT_F(同上) |
| GLD | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 355.78 |  |
| USO | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 168.83 |  |
| EEM | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 61.04 |  |
| EZU | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 65.16 |  |
| FEZ | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 65.03 |  |
| EWU | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 47.83 |  |
| EWG | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 41.88 |  |
| EWJ | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 92.91 |  |
| INDA | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 47.72 |  |
| FXI | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-30 | 33.08 |  |
| BTC | N | PRESENT | global_20261102.json@20261102 sha256=624a9b9e1523ad522b351414ec2f8077281ce72bb231e40e6d47fe5cedc91db8 | 2026-10-31 | 77434.75 | 观测日=完整UTC日收(W5-FIX2口径) |
| UST_2Y | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 4.61 |  |
| UST_5Y | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 4.78 |  |
| UST_10Y | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 4.98 |  |
| UST_30Y | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 5.32 |  |
| HY_OAS | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 3.26 |  |
| BB_OAS | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 1.94 |  |
| B_OAS | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 3.32 |  |
| CCC_OAS | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 13.25 |  |
| IG_OAS | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 0.89 |  |
| TIPS_5Y | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 2.31 |  |
| TIPS_10Y | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-29 | 2.63 |  |
| BEI_5Y | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-30 | 2.46 |  |
| BEI_10Y | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-30 | 2.34 |  |
| CURVE_2S10S | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-30 | 0.38 |  |
| FED_FUNDS | S | KEY_ABSENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | - | null | macro_collector.py L201-226(逐系列try/except,异常仅打印不写键); 月频;20261102档键缺席=当日FRED采集失败(macro_20261101.json在场: FED_FUNDS=3.75@2025-09-01);快照按文件粒度回退(snapshot_builder.py L249-261)无按键回退 |
| CPI | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 336.298 | 月频正常节奏 |
| CORE_CPI | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 338.896 | 月频正常节奏 |
| CORE_PCE | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 130.902 | 月频正常节奏 |
| UNEMPLOYMENT | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 4.2 | 月频正常节奏 |
| NFP | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 159044.0 | 月频正常节奏 |
| NFP_MOM_K | N | DERIVED_READY | 依赖: NFP→macro_20261102.json@20261102(sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e) | - | (派生: NFP) | 引擎序列驱动派生(fact_engine.py L490-499);NFP序列长度21 |
| AHE | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 37.81 | 月频正常节奏 |
| WTI_SPOT_M | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 97.31 | 文件键 WTI→WTI_SPOT_M(fact_engine.py L281);月频,观测2026-09-01(正常发布节奏) |
| UMCSENT | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 48.1 | 月频正常节奏 |
| RSAFS | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 745021.0 | 月频正常节奏 |
| INDPRO | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-09-01 | 103.9506 | 月频正常节奏 |
| ICSA | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-10-24 | 194000.0 | 周频正常节奏 |
| DFF | N | PRESENT | rate_economy_20261102.json@20261102 sha256=4be746da89c6ca26b3697b4e25033cfe62269a3f295f3542f9d56a795350d598 | 2026-10-29 | 3.88 |  |
| DFEDTARU | N | PRESENT | rate_economy_20261102.json@20261102 sha256=4be746da89c6ca26b3697b4e25033cfe62269a3f295f3542f9d56a795350d598 | 2026-11-01 | 4.0 |  |
| DFEDTARL | N | PRESENT | rate_economy_20261102.json@20261102 sha256=4be746da89c6ca26b3697b4e25033cfe62269a3f295f3542f9d56a795350d598 | 2026-11-01 | 3.75 |  |
| ZQ_F1_PRICE | N | PRESENT | rate_economy_20261102.json@20261102 sha256=4be746da89c6ca26b3697b4e25033cfe62269a3f295f3542f9d56a795350d598 | 2026-10-30 | 96.12 | 观测日2026-10-30(次级现象:滞后于档日,新鲜度由freshness_policy另裁) |
| SHCOMP | S | KEY_ABSENT | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | china_market_collector.py L108-150(逐代码try/except,失败不写键);L546(容器恒写);fact_engine.py L340-347 |
| SZCI | S | KEY_ABSENT | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | china_market_collector.py L108-150;L546;fact_engine.py L340-347 |
| CHINEXT | S | KEY_ABSENT | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | china_market_collector.py L108-150;L546;fact_engine.py L340-347 |
| HSI | N | PRESENT | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | 2026-10-30 | 23294.42 |  |
| HSCEI | N | PRESENT | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | 2026-10-30 | 7862.22 |  |
| HSAHP | N | PRESENT | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | 2026-10-30 | 132.49 | 观测日2026-10-30(次级现象:滞后于档日,新鲜度由freshness_policy另裁) |
| SB_FLOW | S | PATH_NULL | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | china_market_collector.py L258-298(失败return None);fact_engine.py L357-363 |
| MARGIN_BAL | B | PATH_NULL | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | fact_engine.py L364-366(期望margin.balance) vs china_market_collector.py L314-319(成功只写rzye/rqye/rzye_billion;全文件无balance键);fetch_margin L305-326(裸except L322-323) |
| SH_PE | B | KEY_ABSENT | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | fact_engine.py L367-369(期望扁平valuation.pe) vs china_market_collector.py L344-351(嵌套pe_ttm)+L88-92(VALUATION_INDICES无000001.SH;A_SHARE_INDICES L42-49含之) |
| SH_AMOUNT | S | PATH_NULL | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | china_market_collector.py L359-427(双方案失败return None);fact_engine.py L375 |
| SZ_COMPONENT_AMOUNT | S | PATH_NULL | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | china_market_collector.py L359-427;fact_engine.py L377-380 |
| CN_TOTAL_TURNOVER | S | PATH_NULL | china_20261102.json@20261102 sha256=e50424987780e0e99167954bef8bf0bae7508968cd53b539e056d1f36eacb953 | - | null | china_market_collector.py L359-427;fact_engine.py L381-391 |
| REAL_10Y | N | DERIVED_READY | 依赖: UST_10Y→macro_20261102.json@20261102(sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e), BEI_10Y→macro_20261102.json@20261102(sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e) | - | (派生: UST_10Y+BEI_10Y) | fact_engine.py L478;macro档顶层derived亦有采集端同值(2.64),引擎读侧面不消费该字典 |
| REAL_5Y | N | DERIVED_READY | 依赖: UST_5Y→macro_20261102.json@20261102(sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e), BEI_5Y→macro_20261102.json@20261102(sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e) | - | (派生: UST_5Y+BEI_5Y) | fact_engine.py L479 |
| REAL_SHORT | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | - | 2.15 | registry status=deprecated(replaced_by REAL_5Y);值存于macro顶层derived字典(macro_collector.py L257-275);normalize_macro不读该字典、compute_derived不派生该指标(fact_engine.py L275-298/L462-500)——引擎事实面无此指标,按registry设计弃用 |
| HY_IG_DIFF | N | DERIVED_READY | 依赖: HY_OAS→macro_20261102.json@20261102(sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e), IG_OAS→macro_20261102.json@20261102(sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e) | - | (派生: HY_OAS+IG_OAS) | fact_engine.py L480;macro档顶层derived亦有采集端同值(2.37) |
| ZQ_IMPLIED_AVG | N | DERIVED_READY | 依赖: ZQ_F1_PRICE→rate_economy_20261102.json@20261102(sha256=4be746da89c6ca26b3697b4e25033cfe62269a3f295f3542f9d56a795350d598) | - | (派生: ZQ_F1_PRICE) | fact_engine.py L482-489;依赖ZQ_F1_PRICE(观测日2026-10-30) |
| JTSJOL | N | PRESENT | macro_20261102.json@20261102 sha256=6de0e59a7ad5af5f38a36d3369d6f4440f709e124f657823cf15874e52575d2e | 2026-08-01 | 7079.0 | 月频正常节奏(JOLTS发布约5周滞后) |

**内部一致性**: 表行数 81 = registry 条目数 81;每行恰一个主状态;非 N 集合 = {FED_FUNDS, SHCOMP, SZCI, CHINEXT, SB_FLOW, SH_AMOUNT, SZ_COMPONENT_AMOUNT, CN_TOTAL_TURNOVER}(S×8) ∪ {MARGIN_BAL, SH_PE}(B×2) = 债务清单成员(§四),不多不少。

**与工具机械事实的偏离登记(W2-AC-01)**: 偏离恰 2 处——MARGIN_BAL(机械 PATH_NULL→主状态 B)与 SH_PE(机械 KEY_ABSENT→主状态 B),均依 §二规则3 以代码侧证据(行内已附)判 B,次级现象(当日源端亦失败)在行内附注。其余 79 行主状态与机械事实零偏离。

## 四、数据质量债务清单(= 覆盖表全部非 N 指标,恰 10 项)

| # | 指标 | 主状态 | 断点摘要(证据见 §三 行内) | 处置方向(建议性) |
|---|---|---|---|---|
| 1 | MARGIN_BAL | B | 引擎期望 margin.balance,采集端任何成功路径只写 rzye/rqye/rzye_billion(全文件无 balance 键);当窗两日 margin:null=源端亦失败(fetch_margin 裸 except 吞异常) | 数据线第2包(键口径对齐;待 R007 后另立合同) |
| 2 | SH_PE | B | 引擎期望扁平 valuation.pe,采集端写嵌套 valuation[code].pe_ttm,且 VALUATION_INDICES(L88-92)无 000001.SH 身份(A_SHARE_INDICES L42-49 含之);当窗两日 valuation:{}=源端亦失败 | 数据线第2包(扁平口径+上证身份;待 R007 后另立合同) |
| 3 | SHCOMP | S | a_share_indices 容器在档但为空 {}(窗口两日同态)——A股指数通道(Tushare)逐代码失败不写键 | 数据线第2包(通道排查: token/积分/网络) |
| 4 | SZCI | S | 同上(399001.SZ 键缺席) | 同 SHCOMP |
| 5 | CHINEXT | S | 同上(399006.SZ 键缺席) | 同 SHCOMP |
| 6 | SB_FLOW | S | southbound:null(窗口两日)——moneyflow_hsgt 失败 return None;映射口径本身一致(引擎 south_money/100) | 数据线第2包(通道排查) |
| 7 | SH_AMOUNT | S | turnover:null(窗口两日)——Tushare/akshare 双方案失败 return None | 数据线第2包(通道排查) |
| 8 | SZ_COMPONENT_AMOUNT | S | 同 SH_AMOUNT(sz_amount_billion 不可达) | 同 SH_AMOUNT |
| 9 | CN_TOTAL_TURNOVER | S | 同 SH_AMOUNT(sh+sz 双路径均不可达) | 同 SH_AMOUNT |
| 10 | FED_FUNDS | S | macro_20261102 键缺席=当日 FRED 单系列失败;macro_20261101 在场(3.75@2025-09-01)。月频指标,单日缺席≠缺期;但按最新档建快照将缺该事实(无按键回退) | 观察项(若连续多日缺席→数据线第2包排查 FRED 瞬时失败重试) |

**超出 R008 已登记范围的新发现**: R008 只登记了 margin/valuation 两个断点;本轮全量审计发现 china 通道当窗**大面积源端失败**——12 个 china 指标中 8 个无值(a_share_indices 整体空、southbound/turnover 为 null),仅 HSI/HSCEI/HSAHP 有数据。这是数据线第2包的范围输入,不是本轮修复面。

## 五、U 项清单(离线不可定夺)

**无(0 项)。** 全部 81 项均可由数据面机械事实(工具实跑)+采集端/引擎代码侧实读离线定夺;无需外部源文档或生产侧信息。

## 六、只读声明

1. 本轮**零修复实施**: 未改任何 collector/registry/fact_engine/snapshot_builder/freshness_policy/既有测试/既有文档(白名单 4 新文件之外零改动,`git diff --name-status 7cbef4c9..<尖端>` 可验)。
2. `data/daily/` 只读锚定: baseline(2026-11-02T03:14Z)与 closing(见证据包)逐字节一致,12 文件零差异。
3. LIVE 生产目录零写入(三项只读取证见证据包 `live_isolation_checks.txt`)。
4. 本报告判定以工具机械事实为基础;偏离处(恰 2 处 B 判定)逐指标附代码侧证据(文件:行),供审计独立重演。
