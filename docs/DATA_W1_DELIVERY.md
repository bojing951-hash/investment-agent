# DATA-W1 · 交付文档 — data/daily 盘点工具 + 缺失指标只读诊断

> **契约**: IA-DATA-W1-AC-v1.0(数据管理独立 track 首包)
> **分支**: `dev/data-inventory`(自 `dev/p0-2-w5-fix3`@`1ddfb65ec78f4358b7a004be8ef5d8916ba0f052` 切出)
> **交付物**: A=`scripts/data_inventory.py`(仅标准库)· B=`tests/test_data_inventory.py`(离线自足)
> · C=本文件 + `docs/DATA_W1_MISSING_DIAGNOSIS.md` · D=证据包 `/tmp/data-inv-evidence/IA-DATA-W1-EVIDENCE.zip`

## 1. 工具用法(两种模式)

### 1.1 inventory(目录清单)

```bash
python3 scripts/data_inventory.py inventory --dir data/daily --out <清单.json>
# --out 缺省时打印到 stdout;成功 exit 0;参数/IO 错误 exit 2
```

输出 schema(契约§三;`generated_utc` 为 ISO8601Z;文件按名排序,确定性输出):

```json
{ "schema_version": 1, "generated_utc": "…", "target_dir": "…", "file_count": N,
  "files": [ { "file": "…", "size_bytes": N, "sha256": "<64hex>",
               "summary": { "data_date": …, "assets_count": …, "assets": […],
                            "close_meta_present": … },
               "notes": "file_type=…[; 异常说明]" } ] }
```

真实演练(2026-11-02,DEV `data/daily/` 12 文件): `file_count=12`,每条目
三元组与独立命令 `shasum -a 256` / `stat` 重算一致(证据包
`inventory_actual_data_daily.json` + `baseline_data_daily_shasum.txt` 逐文件对照)。

### 1.2 diff(清单对比)

```bash
python3 scripts/data_inventory.py diff <old.json> <new.json> --out <结果.json>
# exit 0=无差异 / 1=有差异 / 2=错误
```

输出: `{old, new, generated_utc, added[], removed[], changed[{file, old{sha256,size_bytes}, new{sha256,size_bytes}}]}`;
`added/removed` 条目含 `file/sha256/size_bytes`(契约"至少含文件名"的超集)。
构造演示(1增1删1改,exit=1;恒等对 exit=0): 证据包 `diff_demo/`(输入对
+ 输出逐字记录,可静态复核,不依赖运行工具)。

### 1.3 CLI 语义

`--help` 可用(exit 0);无参/参数错/IO 错 → stderr + exit 2(argparse 原生
usage 错误码即 2);工具对目标目录**只读**。

## 2. 摘要提取规则(按 data/daily 文件类型逐类;DI-AC-01 要求项)

判定顺序: 文件名前缀+扩展名匹配下表六类;未命中 → `generic_json`/`generic_md`/
`other`(summary 四键全 `null`,notes 注明"未登记类型")。`summary` 四键
(`data_date/assets_count/assets/close_meta_present`)**必存**,不适用记 `null`。
`notes` 恒含 `file_type=` 标记(便于审计),异常时附加原因。

| 类型(file_type) | 判据 | data_date | assets / assets_count | close_meta_present | 不适用判据与备注 |
|---|---|---|---|---|---|
| `china_json` | `china_*.json` | `timestamp` 前10字符(ISO日期) | `a_share_indices` ∪ `hk_indices` 两对象键的并集(排序) | 任一资产条目**同时含 `close` 与 `date`** 键 → `true`,否则 `false` | `ah_premium` 为单对象(指数级)不计入资产;`margin/southbound/turnover` 为 null 通道非资产映射 |
| `global_json` | `global_*.json` | 顶层 `date`(原样,`YYYYMMDD`) | `data` 对象键(排序) | 同上 close+date 判据(对 `data` 各条目) | — |
| `global_md` | `global_*.md` | 首行 H1 中首个 `20\d{6}` | markdown 表格数据行首列(跳过表头/分隔行) | 表头含"收盘"列 且 ≥1 数据行 → `true`,否则 `false` | 无表格 → date 仍取首行,assets 记实际解析结果 |
| `macro_json` | `macro_*.json` | 顶层 `date` | `data` ∪ `derived` 两对象键(指标ID) | **`null`(不适用)** | 指标条目为 `value/date` 序列,无"资产收盘"语义——此即本类的 close 判据登记 |
| `rate_economy_json` | `rate_economy_*.json` | 顶层 `date` | `current_rates` ∪ `real_economy` 键 ∪ `fed_funds_futures[].ticker` | **`null`(不适用)** | 利率/宏观序列,无资产收盘语义;`rate_expectations` 为标量组不入 assets |
| `rate_economy_md` | `rate_economy_*.md` | 首行 H1 中首个 `20\d{6}` | **`null`(不适用)** | **`null`(不适用)** | 散文式摘要,无机器可枚举资产表;数值面见同日 `.json`(notes 注明) |
| `generic_json` / `generic_md` / `other` | 其余 | `null` | `null` | `null` | 未登记类型;notes 注明 |

异常路径: 已知类型 JSON 解析失败 → 四键 `null` + notes `JSON解析失败: <原因>`;
**三元组(file/size_bytes/sha256)不依赖解析成败,恒完整**。

## 3. CI 发现机制核实结论(DI-AC-04·2 要求项)

**结论: 情形(a)——自动发现 `tests/test_*.py`。**

依据(`.github/workflows/offline-tests.yml` L38-45 原文,2026-11-02 开轮实读):

```yaml
          for t in tests/test_*.py; do
            name=$(basename "$t" .py)
            if [ "$name" = "test_glm_live" ]; then
              echo "== $name: SKIPPED(真实GLM付费调用,不进CI) exit=skipped"
              continue
```

glob `tests/test_*.py` 自动发现全部套件,仅显式排除 `test_glm_live`(真实付费
调用)。故操作者 dispatch 的 run 将自动包含新套件 `test_data_inventory`
(本地文件数 54 → CI 执行 54-1排除 = 54 个非排除套件 = fix3 基线 53 + 新 1)。
与合同§七预判一致(FIX2 先例: 新增 test_p02_w5_fix2 时 workflow 零改动而 run
含之)。

## 4. 测试与本地全套件(DI-AC-04·1)

`tests/test_data_inventory.py`: 19 用例,unittest(CI 直跑兼容
`python3 tests/test_data_inventory.py`,亦兼容 pytest 收集),仅 tmp 合成
fixture(自造小 JSON/MD,覆盖 china_json/global_json/global_md/rate_economy_md/
未登记类型 ≥2 类型的 summary 提取),零网络、零真实 data/daily 依赖。

- **I组** 清单三元组: 测试内以 `hashlib.sha256`/`stat` **独立重算**对照(不以
  工具自身输出为其正确性唯一证据);
- **S组** 逐类型 summary 与 null 语义(含坏 JSON: 三元组仍完整);
- **D组** diff 三类(1增1删1改,changed 含前后 sha256/size 与两侧清单原值逐字
  对照)+ 恒等对;仅 size 变化亦检出;退出码 1/0;
- **C组** CLI: `--help` exit 0;无参 exit 2;坏目录 exit 2;diff 缺文件/坏输入
  exit 2;
- **R组** 负向敏感性(repo R3 惯例,源码文本最小退化替换 + importlib 加载):
  R1 哈希退化(`sha256→md5`)→ 与独立重算必然分离;R2 diff 退化(changed 判定
  置 `if False:`)→ 漏检 changed,与正确版同输入行为分离。

本地全套件(逐套件退出码留档于证据包,CI 同口径 `python3` 直跑、排除
`test_glm_live`):

| 环境 | 结果 | 记录 |
|---|---|---|
| CI 等效环境(clone@`569b228`(工具+测试提交点,docs 提交不改测试面),`data/` 空=与 Actions checkout 一致) | **54/54 全绿**(53 既有 + 1 新) | `local_suite_exit_codes_CIEQ.txt` |
| DEV 工作区(带真实 `data/daily`) | 53 绿 + `test_p4_fixes exit=1` | `local_suite_exit_codes.txt` |

`test_p4_fixes` 在 DEV 工作区的失败为**既有环境差异**(FIX2 交付文档
docs/P0_2_W5_FIX2_DELIVERY.md §6 已在案: 该套件 glob 命中真实 `global_2026*.json`
即用真实目录,而 `data/daily` 内无 202609 当月文件→月度序列 0 条;CI 空
`data/` 走 e2e fixture 全绿)。本轮第一手复核: 移除本轮两个新文件后重跑,
同样 39通过/4失败(证据 `test_p4_fixes_without_new_files.log`)——与本轮改动
无关,CI 等效环境下 exit=0。既有测试零删除/零弱化/零跳过(除 workflow 明示
排除的 test_glm_live,同 CI 口径)。

## 5. 诊断报告指引(DI-AC-05)

缺失指标只读诊断见 **`docs/DATA_W1_MISSING_DIAGNOSIS.md`**(R004-D4 承接)。
一句话结论:

- **MARGIN_BAL**: 双层断点——当前 `margin: null`(tushare 源端失败)+ 结构性
  键/口径断裂(采集器产出 `rzye/rzye_billion`(融资余额)≠ 引擎期望
  `balance`(两融合计,注册口径));
- **SH_PE**: 三层断点——当前 `valuation: {}`(同源失败)+ 嵌套格式
  (`{指数:pe_ttm}`)≠ 引擎期望扁平 `pe` + `VALUATION_INDICES` 不含上证
  `000001.SH`(身份断裂,300/500/1000 的 PE 不得冒充)。

报告含每指标四节(链路/断点/证据/建议)与 U 项登记(采集时刻具体报错、
tushare 对 000001.SH 的可得性——需外部源定夺)。**未实施任何修复。**

## 6. R005-D3 / R004-D4 承接说明

- **R005-D3(开/收轮 data/daily 取证清单手工化)→ 工具化**: 历轮开/收轮以
  手工 `shasum -a 256 data/daily/*` 落档(R006 审计全量哈希实践)。本轮将该
  实践固化为 `scripts/data_inventory.py inventory`(三元组+摘要+确定性排序),
  `diff` 子命令直接支撑"收轮 vs baseline 逐文件对照"(本轮已演练: 全量一致,
  见§7)。工具转正后可作为历轮开/收轮标准取证手段(契约§五)。
- **R004-D4(MARGIN_BAL/SH_PE 长期缺失根因未定位)→ 只读诊断**: 见§5;
  修复方向已给出(仅建议),数据线第 2 包依诊断结论另拟合同(涉新源/凭证先上
  PENDING)。

## 7. 只读复核(DI-AC-03)

开轮(工具开发前,独立命令 `shasum -a 256 data/daily/*`)与收轮(同法独立
命令复核 + 本工具生成清单三方对照): 12 文件哈希**全程一致,零差异**
(证据包 `baseline_data_daily_shasum.txt` / `closing_data_daily_shasum.txt` /
`inventory_actual_data_daily.json`)。`data/daily/` 本轮零写入。

## 8. 范围与证据

- 改动恰为白名单 4 新增文件(A/B/C×2),既有代码/测试/workflow 零 hunk
  (`git diff --name-status 1ddfb65..尖端` 见证据包 `git_diff_name_status.txt`);
- 证据包: `/tmp/data-inv-evidence/IA-DATA-W1-EVIDENCE.zip`(路径/SHA256/条目
  清单见自述报告与包内 `SHA256SUMS`);
- CI dispatch: 由操作者 CHECKPOINT 执行(执行方零 CI 动作);按§3 情形(a),
  dispatch run 须含 `test_data_inventory` 且绿、总套件数=53+1。
