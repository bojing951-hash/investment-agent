# P0-2 W5-RERUN-4 正式重跑交付文档(R052)

- **合同:** IA-P0-2-W5-RERUN-4-AC-v1.0(FROZEN 2026-11-04 18:1x HKT,操作者依用户
  2026-11-01代批授权+2026-11-04方案B实批与"不等不拖"明示指令批准冻结)
- **执行:** Agent 3(执行Agent,R052),2026-11-04 10:16Z–10:5xZ(18:16–18:5x HKT)
- **基点:** 4561535067e996225eb8f99152d061d7ec116d1d(R051尖端,dev/p0-2-w5-emwin)
- **本轮性质:** R050 NV 三因修复后正式重跑(R051动态窗已修①EM钉死;②Coinbase经代理
  注入;③FRED T+1如实NV不阻塞阈值)→目标=overall=PASS exit=0 的 W5 达标判定件
- **结果一句话:** **overall=PASS,exit_code=0**——W5-RERUN-4 判定件产生
  (formal/attempt1_formal_20261104_r4),收盘守卫PASS,零FAIL

---

## ① 开工保险(合同R4-AC-01;全部机器件,2026-11-04T10:16Z)

1. **合同FROZEN**: 附录A合同全文本轮已注入执行提示词(与R050/R051不同,R051未注入),
   注入文本逐字落档证据包 git/appendix-A-injected-contract.md,
   sha256=4f78712e928fc9e7c20f5475313bbee2bddd6c548789d1160617d21a11ebe0cb。
   引擎侧存档原件(contracts/IA-P0-2-W5-RERUN-4-AC-v1.0.md)位于执行位不可达目录
   (环境事实,R051在案同象),无法与注入文本逐字节比对——如实登记,未见冲突。
2. **基点**: `git rev-parse HEAD`=4561535067e996225eb8f99152d061d7ec116d1d(=合同BASE-B4
   逐字同值);工作树净(opening-git-status.txt 仅分支行);当前支=dev/p0-2-w5-emwin。
3. **分支集**: `git ls-remote` 实取=origin 25支(机器件 opening-ls-remote.txt);
   与本地跟踪 refs/remotes/origin 逐支比对=25支全同值**零漂移**;关键支:
   dev/p0-2-w5-rerun=f124ef3b5a261b329fbbef9722026df23e2f7e7a(=合同§0注入值)、
   dev/p0-2-w5-emwin=4561535(=基点)、main=50b5d13(未动)。
4. **双预检(硬保险,不过→停;两项全过,console留档 isolation/PREFLIGHT-SUMMARY.txt)**:
   - ①EM只读免代理直连(curl --noproxy '*'): sh000001/sz399001 date=2026-11-04完结行
     存在,amount=953,265,155,867.10 / 1,084,429,058,169.67 元,均>6e11 ✓
     (与合同§〇锚定二操作者17:3x实测逐字一致);
   - ②Coinbase经代理(合同原文命令逐字): http_code=200(2xx) ✓。
5. 窗口语义: 开轮UTC 10:16Z=18:16 HKT>16:10→R051动态窗`_em_max_date()`应取
   2026-11-04当日,收盘守卫结构性可满足(预检①已在架印证)。

## ② 登记(合同§一.2;shasum -a 256 实取)

| 件 | SHA256 | 与契约关系 |
|---|---|---|
| scripts/real_data_acceptance.py | 01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b | =R032契约全值=R050登记,逐字一致,零改动 ✓ |
| scripts/china_market_collector.py | f3fff902b0175126d1960919fea2a3e7025a1a67fecad660963038dbf3934cee | =合同注入R051尖端值,逐字一致(含动态窗修复) ✓ |

证据域: /tmp/w5rerun4-evidence/{attempts,formal,git,isolation} 四子目录;
R050(/tmp/w5rerun3-evidence/)与R051(/tmp/w5emwin-evidence/)证据包全程只读。

**隔离开轮三项只读**(isolation/OPENING-REGISTRATION.md):
LIVE验收脚本SHA=f9ca189c5248199bb5acbc78b2a2c82d59c10e1c7c2c2d20bdaaa6105fbfe3eb
≠DEV ✓(与R050开/收轮同值=LIVE零变化);LIVE全库grep RERUN-4标记=0命中 ✓;
LaunchAgents grep investment-agent-dev=0命中 ✓。

## ③ 运行叙事(合同R4-AC-02;四源各恰1次,console全留档 attempts/)

**四源全跑,不带代理环境**(运行器meta逐件记 runner_proxy_env=NONE;
shell实测proxy env=NONE;global采集器内部`_setup_proxy()`为其固有代码,本轮零触碰):

| 源 | 脚本 | 起UTC | 时长s | exit | 关键产出 |
|---|---|---|---|---|---|
| china | china_market_collector.py | 10:19:54 | 429.2 | 0 | tushare index_daily 7调全拒(首调「5次/天」,后续「1次/小时」),闸门7次58.4–60.4s→六指数全落**R051动态窗EM回落** via=akshare_em **date=20261104**(series_last=2026-11-04当日完结行);成交额Tushare拒→akshare-em sh≈9532.65亿/sz≈10844.29亿(total≈20376.94亿,EM方案2);HK/ah date=2026-11-04 |
| macro | macro_collector.py | 10:20:00 | 48.6 | 0 | macro_20261104.json(HY OAS 3.43%关注/CCC 13.19%恐慌标签) |
| rate | rate_expectations.py | 10:21:00 | 135.3 | 0 | rate_economy_20261104.json/md |
| global | global_market_collector.py | 10:23:29 | 12.5 | 0 | 32/32成功零nan;BTC在途UTC日K(2026-11-04)剔除,completed_through=2026-11-03,retrieved_at=2026-11-04T10:23:41Z |

**收盘守卫(合同§一.6,attempts/attempt1_china_20261104.guard.txt 实值)**:
守卫(a) 取值行date=20261104(六指数+成交额全=20261104)→**PASS**;
守卫(b) EM amount全日量级 sh=953,265,000,000元>6e11 且 sz=1,084,429,000,000元>6e11
→**自洽;守卫总判 PASS**。R051动态窗修复在真实运行中生效
(R050同点=FAIL:EM钉死20261103)。

**验收直调(合同R4-AC-02b,零裁量,恰1次)**: 运行器以**进程作用域env**注入
命令行前缀代理(HTTPS_PROXY/HTTP_PROXY=http://127.0.0.1:7890 + NO_PROXY=
hq.sinajs.cn,api.stlouisfed.org,home.treasury.gov,fred.stlouisfed.org,localhost,
127.0.0.1)——**禁全局export(实测shell零proxy变量)、零写入DEV文件/env_config**;
参数与R050逐字同(--data-dir DEV data/daily + --out-dir 判定件目录,auto data-day);
25.2s,**exit_code=0**。代理通道实录: Coinbase BTC-USD/PAXG-USD证据文件两件落档
(R050同点=不可达NOT_VERIFIED);Treasury/FRED/sina走NO_PROXY豁免直连。

## ④ 判定件转录(合同R4-AC-03;formal/attempt1_formal_20261104_r4/)

四要素(run.meta.txt): HEAD=4561535067e996225eb8f99152d061d7ec116d1d(=基点,
worktree_dirty_files=0)/script_sha256=01e3f890…(同②)/UTC=2026-11-04T10:27:37Z
–10:28:02Z(25.2s)/**exit_code=0**;JUDGMENT-PIECE-MARKER.txt 在档。

- 验收数据日= 20261104(自动最新四源齐全日,lag=0)
- Gate A= DEGRADED | 事实77 | 质量{'PASS':61,'DEGRADED':12,'FAIL':0} |
  **core缺失 0** | 非核心缺失3项(MARGIN_BAL,SB_FLOW,SH_PE)
- **综合结果= PASS(exit 0)**;状态分布 {'PASS': 8, 'FAIL': 0, 'NOT_VERIFIED': 2,
  'NOT_COMPARABLE': 1, 'INSUFFICIENT_HISTORY': 1, 'SKIPPED': 0}
- 覆盖门槛(报告coverage): ust_pass=3✓(≥3) | market_pass=2✓(≥2) |
  external_pass_total=5✓(≥4) | recompute_pass=3✓(≥1) | recompute_complete=3✓ |
  零FAIL——与合同§〇锚定三达标算术逐项吻合

**八项check逐项原样转录**(check_id/判定/关键值/evidence_id):

| check_id | 判定 | 关键值(原样) | evidence_id |
|---|---|---|---|
| EXT-UST-2Y | PASS | 2026-11-02同日,4.59 vs 4.59,差0.0bp≤3bp | EV-TSY-2026 |
| EXT-UST-10Y | PASS | 4.91 vs 4.91,0.0bp | EV-TSY-2026 |
| EXT-UST-30Y | PASS | 5.28 vs 5.28,0.0bp | EV-TSY-2026 |
| EXT-BTC | PASS | 2026-11-03完结UTC日收盘vs同日Coinbase日K:77345.05 vs 77336.75,偏差0.01%≤0.5%(**经代理实录**) | EV-CB-BTC-USD |
| EXT-GOLD-F | NOT_COMPARABLE | PAXG现货代币≠COMEX期货连续,工具身份不同无基差/展期证据;参考偏差0.33%(4054.6 vs 4041.46)仅披露不参与判定(PAXG数据经代理取得) | EV-CB-PAXG-USD |
| EXT-SHCOMP | PASS | 2026-11-04同日收盘口径,3686.17 vs 新浪3686.1725,偏差0.0%≤0.3%(报价时间15:35:30) | EV-SINA-SH000001 |
| EXT-SPX | NOT_VERIFIED | FRED无2026-11-03同日观测(realtime=2026-11-03,最近=2026-11-02[7541.4]=T+1口径);日期不匹配不得判PASS | EV-FRED-SP500 |
| EXT-WTI-F | NOT_VERIFIED | 参考源不可达/无该日数据(诊断见外部证据) | EV-FRED-DCOILWTICO |

**复算三资产三期逐项原样转录**(formula=(期末/基准−1)×100,期前收盘基准,tolerance 0.01pp):

- SPX=**PASS完整三期**(0.0pp×3): WEEK=MTD=−0.1471%(基准2026-10-30=7580.069824,
  期末2026-11-03=7568.919922);YTD=+10.5678%(基准2025-12-31=6845.5)
- GOLD_F=**PASS完整三期**(0.0pp×3): WEEK=MTD=+3.9934%(基准2026-10-30=3898.899902,
  期末2026-11-04=4054.600098);YTD=−6.5997%(基准2025-12-31=4341.100098)
- HSI=**PASS完整三期**(0.0pp×3): WEEK=MTD=+2.6834%(基准2026-10-30=23294.42,
  期末2026-11-04=23919.5);YTD=−6.6758%(基准2025-12-31=25630.54)
- SHCOMP=INSUFFICIENT_HISTORY: WEEK=MTD=+2.4215%一致0.0pp(基准2026-10-30=3599.02,
  期末2026-11-04=3686.17);YTD序列不含上年末观测,已核2/3期不冒充完整PASS
  (R050同象在案=china指数series年窗语义,非本轮回归)

报告存活件: real_acceptance_20261104_1828.json/.md/.log + evidence/6件外部原始证据
(Treasury年度CSV/Coinbase BTC-USD/Coinbase PAXG-USD/sina sh000001/FRED SP500/
FRED DCOILWTICO);FRED证据=响应体JSON,api_key仅存在于请求URL,实测
grep未脱敏api_key模式=0命中,凭证明文零出现 ✓。

## ⑤ data/daily 数据清单(先/后全量SHA256)

24→24,**新增0删除0**;同日(20261104)6件覆盖写: 4哈希变(china_20261104.json/
global_20261104.json/global_20261104.md/rate_economy_20261104.json)+
2字节不变mtime为证(macro_20261104.json/rate_economy_20261104.md——上下午两次采集
FRED观测值同日不变,内容逐字节一致);其余18件历史件字节不变(mtime为证,采集器固有
多读写盘语义)。机器件: data_daily_{prerun,postrun}_inventory.txt +
data_daily_round_writes.json。

## ⑥ 偏差与如实声明

1. **SPX/WTI_F=NOT_VERIFIED=FRED口径如实**: FRED realtime 2026-11-03最高观测=
   2026-11-02(T+1),无2026-11-03同日观测;WTI_F参考源DCOILWTICO不可达/无该日数据。
   两者不参与达标算术(external真PASS=UST×3+BTC+SHCOMP=5≥4已足),零凑数零改口径
   (合同§〇锚定三预期即如此)。
2. **GOLD_F=NOT_COMPARABLE**: PAXG现货代币≠COMEX期货连续(工具身份不同),脚本内置
   诚实标签判NOT_COMPARABLE,参考偏差0.33%仅披露——合同锚定三「GOLD_F经代理可能PASS」
   的口径前提是可比;实际不可比→如实NV级,不为凑数改判。
3. **SHCOMP复算=INSUFFICIENT_HISTORY**: YTD历史不足(序列不含上年末),已核2/3期;
   R050同象在案(china指数series年窗语义),非本轮回归,不冒充完整PASS。
4. **Gate A=DEGRADED(非PASS)**: 非核心缺失3项(MARGIN_BAL,SB_FLOW,SH_PE)+
   质量12项DEGRADED;core缺失=0满足进入条件(PASS/DEGRADED均可进验收,FAIL才阻断)。
5. **附录A合同哈希口径**: 4f78712e…为提示词注入转录文本的sha256,引擎侧存档原件
   执行位不可达无法比对(R051同象如实登记)。
6. **tushare限流持续在案**: index_daily 7调全拒(首调「5次/天」,后续「1次/小时」),
   权限类拒3调(index_dailybasic×3)+1调(moneyflow_hsgt);全部经R051动态窗EM回落
   自动兜底,与R050同象,属外部结构性配额耗尽非本轮缺陷。
7. 预检/验收两次免代理EM直连与一次经代理Coinbase调用均为只读取证,非判别实验
   (零tushare探针)。

## ⑦ CI 说明(合同R4-AC-06)

- 执行侧零dispatch(记忆在案: 执行Agent无dispatch权限,offline-tests.yml仅push/PR→main
  +dispatch触发,dev分支push不自动跑)。
- 本轮代码零改动(白名单恰1新增本文档),CI预期=54套件全绿(与R051 CI 41811559827
  success@4561535同构基点;新增docs文件不入测试)。
- **待操作者**: dispatch CI + 登记字面值(run ID+headSha全值+conclusion+套件数)
  +Agent 4审计;PASS后进W5终裁R2程序包(合同§五后链)。

---

## 自检对照(R4-AC-01~06)

- R4-AC-01 开轮保险+双预检: ✓(①合同/基点/分支集机器件;②EM行amount>6e11×2与
  Coinbase经代理200,console留档,两项全过后开跑;反例零:预检过后才首调采集器)
- R4-AC-02 四源+验收(代理恰锁): ✓(四源恰1次不带代理runner_proxy_env=NONE×4;
  验收直调进程作用域env前缀+NO_PROXY五域豁免,禁全局export实测shell零proxy;
  china=20261104完结行守卫PASS;改脚本=零)
- R4-AC-03 判定件: ✓(四要素+JUDGMENT-PIECE-MARKER;core缺口=0;八项+复算原样转录
  见④;overall=PASS/exit=0原样)
- R4-AC-04 隔离: ✓(LIVE/launchd三项只读×2=开轮+收轮;基线各支尖端不变见⑧收轮;
  R050/R051证据包只读)
- R4-AC-05 交付: ✓(本文档七项+恰1笔commit推送;证据包八类+SHA256SUMS+zip;
  凭证明文零出现,grep实measured)
- R4-AC-06 CI: 执行侧零dispatch✓;操作者dispatch+登记=待办(如实)

## 三态自判

执行合规(R4-AC-01~05全过,AC-06执行侧义务已尽、操作者侧待办)+判定件
**overall=PASS & exit=0** → 按§四对照=**PASS臂**(独立验收主体=Agent 4,
本自判非终判)。
