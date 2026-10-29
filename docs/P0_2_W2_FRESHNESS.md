# IA-P0-2-W2 81项数据时效政策矩阵

- 生成: 2026-10-29(程序逐字段生成,生成器与本文件同commit提交说明见交付报告);机器可读版: `P0_2_W2_FRESHNESS.json`
- 单一生效来源: `config/metric_registry.json` `freshness.max_calendar_lag_days`(经`scripts/freshness_policy.py`构建;Gate A `fact_engine.validate_fact` 与 Gate B `data_validator` 消费**同一份**)
- 三问分离: A已观测(完整ISO真实日期且≤as_of) / B点时已发布(仅对真实release_date作答,缺失=RELEASE_UNKNOWN不伪造) / C新鲜(as_of−obs≤已批准窗口)

## 1. 审批记录(两轮)

| 轮 | 决策 |
|---|---|
| 第1轮(2026-10-29) | 月频13项=45; 行情与日频风险资产44项=5; 特殊日频BTC=2/DFF=10/SH_PE=10; 政策目标区间DFEDTARU/DFEDTARL=45 |
| 第2轮(2026-10-29) | 月频13项45→60(修正:BEA/EIA/G.17系正常发布滞后可达~60天,45会误判按时数据过期); 中国大陆日频8项5→10(修正:春节/国庆休市8~9天,5/7天在节后首日必误报);HK 2项维持5; MARGIN_BAL 7→10(与大陆日频同一休市日历,一致化) |

**总量**: 81项 | 政策分类: APPROVED_ROUND1=7 / APPROVED_ROUND2=1 / APPROVED_ROUND2_CORRECTED=21 / NO_CONFLICT=52 | Gate A窗口: 收紧49/放宽13/不变19 | Gate B规则纠正(窗口或频率误判): 33项

## 2. 修正的两处第一轮算术错误(为何45/5不成立)

1. **月频45**: 月度序列观测日戳在**月首**,而BEA(CORE_PCE)/EIA(WTI_SPOT_M)/Fed G.17(INDPRO)的正常发布在次月中下旬至月末——观测滞后合法可达~60天;45会把**按时发布**的数据在每月下旬误判过期。统一60天: 覆盖最慢正常发布,超60≈连缺一期以上。BLS系(CPI/就业/零售)次月中旬发布(~38-45天)亦在60内,代价是采集缺口的发现比45晚约2周。
2. **中国日频5**: A股春节/国庆休市8~9天,节后首个交易日观测滞后8~9天;5(乃至7)必在节后首日误报。大陆8项10天;HK无此量级休市簇维持5。

## 3. 焦点指标(指令§5.2强制15项)

| 指标 | 频率 | 生效窗口(旧引擎→新) | 旧Gate B | 发布/观测证据 |
|---|---|---|---|---|
| SPX | daily | 5(7→) | 5/daily | 美股日频;5自然日≈一个交易周,覆盖周末+单个假日;连续2日以上采集失败即披露 |
| BTC | daily | 2(7→) | 5/daily | 7×24全年无休市,每日必有观测;窗口2=仅容忍1天采集空窗(旧7过宽,加密资产静默缺数7天不披露) |
| UST_10Y | daily | 7(7→) | 7/daily | 美债日频: 窗口7(注册表=旧引擎,零冲突) |
| CPI | monthly | 60(92→) | 45/monthly | BLS CPI: 参考月次月中旬(~10-15日)发布; 观测月首戳→最长正常发布滞后~45天 |
| CORE_PCE | monthly | 60(92→) | 45/monthly | BEA PCE价格指数: 参考月次月末(~27-30日)发布; 最长正常发布滞后~60天——45天窗会在每月下旬误判按时数据过期(第二轮修正依据) |
| UNEMPLOYMENT | monthly | 60(92→) | 45/monthly | BLS就业形势报告: 次月第一个周五(~31-37天) |
| NFP | monthly | 60(92→) | 45/monthly | BLS就业形势报告: 次月第一个周五(~31-37天) |
| ICSA | weekly | 16(16→) | 16/weekly | DOL初请失业金: 周四发布当周观测(发布滞后~0-3天) |
| DFF | daily | 10(7→) | 45/monthly | 日度有效利率T+1发布(FR纽约联储);10天覆盖多假日簇(旧7在假日簇+单次采集故障时误报) |
| DFEDTARU | daily | 45(7→) | 45/monthly | FOMC目标区间上限: 8次会议/年(~6-7周间隔),区间仅会后变动;45天≈会期间隔,超期=跨会议未更新采集(旧日频7频繁误报DEGRADED) |
| DFEDTARL | daily | 45(7→) | 45/monthly | 同DFEDTARU(区间下限) |
| ZQ_F1_PRICE | daily | 5(7→) | 45/monthly | 30天联邦基金期货: 日频交易价格;窗口5;注意曲线点锚点(rate_economy.fed_funds_futures.<i>.price)由sb直接构造、不带obs_date=无法判龄(如实警告,非本轮修复项) |
| SHCOMP | daily | 10(7→) | 5/daily | 交易日观测(收盘价/当日值) |
| MARGIN_BAL | daily | 10(7→) | 7/daily | 交易日观测(收盘价/当日值) |
| SH_PE | daily | 10(7→) | 7/daily | 上证市盈率日频,估值数据通道偶发延迟;10天缓冲(旧7误报) |

## 4. 全81项清单

| 指标 | 频率 | 改前(注册/引擎/GB) | 生效 | 政策状态 | Gate A影响 |
|---|---|---|---|---|---|
| SPX | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| NDX | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| RUT | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| VIX | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| NVDA | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| AAPL | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| MSFT | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| TLT | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| IEF | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| SHY | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| HYG | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| LQD | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| DXY | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| EURUSD | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| GBPUSD | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| USDJPY | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| USDCNY | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| GOLD_F | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| SILVER_F | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| WTI_F | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| BRENT_F | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| GLD | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| USO | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| EEM | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| EZU | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| FEZ | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| EWU | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| EWG | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| EWJ | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| INDA | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| FXI | daily | 5/7/5(daily) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| BTC | daily | 2/7/5(daily) | **2** | APPROVED_ROUND1 | 收紧7→2天: 滞后3~7天的事实从有效变为DEGRADED披露 |
| UST_2Y | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| UST_5Y | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| UST_10Y | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| UST_30Y | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| HY_OAS | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| BB_OAS | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| B_OAS | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| CCC_OAS | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| IG_OAS | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| TIPS_5Y | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| TIPS_10Y | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| BEI_5Y | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| BEI_10Y | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| CURVE_2S10S | daily | 7/7/7(daily) | **7** | NO_CONFLICT | 不变(7天) |
| FED_FUNDS | monthly | 45/92/45(monthly) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| CPI | monthly | 45/92/45(monthly) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| CORE_CPI | monthly | 45/92/45(monthly) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| CORE_PCE | monthly | 45/92/45(monthly) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| UNEMPLOYMENT | monthly | 45/92/45(monthly) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| NFP | monthly | 45/92/45(monthly) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| NFP_MOM_K | monthly | 45/92/7(daily) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| AHE | monthly | 45/92/45(monthly) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| WTI_SPOT_M | monthly | 45/92/7(daily) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| UMCSENT | monthly | 45/92/7(daily) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| RSAFS | monthly | 45/92/7(daily) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| INDPRO | monthly | 45/92/7(daily) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |
| ICSA | weekly | 16/16/16(weekly) | **16** | NO_CONFLICT | 不变(16天) |
| DFF | daily | 10/7/45(monthly) | **10** | APPROVED_ROUND1 | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| DFEDTARU | daily | 45/7/45(monthly) | **45** | APPROVED_ROUND1 | 放宽7→45天: 滞后8~45天的事实从DEGRADED恢复有效(误报消除) |
| DFEDTARL | daily | 45/7/45(monthly) | **45** | APPROVED_ROUND1 | 放宽7→45天: 滞后8~45天的事实从DEGRADED恢复有效(误报消除) |
| ZQ_F1_PRICE | daily | 5/7/45(monthly) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| SHCOMP | daily | 5/7/5(daily) | **10** | APPROVED_ROUND2_CORRECTED | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| SZCI | daily | 5/7/5(daily) | **10** | APPROVED_ROUND2_CORRECTED | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| CHINEXT | daily | 5/7/5(daily) | **10** | APPROVED_ROUND2_CORRECTED | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| HSI | daily | 5/7/5(daily) | **5** | APPROVED_ROUND1 | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| HSCEI | daily | 5/7/5(daily) | **5** | APPROVED_ROUND1 | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| HSAHP | daily | 5/7/7(daily) | **10** | APPROVED_ROUND2_CORRECTED | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| SB_FLOW | daily | 5/7/7(daily) | **10** | APPROVED_ROUND2_CORRECTED | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| MARGIN_BAL | daily | 7/7/7(daily) | **10** | APPROVED_ROUND2 | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| SH_PE | daily | 10/7/7(daily) | **10** | APPROVED_ROUND1 | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| SH_AMOUNT | daily | 5/7/7(daily) | **10** | APPROVED_ROUND2_CORRECTED | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| SZ_COMPONENT_AMOUNT | daily | 5/7/7(daily) | **10** | APPROVED_ROUND2_CORRECTED | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| CN_TOTAL_TURNOVER | daily | 5/7/7(daily) | **10** | APPROVED_ROUND2_CORRECTED | 放宽7→10天: 滞后8~10天的事实从DEGRADED恢复有效(误报消除) |
| REAL_10Y | daily | 7/7/14(unknown) | **7** | NO_CONFLICT | 不变(7天) |
| REAL_5Y | daily | 7/7/14(unknown) | **7** | NO_CONFLICT | 不变(7天) |
| REAL_SHORT | daily | 7/7/14(unknown) | **7** | NO_CONFLICT | 不变(7天) |
| HY_IG_DIFF | daily | 7/7/14(unknown) | **7** | NO_CONFLICT | 不变(7天) |
| ZQ_IMPLIED_AVG | daily | 5/7/45(monthly) | **5** | NO_CONFLICT | 收紧7→5天: 滞后6~7天的事实从有效变为DEGRADED披露 |
| JTSJOL | monthly | 45/92/7(daily) | **60** | APPROVED_ROUND2_CORRECTED | 收紧92→60天: 滞后61~92天的事实从有效变为DEGRADED披露 |

## 5. 已知限制(如实声明)

- 期货曲线点锚点(rate_economy.fed_funds_futures.<i>.price/implied_rate)由sb直接构造不带obs_date: 判龄不可证,保持"无法判龄"警告(如实,不伪造);补时间元数据非本轮范围
- scorecard.*为报告内部推导(非注册表指标): 维持遗留周度10天规则并显式标注非认证
- 窗口为自然日口径(max_calendar_lag_days); 交易所休市日历感知(如遇极端多日休市)属未来工作——大陆10天已覆盖春节/国庆8~9天休市簇
- prev/mom/yoy锚点沿用当前事实observation_date(研究证据时效),不把历史前值观测日伪装为当前观测日

