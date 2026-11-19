# C 线安全增量审查 — Charter 6(deep-macro-v1)

- 审查者: Agent C/D 线(独立安全审计,承接 Charter 4/5 同角色)
- 基准: `dev/deep-macro-v1` @ `2fc8cc5`,range `0f92151..2fc8cc5`(6 commits,50 文件 +3637/−136)
- 日期: 2026-11-10
- 红线遵守: 仓库只读(除本报告文件)、零真实拉取(Shiller 经 fixture 字节注入验证,未下载真实 ie_data.xls;对 Yale 仅 2 次 HEAD 探测无 body)、LIVE 未碰、零凭证实验
- **判定: PASS**(无阻断项。附 F-1 建议修[非阻断]+R-1 登记级风险,详见末节)

## 1. Shiller 采集器网络路径(全新) — PASS(附 R-1/F-1)

文件: `scripts/shiller_collector.py`(全读,280 行)。

- **URL 硬编码**: `SHILLER_IE_URL` 常量(:50),无任何 env/参数注入面;零凭证源。
- **R-1(登记): 源站仅 http**。`http://www.econ.yale.edu/~shiller/data/ie_data.xls` 明文直连;实测 HEAD 探测: http=200 且**无 https 重定向**,https 连接失败(TLS 不通,code=000)——明文是**源站属性**,非实现偷懒。威胁=网络位置攻击者篡改宏观估值数据(数据完整性面,非代码执行面);缓解现状: 解析层结构校验(表头列驱动/月份 1-12 校验/数值列过滤)+source_version 落档可事后人工核対。
- **F-1(建议修,非阻断)**: `build_payload` 将**原始下载字节 sha256** 随档落盘(一行改动),事后可独立核验篡改;配合既有 source_version 构成完整防篡改证据链。
- **恶意 xls 风险面**: `xlrd>=2.0.1` 锁定(requirements.txt +1 行,注释标明用途);xlrd 2.x 仅支持 .xls 值解析、**不执行宏/公式**(`open_workbook(file_contents=raw)` :105)。拒绝服务面(伪造巨型 OLE2)存在但前置条件=MITM(R-1 同源),登记不阻断。
- **下载失败**: `_http_get` 异常→alerts+`sources_status READ_FAIL`(:207-210);`n==0`→`main` exit 1 **不产出文件**(:270-272)——不产空壳 ✓。
- **原子写**: `save_daily` tmp+`os.replace`(:243-250)✓。落盘路径: `data_dir` 仅来自 CLI `--data-dir`(运维者信任级)或仓库内定值;文件名 `shiller_{YYYYMMDD}.json` 纯数字,**无 env 注入路径面** ✓。
- **离线验证**: fixture 字节注入 `build_payload(raw=...)` → 2 系列解析 ✓;`save_daily` 原子写实测(/tmp);`tests/test_charter6_p2_shiller.py` PASS。

## 2. 新 env 变量注入面 — PASS

- `env_config.resolve_history_period`(全读): 严格白名单**精确成员匹配**(`val not in HISTORY_PERIOD_LEGAL` → 回落默认),合法集=yfinance 官方 period 语法 11 值;非法值**不可能**构造注入串(大小写敏感、无拼接、无路径使用)。
- **告警不打值**: `global_market_collector.py:68` 告警仅含合法集与回落默认,**不含原始值**;`env_config` 源零 print(W8 纪律保持)。
- 登记项(非缺陷,先例一致): `macro_collector.py:69` `MACRO_HISTORY_YEARS={raw!r}` 回显原值——既有模式,数值型非密钥配置,可接受。
- `jp_market_collector.py` NIKKEI 窗口共用同一 resolver;`SERIES_WINDOW` 为派生数值遗留别名,无注入面。

## 3. analog 输出敏感面 — PASS

`scripts/analog_engine.py`(660 行,纯确定性计算,声明并验证"不碰文件不碰网络"): 输出键=数值统计(w_norm/norm_wsum/features_detail 的 z 值与归一权重/unavailable_horizons);**无 source_file/engine_root/本机路径字段**(grep 零命中;ia_cli `cmd_analog` 信封仅 data+warnings+snapshot,与其他能力同口径)。先例披露口径未新增暴露面。

## 4. redact 消毒面(六参直存) — PASS

- `ia_cli` sidecar `_san`(redact 包装)与 payload 字段清单在本 range **零改动**(diff 中唯一 `'values': list(...)` 新增属 analog 的内存 series_map 装配,非落盘 payload)。
- 新字段经 Agent 文本参数(--statistics 等)入档仍走既有 `_san` 全量消毒;SPX_CAPE 等新 registry 条目为数值序列,经结构化 values 路径,无自由文本旁路。Charter 5 的两层消毒(模式族+登记明文)未被触碰。

## 5. vendor guard 独立复核 — PASS

新增文件(`shiller_collector.py`/`analog_engine.py`/`data_retention.py`/4 个 charter6 测试)独立 grep: 厂商A/厂商A/厂商A/厂商A/厂商B/ARK_API **零命中**;`tests/test_charter5_vendor_residue_guard.py` 实跑 PASS。

## 6. fixture 安全(三个 xls 二进制入库) — PASS

`charter6_shiller_{min,nocol,pe_col}.xls`: 各 5632B,sha256 前缀 493ea6fae884/d7e0fc98fd9c/0b904fe3af73,sheet=[Data] 单表,字节级扫描**无 VBA/Macros/MODULE 痕迹**;xlrd 2.x 值解析不执行内容。登记面完成(本文件即登记)。

## 7. jp/global 采集器改动 — PASS

diff 新增行仅 env_config resolver 导入与窗口参数化逻辑;**零新增** requests/urlopen/yf./http 调用。`data_retention.py`(新增,维护脚本): 删除范围由锚定正则 `^(?:macro_|global_|china_|japan_|jp_|ea_|rate_economy_|shiller_)(\d{8})\.(json|md)$` 圈定,research_snapshot/anchors 等不可变契约族**不可能匹配**(入 untouched);同月 gzip 归档保留代表档;listdir 名拼接无路径穿越;dry_run 支持。范围安全 ✓。

## 结论与清单

**判定: PASS。** 六 commits 无阻断级安全问题;新增攻击面(网络下载/env 窗口/二进制 fixture/删除脚本)全部核过。

| 编号 | 级别 | 内容 | 建议 |
|---|---|---|---|
| R-1 | 登记 | Shiller 源站仅 http(Yale 无 TLS),明文下载=源站属性 | 已有结构校验+source_version;接受并登记 |
| F-1 | 建议修(非阻断) | `build_payload` 增加**原始字节 sha256** 随档落盘 | 一行改动,事后可独立核验 R-1 的篡改风险 |
| 登记 | 先例一致 | macro `MACRO_HISTORY_YEARS` 告警回显原值(数值配置非密钥) | 维持现状 |

验证记录: charter6 四套件+vendor guard 5/5 PASS(本机离线实跑);Shiller 零网络注入验证+原子写实测;HEAD 探测 2 次(http 200/https 000,无 body 无凭证)。
