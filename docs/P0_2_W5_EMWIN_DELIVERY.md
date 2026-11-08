# P0-2 W5-EMWIN 交付文档(R051;IA-P0-2-W5-EMWIN-AC-v1.0 配套)

- 分支: `dev/p0-2-w5-emwin`(自基点 `f124ef3b5a261b329fbbef9722026df23e2f7e7a` 新建)
- 本轮唯一行为变更: `EM_FALLBACK_MAX_DATE='2026-11-03'` 合同级常量 → `_em_max_date(now=None)` 动态函数(HKT 已完结交易日截止)
- 证据包: `/tmp/w5emwin-evidence/`(SHA256SUMS+zip 见 §六)

## 一、开工保险(全部实取字面值)

1. **附录A合同 FROZEN 核验——无法执行,如实登记**: 主Agent提示词称"附录A=本目录
   IA-P0-2-W5-EMWIN-AC-v1.0.md 全文(FROZEN)",但**附录A全文未随提示词注入**;
   DEV 仓库全树 glob `**/*EMWIN*` 零命中,授权工作目录(~/AI内容 等)
   零命中,引擎目录(~/agent-loop)会话沙箱确认不可达(与提示词"你无法访问引擎
   目录"自述一致)。→ 冻结章+sha256 的直接核验在执行位不可执行。**替代基准**:
   驱动注入的"本轮验收条件"五条(EM-AC-01~05,明示"冻结/待冻结,由驱动注入;
   对照自检用")为对照自检依据;本文件 §五所需"合同§〇锚定一引文"以注入文本
   替代并显式标注,引擎侧原文核对权属 Agent 4。**零编造**。
2. 基点核验: `git rev-parse HEAD` = `f124ef3b5a261b329fbbef9722026df23e2f7e7a`
   (与提示词逐字同值);`git status --porcelain` 零输出(树净);开工时当前支
   `dev/p0-2-w5-rerun` ✓ → `git checkout -b dev/p0-2-w5-emwin` ✓(开轮 UTC=
   2026-11-04T09:37:10Z,git/opening-utc.txt)。
3. 24 支零漂移: `git ls-remote origin`(25 行=24 refs/heads+HEAD)与 R050 收轮
   快照 `/tmp/w5rerun3-evidence/git/closing-ls-remote.txt` 排序 diff=**零差异**
   (`ZERO_DRIFT_24_BRANCHES`,含 `dev/p0-2-w5-rerun@f124ef3` 逐字一致;
   本证据域 git/opening-ls-remote.txt 留档)。

## 二、改动清单(diff 恰 3 文件;基点→本尖端)

```
 scripts/china_market_collector.py   | 34 ++++++++++++---
 tests/test_p02_w5_datasrc_b.py      | 98 ++++++++++++++++++++++++++----
 docs/P0_2_W5_EMWIN_DELIVERY.md     | 新增(本文件)
 3 files changed(工作树 git diff --stat 实取;commit 后以 name-status 复核)
```

### 关键 hunk( collector 5 hunks )

| # | 位置 | 内容 |
|---|------|------|
| h1 | @@ -12,7 | `from datetime import datetime, timedelta` → `…, timedelta, timezone`(1 行;`import time` L12 原样,零覆盖) |
| h2 | @@ -79,7 | 常量行 → 6 行注释(R051 缘起)+`def _em_max_date(now=None)`+docstring+7 行实现 |
| h3 | @@ -91,17 | `_em_settled_pairs` docstring+L116 比较行: `<= EM_FALLBACK_MAX_DATE` → `<= _em_max_date()` |
| h4 | @@ -113,7 | `_em_last_settled`/`_fetch_index_em` docstring 同步 |
| h5 | @@ -122,7 / @@ -523,7 / @@ -534,7 | 两处无完结行告警 f-string+方案2注释: 标识符机械替换 |

**引用计数如实登记**: `EM_FALLBACK_MAX_DATE` 在 collector 内共 **8 行提及** =
定义 1(L82,本次转换为函数本体)+ 代码引用 3(L100/125/537)+ docstring 3
(L94/104/116)+ 注释 1(L526)。任务书"6 处引用"≈代码 3+docstring 3;L526 注释
一并替换(否则残留悬空标识符,违反机械替换不留残渣的意图);全文件替换后
`grep EM_FALLBACK_MAX_DATE` 仅存于历史说明注释(L82 缘起注释引述旧常量名,非活引用)。
**行为零触碰面**(§一禁令)逐项: 61s 闸门零变化/tushare 调用参数零变化/
A_SHARE_INDICES 与 EM_MAP 清单零变化/单位换算(÷1e8、÷1e5)零变化/via·source
标记零变化/None 语义零变化/在途禁用语义零变化(date≤截止,仅截止随钟动态)。
阈值容差(real_data_acceptance)零触碰;八项门槛零触碰。

### 测试( tests/test_p02_w5_datasrc_b.py,21→23 用例,只强不弱 )

- t2f 常量断言 → `test_t2f_cutoff_function_four_vectors_frozen_clock`(四向量
  +常量零残留+aware 任意时区折算 HKT+naive 按 HKT 墙钟,共 10 断言)——任务书
  明示的 1:1 升级,唯一被替换的既有断言(常量已不存在,锁语义升级为函数锁)。
- **既有断言零删改**: t1a/t1b/t2a~t2e/t3a~t3d/T4 全部/T5 全部的断言体逐字保留
  (diff 可核);行选择测试(t1c/t2a/t2b/t2d/t2e/t3b/t3d)统一加 `freeze_clock`
  冻结时钟注入——`monkeypatch cmc.datetime` 为冻结子类(now()/now(tz) 恒返同一
  时刻),被测 `_em_max_date`→`_em_settled_pairs`→`_fetch_index_em`/`fetch_turnover`
  全程**真实代码**,仅钟被冻结 → 测试与时钟无关。
- 新增 2 强锁: `t2g`/`t3e`——FROZEN_POST(11-04 16:10:00 HKT)下同一 fixture 的
  11-04 在途行**转为取值行**(date='20261104'/close/单位/via/source 全链)——
  锁住"窗口动态推进"这一本轮核心行为,负向敏感度证明两条均红。
- 锚点: `FROZEN_AM`=2026-11-04T10:00+08:00(→截止 2026-11-03,保留 R049 全部
  原值断言的语义等价钟);`FROZEN_POST`=2026-11-04T16:10:00+08:00(→截止 2026-11-04)。

## 三、语义规格对照( `_em_max_date`,EM-AC-03 四向量逐字)

规则: HKT 已完结交易日截止——时刻 ≥16:10:00 → 当日 ISO;否则前 1 **自然**日 ISO
(非交易日历日;周六→周五)。`now=None` 缺省读真实 HKT 钟(UTC+8 固定偏移,无夏令时);
aware 输入(任意时区)一律 `astimezone` 折算 HKT 判定;naive 输入按 HKT 墙钟。

| # | 冻结时刻(注入 now) | 期望 | 实测 | 断言位置 |
|---|---------------------|------|------|----------|
| ① | 2026-11-04T15:59:00+08:00 | '2026-11-03' | '2026-11-03' ✓ | t2f v1 |
| ② | 2026-11-04T16:09:59+08:00 | '2026-11-03' | '2026-11-03' ✓ | t2f v2 |
| ③ | 2026-11-04T16:10:00+08:00 | '2026-11-04' | '2026-11-04' ✓(阈值含等于) | t2f v3 |
| ④ | 2026-11-07T10:00:00+08:00(周六) | '2026-11-06' | '2026-11-06' ✓(前1自然日=周五) | t2f v4 |
| 加强a | 2026-11-04T08:09:59Z(=16:09:59 HKT) | '2026-11-03' | ✓ | t2f v5 |
| 加强b | 2026-11-04T08:10:00Z(=16:10:00 HKT) | '2026-11-04' | ✓ | t2f v6 |
| 加强c | naive 2026-11-04 16:09:59 | '2026-11-03' | ✓ | t2f v7 |

行为契约保留断言(全部通过,consoles/FINAL-pytest-datasrc-b.txt `23 passed`):
在途行禁用(t2a)/无完结行→None(t2b)/EM 失败→None(t2c,t3c)/÷1e8 单位
round2(t3b,t3e)/via='akshare_em' 与 source='akshare_em'(t2d,t3b,t3e)/tushare
先行零变化(t1a/t1b/t1c)/诚实标签 T4 全套/源级冻结 T5 全套零触碰。

## 四、三重验证(console 全留档 /tmp/w5emwin-evidence/consoles/)

1. **本机全套件**(任务 §三①,如实双口径):
   - `python3 -m pytest tests/ -q` 整树: **既有结构性 INTERNALERROR**(收集期
     test_datafix_20261017.py 模块级 `sys.exit`;基线前/后 console **逐字节同象**,
     唯一差异=运行时长 0.99s→0.95s,pytest-wholetree-BASELINE-vs-POST.diff 4 行)。
     R049 交付文档 §line46 已登记同象为"W5-FIX2 轮先例、本套件历史上以 CI 逐文件
     方式运行"——非本轮引入、非本轮回归,禁子集要求以整树命令如实执行并留档。
   - **CI-parity 权威口径**(与 GitHub Actions 运行步逐字同构的逐文件循环;
     clone@f124ef3+2 改动文件,data/ 天然空=git 0 文件=checkout 同构):
     **54/54 exit=0,SUITE_FAIL=0**(SUITE-CI-PARITY-SUMMARY.txt;套件文件数 54,
     含升级后 test_p02_w5_datasrc_b.py 内 23 用例 OK)。
   - DEV 工作树逐文件: **53/54**,唯一红=test_p4_fixes exit=1,失败签名
     "提取到≥5个月度序列 got 0"=R049/W5-FIX2 §6 登记的既有数据环境差异(需多月
     data/daily 历史;该套件在上 CI-parity 空数据克隆=exit=0),与本轮 diff 零交集
     (SUITE-DEV-WORKTREE-SUMMARY.txt+逐套件日志)。
2. **CI-sim akshare 掩码绿**: /tmp/ci-sim-mask/akshare.py=`raise ImportError`
   置 sys.path 首位(PYTHONPATH 前位遮蔽语义等价,R049-fix2 同型)→
   `23 passed, PYTEST_EXIT=0`(CI-SIM-akshare-masked-pytest.txt)。
3. **负向敏感度红→还原→绿**: 临时注入真实缺陷(`now >= cutoff` 判定取反为
   `now < cutoff`,恰 1 行)→ `7 failed, 16 passed`(红: t2f 四向量+t2a/t2b/
   t2g/t3b/t3d/t3e——含两条新增强锁,证明其对缺陷敏感)→ 还原 → `23 passed`
   (NEGSEN-inverted-threshold-RED.txt / NEGSEN-restored-GREEN.txt;缺陷仅存在于
   工作树 2 次运行之间,未入 commit)。

## 五、R050 缺陷背景与操作者裁定转述(附引文)

**缺陷背景(R050 判定件实测)**: R050 四源全跑后 Gate A core 缺失 4→0 清零
(4 只全经 EM 回落),但收盘守卫 FAIL——china 取值行 date=20261103≠20261104,
机制= tushare index_daily 7 调全拒(日配额外部先在耗尽)+EM 回落被 R049 冻结的
合同级常量 `EM_FALLBACK_MAX_DATE='2026-11-03'` 钉死取值行 → 收盘守卫(要求
取值行=运行日 2026-11-04)**结构性不可满足** → overall=NOT_VERIFIED(exit 3)。
R050 交付文档 §偏差 明示"零凑数: 未改截止、未改阈值、未换比较日"如实交审计。

**操作者裁定与批准基础(注入提示词 §二 逐字转述)**:

> "R050判定件落档: GateA core缺失4→0清零(全经EM回落)但overall=NV——根因之一
> =china_market_collector.py L82合同级常量`EM_FALLBACK_MAX_DATE='2026-11-03'`
> 把EM取值行永久钉死11-03,收盘守卫(要求11-04)结构性不可满足(R050合同违反
> '无结构性不可满足'的操作者设计缺陷,executor无责)。本轮依用户方案B实批(免费
> EM端点换路,通道后续交易日正常出数=授权固有内容)+操作者裁定,将该常量动态化,
> 测试同步语义升级。**这是本轮唯一授权行为变更**。"

**合同 §〇 锚定一引文——执行位不可得,如实声明**: 附录A(IA-P0-2-W5-EMWIN-AC-
v1.0.md 全文)**未随提示词注入**且引擎目录不可达(§一1),执行位无法逐字引用
合同 §〇 锚定一原文;上方引文为**主Agent注入提示词的逐字文本**(§二+验收条件
节),语义覆盖: 缺陷定性(结构性不可满足=操作者设计缺陷、executor 无责)/批准
基础(用户方案B实批+操作者裁定)/授权范围(常量动态化+测试语义升级=唯一行为
变更)。引擎侧合同原文与冻结章+sha256 的核对权属 Agent 4。**本文件零编造引文**。

## 六、CI 说明与收轮

- **执行侧零 CI 动作**: 本轮不 dispatch、不改触发(R032/R049/R050 先例;执行面
  白名单无 dispatch 权);workflow 触发器=push/PR 到 main+manual dispatch,
  push dev 支不触发 CI。
- **操作者侧预期**: 最终尖端 workflow_dispatch `offline-tests` → **预期 54 套件
  全绿**(逐文件口径;套件文件数与 R049/R050 基线同为 54,本轮 0 新增文件,
  升级发生在既有文件内: 21→23 用例=+2 强锁,只强不弱)。
- 隔离(只读取证): LIVE china_market_collector.py SHA256=eba388e9…两读同值
  (≠DEV 改动件,LIVE 零触碰);launchd grep investment-agent-dev=0 命中;
  引擎目录零触碰(沙箱不可达);凭证明文清扫 grep api_key/token/secret=
  证据包零命中(SHA256SUMS 豁免自身前的全包扫描)。
- 证据包: /tmp/w5emwin-evidence/{git,consoles,isolation,result.md,SHA256SUMS,
  IA-P0-2-W5-EMWIN-EVIDENCE.zip};收轮 `git ls-remote` 复验 24 支零漂移+
  本支恰 1 笔线性追加(见 git/closing-ls-remote.txt、git/commit-chain.txt)。

## 七、偏差与如实声明(汇总)

1. 附录A合同全文未注入+引擎目录不可达 → §0.1 冻结章/sha256 直接核验不可执行;
   以驱动注入的 EM-AC-01~05 为对照自检基准;§五引文以注入文本替代(零编造)。
2. "6 处引用"实为 8 行提及(定义1+代码3+docstring3+注释1),全部机械替换,
   计数差异如实登记(§二)。
3. 任务 §三①"pytest tests/ -q 全绿"与仓库既有结构性 INTERNALERROR 冲突 →
   整树命令如实执行+基线前后同象留档+CI-parity 逐文件 54/54 权威口径(§四1)。
4. 新增 2 用例(21→23): 依"只强不弱"对"窗口动态推进"核心行为加锁;套件文件数
   仍=54,操作者侧 CI 预期不变(§六)。
5. 本轮零真实数据运行、零判定件、零 data/daily 写入、零 LIVE/launchd/引擎触碰
   (微修复轮,§三未授权真实采集;EM 通道动态化后的真跑属后续轮次)。
