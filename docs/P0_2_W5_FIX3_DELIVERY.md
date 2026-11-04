# P0-2 W5-FIX3 交付文档(IA-P0-2-W5-FIX3-AC-v1.0)

- **轮次**: Round 006(W5-FIX3 近零代码最小整改轮: 仅 workflow 依赖一行 + docs)
- **分支**: `dev/p0-2-w5-fix3`(自 `dev/p0-2-w5-fix2`@`02f1bade0688fed6afd61aa8973bc326c3a75c1d` 切出,ls-remote 实取核对)
- **代码态**: 与 `9e6fe71`(FIX2 最终代码SHA)完全一致——本轮**零生产代码/测试改动**,仅 docs 更正/新增 + workflow 一行
- **证据包**: `/tmp/w5fix3-evidence/IA-P0-2-W5-FIX3-EVIDENCE.zip`(路径+SHA256全值+条目清单见包内 README 与 SHA256SUMS)
- **整改对象**: R005 终裁三项阻断——R-BLK-3(DIAG失实引用)、R-BLK-2(CI依赖)、R-BLK-1(china尝试取证,达标判定已移出本合同)

## 1. R-BLK-3 DIAG 证据链更正(F3-AC-01)

### 1.1 事实底稿(原档实录,不可推翻)

`DIAG-EXT-BTC-20261102.txt`(FIX2 证据包内原件,SHA256=`e4e48938f1355131c38f306ef9bf5ed9d973261be29fd04760edf9b443be70c1`,2026-11-01T16:44Z 运行)实际记录:

- `check_btc verdict=NOT_VERIFIED`
- Coinbase evidence: `status_code: null, sha256: null`
- `candles dates: []`
- note: "Coinbase日K不可达/无数据(诊断见外部证据)"

00:50(同日)另由 `capture_coinbase_raw.py` 手动取回真实 body(`evidence-coinbase-btcusd-20261031.json`,SHA256=`9235918b45490622b65451296d3d260d81f439ed4ab3bacfe006c203e0487bab`,close=77423.98,start_ts=1793404800=UTC日界)——**系手动取证,非 check_btc 输出**。R005 审计据此独立复算偏差 0.0139%(77434.75 vs 77423.98)为真,但 FIX2 文档将该档引为"check_btc PASS/偏差0.01%"属失实引用。

### 1.2 更正路径 = (a) 重跑诊断(Coinbase 已恢复可达)

本轮 2026-11-01T17:51:13Z 对同一 20261102 快照 BTC 记录(77434.75@2026-10-31,close_meta 完备)重跑 check_btc 诊断(Coinbase 真实 candles,granularity=86400,UTC 2026-10-31 完整日,原始 body+哈希留档):

- **新档**: `DIAG-EXT-BTC-20261102-R2.txt`(R2 区分标记;连同 R2 原始 body `evidence-coinbase-btcusd-20261031-R2.json` 入 FIX3 证据包)
- **R2 实测结果(如实)**: candles=['2026-10-31'],close=77423.98,start_ts=1793404800(start_ts%86400=0,UTC日界);**check_btc verdict=PASS,偏差0.01%**(脚本口径"四舍五入至0.01%再比较"的输出);未舍入偏差=0.013910%≈0.0139%(|77434.75−77423.98|/77423.98×100),与合同预登记 0.0139% 一致
- **R2 body 完整性**: SHA256=`9235918b45490622b65451296d3d260d81f439ed4ab3bacfe006c203e0487bab`,与 FIX2 00:50 手动捕获 body **逐字节一致**(哈希相同)——两时点独立取得同一外部事实
- R2 仍为**工程诊断,非正式验收产物**(正式重跑判定已整体移出本合同,§六附则)

### 1.3 失实引用逐处更正清单(文件:行,原句→更正句)

**DEV 库内(docs/P0_2_W5_FIX2_DELIVERY.md,5 处,已在本分支更正)**:

| # | 位置 | 原句(失实) | 更正句(要点) |
|---|---|---|---|
| 1 | docs/P0_2_W5_FIX2_DELIVERY.md:49(§3.6) | "直接驱动 check_btc vs Coinbase 同UTC日K → **PASS,偏差0.01%**(完结vs完结;证据包 DIAG-EXT-BTC-20261102.txt)" | "原始诊断档 DIAG-EXT-BTC-20261102.txt 实际记录 check_btc=NOT_VERIFIED(Coinbase当时不可达: status_code=null、candles=[];00:50 另由 capture_coinbase_raw.py 取回真实 body,系手动取证非 check_btc 输出)。FIX3 轮 R2 重跑(DIAG-EXT-BTC-20261102-R2.txt)check_btc=PASS、偏差0.01%(未舍入0.0139%=77434.75 vs 77423.98;body SHA256 9235918b…与FIX2捕获body逐字节一致;start_ts=1793404800=UTC日界;完结vs完结)" |
| 2 | docs/P0_2_W5_FIX2_DELIVERY.md:66(§5) | "§3.6——快照BTC…vs Coinbase同日完整日K=PASS/0.01%(完结vs完结)" | "§3.6 原始诊断档实际记录 check_btc=NOT_VERIFIED(Coinbase当时不可达,candles=[]);FIX3 轮 R2 重跑(check_btc 真实输出)…=PASS/0.01%(未舍入0.0139%;证据: FIX3证据包 DIAG-EXT-BTC-20261102-R2.txt)" |
| 3 | docs/P0_2_W5_FIX2_DELIVERY.md:67(§5) | "工程探针显示既有源在数据日的预期状态(UST 0bp同日行/BTC 0.01%/…)" | "既有源在数据日的预期状态(UST 0bp同日行/BTC 手动复算0.0139%(FIX3 R2重跑check_btc实证PASS/0.01%)/…)…(BTC该值非当日check_btc输出——原始诊断档NOT_VERIFIED,见§3.6更正)" |
| 4 | docs/P0_2_W5_FIX2_DELIVERY.md:87(§7.3) | "本轮真实数据实证完结vs完结=0.01%,工程诊断" | "真实数据完结vs完结差异=0.0139%未舍入——FIX3 R2重跑check_btc输出0.01%为四舍五入口径;原始诊断档当时NOT_VERIFIED,见§3.6更正" |
| 5 | docs/P0_2_W5_FIX2_DELIVERY.md:112(§10) | "F2-AC-02(…含真实数据级工程诊断PASS/0.01%)" | "F2-AC-02(…;真实数据级行为——原始诊断档NOT_VERIFIED(Coinbase当时不可达),FIX3 R2重跑check_btc=PASS/0.01%(未舍入0.0139%),见§3.6更正与FIX3交付文档)" |

**FIX2 证据包内(README.txt / UNVERIFIED-ITEMS.txt,2 处——包为 R005 审计对象原件,只读不可改,以本声明更正)**:

| # | 位置 | 失实表述 | 更正声明 |
|---|---|---|---|
| 6 | FIX2包 README.txt:18-19 | "DIAG-EXT-BTC-20261102.txt …工程诊断…→check_btc PASS/偏差0.01%(完结vs完结口径)" | 该档实录 NOT_VERIFIED(Coinbase不可达/status_code=null/candles=[]);0.01%系手动复算(未舍入0.0139%),后由 FIX3 R2 重跑 check_btc 实证 PASS/0.01%(DIAG-EXT-BTC-20261102-R2.txt)。该表述自本声明发布之时起作废,以本节为准 |
| 7 | FIX2包 UNVERIFIED-ITEMS.txt:16-19(U-2) | "工程级替代证据…DIAG-EXT-BTC-20261102.txt——快照BTC…check_btc(verdict=PASS,偏差0.01%,完结vs完结口径)" | 同上;U-2 的准确表述应为"该档 check_btc=NOT_VERIFIED;body 级手动取证(9235918b…)支撑独立复算 0.0139%;FIX3 R2 重跑实证 PASS/0.01%" |

更正核对: 最终尖端全库检索 `DIAG-EXT-BTC-20261102`,命中仅 2 处(§1.3 表 #1/#2 所在行),均以 NOT_VERIFIED 如实领起、PASS/0.01% 明确归因 R2 重跑——固定反例(PASS/通过/0.01% 归因原档)不存在。

### 1.4 原档保全

原档 `DIAG-EXT-BTC-20261102.txt` 不修改、不删除、不移位: 仍在 FIX2 证据包内(SHA256 全值 `e4e48938…`,开/收轮一致——收轮以 `unzip -p | shasum` 复核),字节副本+SHA256 入 FIX3 证据包(`fix2-zip-extracts/DIAG-EXT-BTC-20261102.txt`)。

## 2. R-BLK-1 china 一次性诚实尝试(F3-AC-02;条件分支未触发)

### 2.1 尝试记录(证据任务,单次,零修改零变通)

- **命令**: `python3 scripts/china_market_collector.py`(cwd=DEV 仓库根,既有调用方式,零参数: 不加间隔等待、不改调用顺序、不换接口)
- **时间**: 开始 2026-11-01T17:55:39Z,结束 2026-11-01T17:55:57Z(2026-11-02 01:55 HKT);采集器 exit=0
- **逐资产响应原文**: 完整 console 见证据包 `china-20261102-fix3-attempt.log`(逐字留档);关键逐资产响应:
  - 上证指数(000001.SH): ❌ "抱歉,您访问接口(index_daily)频率超限(5次/天)…"
  - 深证成指(399001.SZ): ❌ "抱歉,您访问接口(index_daily)频率超限(1次/分钟)…"
  - 创业板指(399006.SZ)/沪深300(000300.SH)/中证500(000905.SH)/中证1000(000852.SH): ❌ 同上"频率超限(1次/分钟)"
  - 恒生指数: ✅ 23294.42(周+0.36%)[腾讯直连];恒生国企: ✅ 7862.22(周+0.77%)[腾讯直连]
  - 南向资金: ❌ 无接口(moneyflow_hsgt)访问权限;融资融券: ⚠️ 暂不可用;指数估值×3: ❌ 无接口(index_dailybasic)访问权限
  - A股成交额: ❌ tushare"频率超限(1次/分钟)" + akshare amount=0 跳过
  - AH溢价指数(HSAHP): ✅ 132.49(港股偏便宜)[新浪直连]
- **产物文件**: `data/daily/china_20261102.json`(28681 字节,a_share_indices 空、港股2只+AH溢价在)

### 2.2 结果与条件分支

- **结果**: 未取得 SHCOMP,未取得 SZCI(全部 A 股指数被 tushare 限流拒绝;SHCOMP 本次报"5次/天"=当日配额亦耗尽,SZCI 报"1次/分钟"=同 run 第2只调用的结构性拒绝,与合同§六附则实证一致)。
- **条件分支(须同次取得 SHCOMP 与 SZCI)未触发**——未运行正式重跑;无重试、无择时复跑、无任何"跑通"手段。
- 本尝试价值=如实取证呈报用户作路径①(china 通道改造)决策依据;限流被拒是预期且合法结果,仅是证据内容,不影响本合同判定。
- **快照保护(同日覆盖留档)**: 尝试产物覆盖 `china_20261102.json`——覆盖前字节副本 `china-20261102-preoverwrite-copy.json`(SHA256=`1b47f5478bb631e13d4dd56608f8ee9497758bbe85d2363eb82c455cbd2f6033`,与开轮清单一致)**先行入证据包**;覆盖后=`e5042498…`。`china_20261101.json` 等其余 11 文件字节不变(开/收轮清单对照)。

## 3. R-BLK-2 workflow 依赖一行修复 + CI 登记说明(F3-AC-03)

### 3.1 修复内容与理由

`git diff 02f1bad..尖端 -- .github/workflows/offline-tests.yml` **有且仅有一处变更**:

```diff
       - name: 安装被测模块import面所需的真实第三方依赖
         run: |
           python -m pip install --upgrade pip
-          pip install requests openai pandas fredapi feedparser finnhub-python tushare yfinance
+          pip install requests openai pandas fredapi feedparser finnhub-python tushare yfinance six
```

**理由(备案)**: six 是 tushare 1.4.29 真实 import 而上游未声明的依赖;上游 python-dateutil 4.0.0(2026-11-01 两次 run 之间发布)移除 six 传递依赖,CI 每次全新环境必然缺失(取证: run `41329974596`@`02f1bad`,53 套件 52 绿,唯一红=test_datafix_20261017,`ModuleNotFoundError: No module named 'six'`,登记于 `rounds/006/R005-BLK2-ci-dispatch-evidence.md`)。本修复属该 workflow 文件头自述原则"CI 必须安装被测模块 import 面的真实依赖"覆盖内的忠实补全——**不删除、不跳过、不弱化任何既有套件**(触发器/步骤/用例 glob/超时/其余依赖零 hunk)。

### 3.2 本地全套件(T 级工程自检,非 CI)

CI 等效环境(clone@`d9db19d`+空 data/,与 Actions checkout 同构)逐套件直跑: **54 个 test_*.py 全部 exit=0**(2026-11-01T17:53:44Z,含 test_p02_w5_fix2 全部 23 用例、test_datafix_20261017 亦绿)。**如实声明: 本机已装有 six,本地绿不能证明 CI 修复生效**;权威 CI 判定=操作者经 CHECKPOINT 机制对最终尖端 dispatch 的 GitHub Actions run。test_glm_live 本地为内部自跳过(exit=0),CI 侧按 workflow 显式排除,口径不变。

### 3.3 CI 登记(操作者侧,不入 DEV 文件)

执行Agent 无 dispatch 权限,零 CI 动作。Run ID/conclusion/headSha/时间戳由**操作者**在对最终尖端 workflow_dispatch offline-tests 后登记至轮次档案(`*-evidence.md`),供 Agent 4 以 gh 独立核验。预期: headSha=最终尖端、conclusion=success、53 套件全绿(含 test_p02_w5_fix2 23 用例)。

## 4. 范围/隔离/冻结纪律自检(F3-AC-04)

- **改动范围**: `git diff --name-status 02f1bad..尖端` = docs/P0_2_W5_FIX2_DELIVERY.md(更正,范围A)+ .github/workflows/offline-tests.yml(一行,范围D)+ docs/P0_2_W5_FIX3_DELIVERY.md(新增,范围A)——代码/测试/其他配置零 hunk;data/daily 为 gitignored 运行产物(范围C,开/收轮清单覆盖,唯一变化=§2.2 披露的同日覆盖)。
- **real_data_acceptance.py**: DEV 版 SHA256 全值 `01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b`,开轮登记,全程未变(本轮未触发条件分支,亦无任何运行时改动)。
- **Git 纪律**: 分支自 02f1bad 线性切出(T1 更正 commit → T3 workflow commit → T4 本文档 commit),未合并 main、无 force push、无 reset --hard、无 amend;ls-remote 实取: main=50b5d13d、dev/p0-2-w1=69d7fc71…、w2=14fe6e57…、w3=497b02c7…、w4=7c004c65…、dev/p0-2-w5=10207929…、dev/p0-2-w5-fix2=02f1bad… 全部与开轮一致不变(收轮再取,见证据包 OPEN/CLOSE-FORENSICS-FIX3.txt)。
- **LIVE/launchd**: 零写入零改动;只读隔离取证三项见 DEV-LIVE-ISOLATION-FIX3.txt(LIVE 脚本 SHA256=f9ca189c…≠DEV 且与 FIX2 轮登记一致=LIVE 未动;W5-FIX3 专属标记 LIVE 0 命中——唯一 `F3-AC-` 命中经逐行定性为 LIVE 内 P0 期修复FIX3轮历史验收编号,与本合同无关;launchd 配置零 DEV 引用)。
- **不重开/不动**: P0-1/W1~W4 不重开;P0-3/P1 未启动;无历史回补;无新增资产/采集器/付费源/凭证;R004/R005 DEFERRED 各项只登记未动。

## 5. R004-D1 笔误不复现声明

R004-D1(FIX1 交付文档 :130 引用 `…-4a19619.txt` 而实包为 `…-1020792.txt` 的文件名引用笔误)在本轮**不复现**: 本文档引用的每个证据文件名均与 FIX3 证据包实际条目逐一核对(方法: 文档内引用文件名 grep 证据包 `unzip -l` 清单;包内 SHA256SUMS 含全部条目哈希,引用文件哈希与正文登记值一致)。

## 6. 遗留与待批准事项(如实,不扩权)

- **W5 整体签发**: 本合同 PASS 不自动=W5 PASS。条件分支未触发→闭合路径须用户批准路径①(china 通道改造,已登记 PENDING-APPROVALS.md 排队中)后另拟 IA-P0-2-W5-RERUN 合同完成原 W5 门槛验证,再由 Agent 4 终裁。
- **待用户批准(本轮一律未执行)**: ①china 采集通道改造(备源/限流间隔/调用序变更);②对 china 尝试的任何重试或择时复跑;③历史回补;④合并 main;⑤LIVE 写入/launchd/生产部署。
- **U 级事项**: 最终尖端的 GitHub Actions CI run 由操作者 CHECKPOINT dispatch 取得(本会话执行Agent 零 CI 动作)——登记前该项为 U(未验证),不归责执行方。
