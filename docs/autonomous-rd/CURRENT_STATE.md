# CURRENT_STATE — 最新研发状态

> 研发面恢复入口(新会话先读这里,再读 `RESUME.md`)。
> 引擎运转面(LIVE/轮次/合同)不在本档——见 `~/agent-loop/STATE.md` 顶部速览。
> 更新纪律: 每完成一个重要研发阶段必须更新本档(进度/测试与审计结果/分支与 Commit/下一步)。

## 权威快照: 2026-11-12 R21 检查点 · 持续执行验证(Charter 10 阶段二)

> **本节=唯一当前态入口**(Charter 10 §3.1)。下方历史快照仅供追溯,以本节+Git HEAD 为准。
> 核对法: 本节 `baseline=` 机器行必须是 HEAD 祖先(`git merge-base --is-ancestor <baseline> HEAD`);
> 一致性门 `python3 scripts/rd_state_consistency.py` 六项全绿方可开工;不一致时禁止开发,先恢复状态(§3.2)。

- **基线(机器面)**: baseline=4829b64c4c0162c87d8f501365bad64b3d9d7af4(检查门§①解析本行;rd_checkpoint.py 收口时自动刷新)。
- **基线**: main = dfad40e(v0.16.0-alpha 面,R20 状态管理机器化)。**Charter 10**: docs/autonomous-rd/CHARTER_10_RECTIFICATION.md(用户总指令原文)。
- **真实进度**: R9-R20 已毕并入(R20=状态管理机器化: 六项门+finalize 管线+恢复验收);v0.15.0 已发布+LIVE 已部署(9e85699);**R21 持续执行验证(Charter 10 阶段二)毕**——§4.4 七项矩阵 6 PASS+1 PARTIAL(无头压缩恢复无实例子面),零冒认;防死循环顾问+finalize 事故弧回归锁+候选钩子包落地。
- **验收层状态(按 Charter 10 §八重开)**: 九 PASS + AC3 PARTIAL 为**待复核旧结论**——受影响项重验中: AC3(金融正确性缺口)/AC6(L3/L4 produced=False)/无人值守证据(阶段二已补强: R21 七项矩阵,见 R21_CONTINUOUS_EXECUTION_AUDIT.md);其余 PASS 项维持至复触及。
- **当前任务**: 阶段二(R21)已毕待操作者合并;下一轮=**阶段三 金融正确性**(5.1 汇率方向/5.2 到期新鲜度/5.3 标签-证据绑定/5.4 前视偏差,先复现后修);阶段四~六见 CHARTER_10 §十一。
- **权限变化(Charter 10 §十)**: LIVE 生产修改自此需用户明确指令,不再随波次自动同步。
- **检查点(R21·2026-11-12)**: 持续执行验证+防死循环;候选钩子包(ops/hooks-candidate/)待操作者席安装;LIVE 观察: 明日 daily 首跑 v0.15.0 面(daily exit1/weekly exit2=已知 ZQ 族缺口,11-14 观察钟)。

### 任务台账(机器维护: scripts/rd_checkpoint.py 收口;已毕任务只进 ITERATION_LOG/RESUME 存档,永不回台账)

| ID | 状态 | Git证据 | 说明 |
|---|---|---|---|
| T-R21-1 | 待合并 | dev/rd-r21-continuous-exec@4829b64 | R21 持续执行验证(Charter 10 阶段二): §4.4 七项矩阵+防死循环顾问+finalize 事故弧锁+候选钩子包;报告=R21_CONTINUOUS_EXECUTION_AUDIT.md |

### [历史快照·R15 视角,已被上方权威快照取代]

- **R15(AC 覆盘轮第二波)已完成**: 分支 `dev/rd-r15-ac1-ac2-ac8` @(本 commit,
  基于 main dc4c57a;独立 worktree /tmp/r15-wt,防撞车纪律;真实数据只读引用
  dev 树,零写入)。按 PRODUCT_GOAL §八原文定义独立复核三 AC,证据=本席亲跑
  命令+亲算数值:
  **AC1 真实全球宏观全景→EXECUTED**(终判 PASS 候选): registry v2.8.4 110
  指标零缺 source/source_symbol(US57/CN18/GLOBAL12/EA11/JP8/HK4);快照 v2
  103 facts 全带值/单位/观测日/as_of/源;md 展示面=指标|值|单位|观测日|周变化|
  身份备注|质量+8 通道源状态表+Gate A 5 noncore_missing 逐项带因+P2 台账;
  derived week/mtd 窗含 basis+formula 71/103(余 32 月频水平显式示—);
  口径注记=v2 md 缺失措辞为 R11 三分支归因之前的旧口径(不可变快照保留,现行
  代码更细)。
  **AC2 真实机构研究→EXECUTED**(终判 PASS 候选): 17 档四要素(机构/报告/
  发布时间/原始内容)17/17 零缺,schema 1.1;access_level 逐档披露
  (public_full10/summary6/headline1)+source_url 17/17,15 机构;明示 vs
  AI推导=结构强制(view_store.py:163-201 attribution 枚举硬拦截,112/112
  core_views=institution_stated,AI 推导隔离于 VP sidecar 独立层 17/17);
  C 型首验窗 2026-12 日历门如实未判。
  **AC8 研究可复核→EXECUTED**(终判 PASS 候选): 三层链亲验——QB-001
  digest_snapshot=d912054bb6e154a3 按正口径(canonical JSON sha256[:16])亲算
  当前 v2 逐位一致(注:内容指纹,非文件字节);SPX 11-11 收盘 7609.63+周基准
  7376.85 物理在场于 global_20261112.json;独立复算 4 组全中(ZQ−DFF=
  4.185−3.88=+0.305pp 实证 correction-1 更正正确,档案原值 0.295 为算错;
  SPX 周 +3.16%;NDX 周 +5.2942%;REAL_10Y 恒等 4.88−2.20=2.68 精确)。
  N1 兼证 AC8 条款②闭环: 审计发现错→评注更正→结论方向不变的越界判断。
  **移交 R16**: ①AC6 行「AC7 未跑」注记过时须更新;②QB-005~008 零Key边缘
  档归档说明注记;③AC4+AC5 正式验证(矩阵最后两个 NOT_VERIFIED)。
  报告=`docs/autonomous-rd/R15_AC1_AC2_AC8_VERIFICATION.md`。

## 快照: 2026-11-12 (HKT, R17 零Key套件 tempdir 隔离·fork 开发)

- **R17(R16 移交项①代码波)已完成**: 分支 `dev/rd-r17-zeroykey-tempdir`
  @(本 commit,基于 main 889a221;独立 worktree /tmp/r17-wt)。
  **修复**: `ia_cli._ARCHIVE_DIR` 注入缝扩环境变量形态 `IA_ARCHIVE_DIR`
  (未设置严格 None=生产路径,默认行为零变化——A1 子进程实证;生产/launchd
  均不设此变量);零Key套件 §4 save/list 全走 tempdir,新增 4b(落 tempdir
  双档在场)/4c(生产 query_history 文件集跑前后逐位一致)断言;批2 WI6
  "不引入环境变量面"决策由 R17 修订,理由注记在 ia_cli.py:45-52。
  **新套件** `tests/test_rd_r17_zerokey_tempdir.py` 7 判三面全绿(seam 解析/
  save 分支 B1-B4 合成快照 2099 段 gitignored 路径 finally 清理/拒存分支
  C1)。零Key套件 18✅ rc=0。
  **存量处置**: 16 件空档 append-only 保留注记不删,
  P2_DATA_GAP_LEDGER 三之五+REMAINING_ISSUES P2-9 已标已修。
  **worktree data/ 机制**: gitignored 不检出(仅 3 个历史强制加档文件在),
  data/research 全程未创建;合成快照仅借 daily 落位即时清理。
  **移交下一轮**: 终判覆盘轮材料包(十行终判+日历门 F=2026-12-05/
  六标签 2026-12 呈报用户裁定席);LIVE 部署脚本 /tmp/deploy_v0141_live.py
  待用户终端跑。**波次毕,待操作者合并**。

## 快照: 2026-11-12 (HKT, R16 AC4+AC5 验证+AC6 收口·fork 开发;矩阵收满)

- **R16(AC 覆盘轮第三波)已完成**: 分支 `dev/rd-r16-ac4-ac5-ac6` @(本 commit,
  基于 main bde1ab1;独立 worktree /tmp/r16-wt;真实数据只读)。三 AC 亲验:
  **AC4 经济机制与历史研究→EXECUTED**(PASS 候选)——analog 真跑 v2 快照(扫描
  1871 月/73 有效/5 独立簇;rank-1 距离本席加权 L2 亲算 0.326434 vs 引擎
  0.326433 六位一致;四判据巧合旗标现役全开;vintage/事件研究/发布滞后三面
  诚实拒答);aftermath 非预测分离+起止观测日随行;E1/E2/E3 四层标注+--lag
  禁写"驱动";数据深度对账全中(JP_POLICY_RATE 1985-07 起 n=495/SPX_CAPE
  n=1750/FRED 月频 119-120/USDJPY 日频 2601/HY_OAS 36 月受限如实)。
  **AC5 独立研究结论→EXECUTED**(PASS 候选)——QB-032 亲读六要素全中(到期判
  2/17 如实/分歧逐名/未知 12 条不填空/预期差附口径警告/S1-S4 五行=证伪条件
  +竞争环);引数复算命中(compare 亲跑 pearson 0.42198 vs 档案 0.4220)。
  **AC6→EXECUTED**(收口: AC7 已执行补齐原差距+四页工作台零模型调用纪律
  36✅;剩余=真实案例积累+终判留席)。
  **移交 D 根因查明**: QB-005~008「零Key矩阵问题」16 件=零Key套件 §4 在有快照
  本地/无头 dev 树真写生产档案(CI 干净克隆不受影响);诚实空档非伪造;修复候选=
  tempdir 注入缝,REMAINING_ISSUES P2+1;存量保留注记不删。
  **矩阵=九项 EXECUTED+AC3 PARTIAL**(C 型首验窗 2026-12 日历门),全部终判
  留用户裁定席。报告=`docs/autonomous-rd/R16_AC4_AC5_AC6_VERIFICATION.md`。
  R17 候选: ①零Key套件 §4 tempdir 隔离(代码波)——**[R17 已毕,见上快照]**;
  ②终判覆盘轮材料包(十行终判+日历门状态一并呈报用户)。

## 前一快照: 2026-11-12 (HKT, R14 AC10 红线终审+USER_GUIDE 代理落档·fork 开发)

- **R14(AC 覆盘轮第一波)已完成**: 分支 `dev/rd-r14-ac10-redline` @(本 commit,
  基于 main 7a58f8f;独立 worktree /tmp/r14-wt,防撞车纪律)。
  **任务A=AC10 红线终审**(只读五面+九红线映射,报告
  `docs/autonomous-rd/R14_AC10_AUDIT.md`): 厂商词(权威守卫
  test_charter5_vendor_residue_guard 5/5✅+72 文件残余逐类判读全豁免类)/
  个人路径(3 命中=1 审计引用+2 负向守卫)/密钥(赋值形 0 命中,sk- 全 FAKE
  明标)/档案真实性(dev 树 195 文件=97 记录+97 full+1 更正,mode/ir_stage/
  snapshot_id 零缺失,零合成冒充,零重复)/源披露(registry v2.8.4 110 指标
  全 source+source_symbol;11 快照逐 fact 注册+带源)+交易执行面
  (place_order/broker/ccxt 等 0 命中)+端点清单(全免费公共源,Bloomberg 仅
  公开 RSS)。**终判: 五面全 PASS 零违规**;AC10 NOT_VERIFIED→EXECUTED
  (终判=PASS 候选留用户裁定席)。
  **任务B=USER_GUIDE 代理落档**(R12 根因): Q2 扩为「网络与代理(境内网络
  必读)」——症状识别(腾讯 WAF HTTP200+空数据/yfinance 429)+根因(macOS
  系统代理不进 shell/launchd)+两姿势(shell export/wrap 脚本)+launchd
  plist 模板补 EnvironmentVariables 两键;§1 环境要求同步指向。零代码改动。
  **观察登记**(非违规): GLMRecorder/GLMDraft 测试替身类名存活于 tests/
  (守卫模式清单未收录,tests/ 外零命中);DEEPSEEK_* 死通道常量为
  REMAINING_ISSUES P1 既有登记维持观察。
  **测试**: 全仓套件(结果见 ITERATION_LOG R14 行);首次跑批翻车=日志目录
  未建即重定向(0 套真跑),建目录重跑为准。
## 前一快照: 2026-11-12 (HKT, R13 japan 通道 source_key 补接轮·无头自主执行)

- **R13(R11 审计 MINOR 收口,RESUME R13 候选②)已完成**: 分支
  `dev/rd-r13-japan-source-key` @`f242c63`——**注意: 本分支含并发 AC9 会话
  (自号 R12)的 9de4cc8+13e518e+fadba31**(其合并误落于本分支——彼时主树正
  检出本分支;两波次文件面不相交,叠加无害,合并 main 时一并落交操作者裁量;
  main 现仍=12c3c0f)。
  **根因**: japan 通道 4 指标(JP_POLICY_RATE/JGB2Y/JGB5Y/JGB10Y)注册表无
  source_key,且 japan_rate_collector **不持久化**子源级 sources_status(失败
  仅 alerts 字符串);兜底文案"档内无记录"在「注册表缺映射」「纯重验未读档」
  两种断点下失准(未读档却归咎档内)。
  **修复三件**: ①japan_rate_collector 顶层增子级 sources_status(键
  MOF_JGBCME/FRED_POLICY 与 jp 采集器同上游源词汇一致,真实档 jp_20261112
  佐证;EXACT=取数解析出有效观测/READ_FAIL=获取或整体解析失败;列级坏值仍
  EXACT 由 alerts 披露;retrieved_at=尝试时刻语义;旧档无该节不受影响)
  ②registry **v2.8.3→v2.8.4** 接线 4 条(JP_POLICY_RATE→FRED_POLICY,
  JGB 三期限→MOF_JGBCME;110 条/108 active/通道零变动)③recompute 兜底
  话术**按证据链断点三分支归因**(注册表未登记键/未提供采集目录/档内无
  记录),不再一律归咎档内。**契约零变动**(纯话术层)。
  **测试**: 新套件 `tests/test_rd_r12_japan_source_key.py`(按立项时号命名,
  轮次实为 R13)25 判定绿;11 套件版本锁/话术断言随升(无弱化,审计逐行核);
  **全仓 tests/ 133 文件=132 exit0+1 环境性 FAIL**(test_p0_baseline_lock_
  equivalence 的 worktree 清单断言测到并发 AC9 会话活 worktree /tmp/r12-wt,
  R7 期同类先例=环境性非回归;审计已核该断言代码位置佐证)。
  **真实数据复证**: 真实快照 20261112_v2/20261110_v5 改前(12c3c0f)改后双跑
  ——effective/core_missing/noncore_missing/overall 全零变动;detail 话术差
  恰 2 处=无 source_key 指标(CN_OMO_7D/CN_SF_FLOW)归因精确化。
  **独立审计已收口**(未参与开发 general-purpose 席,四维对抗: 代码正确性
  [键词汇/五场景+17 项边界对抗全绿/三分支无误分类]/诚实纪律[无失败标成功
  路径,老档如实兜底]/契约不变性[真实快照双跑逐字段全同,detail 差恰为归因
  变体]/测试真实性[变异测试双红证明锁有牙,11 随升无弱化]=**四维全 PASS,
  零 BLOCKER 零 MAJOR 零 MINOR**;2 NIT=①data_dir 空串理论角落走档内分支
  ②三期限列全坏值时"采集遗漏"措辞与列级真因略有张力[设计取舍已 docstring
  明示]。终判=**可并入**)。**CAPABILITY_MATRIX 无差距变动**(披露精度硬化)。
- **R13 波次毕,待操作者合并发布**(与 AC9 波次同分支叠加,见上注)。

## 前一快照: 2026-11-12 (HKT, R12 AC9 干净环境全链覆盘轮·fork 开发)

- **R12(AC9「真实用户可用」NOT_VERIFIED→EXECUTED)已完成**: 分支
  `dev/rd-r12-ac9-clean` @`9de4cc8`+docs(自 main=12c3c0f 切出,含 R11 面)——
  **①安装器 --force 坑修复**: 根因=`local_modifications()` 仅比对当前源树,
  源树 git 拉新后**未动过的旧装机面**被误判"用户修改"逼 --force(首发安装
  无此坑,实证);修复=`matches_source_history()`(装机树逐文件 git blob sha1
  vs 源目录近 64 提交 `git ls-tree -r` 比对,任一历史版本逐字节一致⇒幂等刷新
  +`stale_version_refreshed` 旗,不备份不逼旗标;真修改仍拒/--force+.bak;
  卸载同语义;非 git 部署保守回退 v1.1 语义);macOS realpath 归一坑(realpath
  (SOURCE) 须对齐 git toplevel,否则 relpath 跨符号链接 git log 过滤必空)。
  套件 `tests/test_rd_r12_installer_stale.py` **16/0**+skill_installer 回归
  **32/0**;SKILL_GUIDE v1.2 话术随升。
  **②干净环境七步链**(/tmp/r12-clean 全新 clone,非 worktree): 安装零旗标
  verified=ok → 配置(.env chmod600 三 key 只读注入零回显;零 Key 面=doctor ok
  +research 诚实拒答 no_snapshot 不造数) → 更新首轮 **10/15 Gate A 拒**
  (core_missing HSI/HSCEI;根因链: 腾讯 ifzq 对 count=2600 深窗 HTTP200+空
  数据[WAF 静默拦,≤320 正常,设计不降级凑短窗]+yfinance 直连 IP 当日 429;
  **LIVE 同日同败 core_missing 逐字一致=环境面铁证非副本缺陷**)→ 补
  HTTPS_PROXY env(系统代理 127.0.0.1:7890 已在,shell 不自动继承;恢复代码
  注释"境外源走代理"设计姿态)+`--allow-revision` 同日修订 → **15/15 exit 0**
  (955.6s;快照 v2 DEGRADED core 0 缺;HSI=24104.44/HSCEI=8091.68 真值入档;
  原版 FAIL 快照保留) → 一键研究两问(自然语言面 11 步 ok[S4/S5 零词面命中
  诚实跳过零模型不语义翻译];指标面 **14 命令全 executed**,L1 2 行证据) →
  research-map 十问(views/archive 空面如实注"干净 clone 常态") → 追溯 3/3
  (SPX/HSI/NIKKEI225 快照值→源档命中→sha256 链,快照 v2 sha=5ec4f9ab…) →
  归档 **QB-20261112-001**(绑 v2 快照,record/full 双视图回读逐字一致)。
  证据档: /tmp/r12-clean/evidence_log.md(七步全真实命令+exit+输出节选)。
  **③登记**: AC9=EXECUTED(终判留 AC 覆盘轮不自动 PASS);用户文档面发现=
  **shell 启动管线须带 HTTPS_PROXY**(macOS 系统代理不自动进 shell env;
  待补 USER_GUIDE,本轮不改代码);--force 坑登记面=FINAL_ACCEPTANCE AC9 行+
  SKILL_GUIDE(均已收口;OPEN_ISSUES 原无此条目,如实注记)。
  **边界**: 零 push/零 merge/零 tag/零 LIVE 触碰/零付费 API/密钥零回显;
  报告零厂商词零个人路径。

## 前一快照: 2026-11-12 (HKT, R11 子源级注记细化轮·无头自主执行)

- **R11(Gate A noncore_missing 子源级注记细化,RESUME 3①=P2 台账 R10 候选①)
  已完成**: 分支 `dev/rd-r11-subsource-missing` @`1d135d7`(自 main=14b1590
  切出;操作者已合并 R10 并发布 v0.13.0-alpha)——
  **根因**: 「来源文件在场而指标缺席(采集遗漏)」为文件级泛化文案,BBK 源站
  断连(READ_FAIL)/白名单域未采(MISSING)这类诚实子源缺席被误标"采集遗漏";
  ea/jp 采集器日档已持久化子源级 sources_status,信息在档引擎未用。
  **修复**: registry **v2.8.2→v2.8.3** 新增可选字段 `source_key`(指标→采集档
  内子源状态键,接线 7 条: ECB_DFR/ECB_MRO/BUND_10Y/BUND_2Y/EA_HICP_YOY/
  JP_CPI_TOKYO_YOY/NIKKEI225);`_channel_subsource_map`(可信路径+sha256 一致
  才采信,只读不加信,单次重算共享缓存)+`_missing_reason_file_present`
  三分支分类: 子源非 EXACT=子源缺席(非采集遗漏)/子源 EXACT 而缺席=采集遗漏
  (采集器已取到而事实未生成)/证据不可得=诚实兜底「采集遗漏或子源缺席不可
  区分」(不再无证据断言"采集遗漏")。**契约零变动**: noncore_missing 成员/
  Gate 状态/门核验链不变(套件[5]对照锁+真实快照改前改后双跑复证)。
  **测试**: 新套件 `tests/test_rd_r11_subsource_missing.py` 24 判定绿(注册表
  面/READ_FAIL·MISSING·EXACT 三态/兜底两路/契约锁/单元面/MD 渲染);
  版本锁 10 处/9 文件随升+话术断言 4 处随升;**全仓 tests/ 131 文件
  131 exit 0**(基线 130+新 1,零环境性 FAIL)。
  **真实数据复证**: 真实快照 20261112_v2/20261110_v5 改前(14b1590)改后
  双模块同参 recompute——effective/core_missing/noncore_missing/gate_status
  全零变动;话术分化正中诉求: BUND_10Y/2Y→子源缺席(ea 档 BBK=READ_FAIL)/
  JP_CPI_TOKYO_YOY→子源缺席(jp 档 MISSING)/CN_OMO_7D/CN_SF_FLOW→诚实兜底。
  **独立审计已收口**(未参与开发的 general-purpose 席,四维对抗: 代码正确性
  [自写 33 项对抗测试含 FALLBACK 旧档/sha 缺失/路径成分/缓存串扰全绿]/
  诚实纪律[7 条 source_key 与采集器档内键逐一核对]/契约不变性[静态+动态
  8 份真实快照×双模式 15 字段零失配+下游 7 消费点无比对 detail 断言]/
  测试真实性[变异测试证明契约锁有牙]=**四维全 PASS,零 BLOCKER 零 MAJOR**;
  MINOR=japan 通道 BOJ_POLICY_RATE/JGB_* 未接 source_key 时兜底文案"档内无
  记录"失准(实为注册表缺映射,方向保守零裁决影响未触发,登记台账后续补)
  /NIT=词汇表外子源状态串仍入"源端不可得"分支[原始值已内插,无害]。
  终判=**可并入**)。**CAPABILITY_MATRIX 无差距变动**(披露精度硬化,非覆盖面
  增量)。
- **R11 波次毕,待操作者合并发布**(无头权限面无推送能力);v0.13.0 LIVE
  同步仍待用户终端亲跑或加白名单(R10 轮遗留,分类器拦)。

## 前一快照: 2026-11-12 (HKT, R10 tushare 月度缓存轮·无头自主执行)

- **R10(采集器级缓存硬化,RESUME 2②)已完成**: 分支 `dev/rd-r10-tushare-cache`
  @`68469f5`(自 main=3fcf263 切出)——
  **根因**: tushare `cn_cpi`/`cn_ppi` 同 api 1 次/分限流,午夜窗自采+流水线=
  两独立进程同分钟各拉一次→第二次必拒→cpi_yoy/ppi_yoy 假性缺席→Gate A
  误拒(生产 07:00 单跑不受影响);`_index_daily` 进程内闸门护不到跨进程。
  **修复**: 文件级跨进程响应缓存 `data/cache/tushare_monthly_{api}.json`
  (TTL 600s 命中免直连+♻️日志披露;`.tmp.{pid}`+`os.replace` 原子写;NaN→null
  严格 JSON;api 名白名单防路径注入)。**纪律保持**: 仅同窗去重不做陈旧
  回退(直连失败+陈旧档在场→仍如实缺席,t113 锁);仅可解析响应入缓存
  (列漂移零缓存档,t114 锁);缓存读写失败=透明跳过;输出三字段契约与
  源标签 `tushare_pro` 零变动。
  **测试**: 新套件 `tests/test_rd_r10_tushare_monthly_cache.py` 42 判定绿
  (纯函数 TTL 闭界/坏档六态/序列化保真+集成面同窗二拉零直连场景+契约锁);
  wp_e 29/29(测试密闭化: `_run_fetch_macro`+t60 缓存目录指一次性临时目录,
  R5 教训防套件间经真实 data/cache 串扰);**全仓 tests/ 130 文件批跑
  130 exit 0**(基线 129+新 1;R7 期的环境性 worktree FAIL 本轮不复现=
  再证环境性)。
  **独立审计已收口**(未参与开发的 general-purpose 席,四维对抗: 代码正确性/
  不做陈旧回退纪律/测试真实性含双序连跑/红线全过=**四维全 PASS,零
  BLOCKER 零 MAJOR**;MINOR-1 TTL 内被外部篡改档→最长 600s 诚实缺席[非错
  数据,可接受]/MINOR-2 冷启动同瞬双拉仍可撞限流[本修收窄误拒窗非彻底
  消除,已如实记台账];2 NIT[crash 残留 .tmp 无清扫/测试 mkdtemp 不回收,
  无害]。终判=**可并入**)。**CAPABILITY_MATRIX 无差距变动**(可靠性硬化,
  非覆盖面增量)。
- **R10 波次毕,待操作者合并发布**(无头权限面无推送能力);v0.12.0 LIVE
  同步仍待用户放行(R9 遗留,分类器拦)。

## 前一快照: 2026-11-12 (HKT 凌晨, R7 AC7 真实端到端首跑完成)

- **R7(AC7 三任务+一开放题)已完成**: 分支 `dev/rd-r7-ac7-e2e`(自 main=a22a2b7 切出,
  worktree /tmp/ac7-wt)——
  **数据面修复(首跑前置)**: 00:16 快照 v1 Gate A=FAIL(HSI/HSCEI core 缺席=午夜采集双通道
  皆阻: 腾讯 WAF 拦 2600 根深窗+yfinance 限流; PPI 丢)→global 采集 34/34+china 重跑+腾讯
  2000 根(≈8 年, 经 HK_INDEX_HISTORY_BARS env 缝, 窗口缩短如实披露)+PPI 真实复拉
  (5.0@2026-09-30)→**research_snapshot_20261112_v2, Gate A=DEGRADED, core 缺失 0**,
  事实 103(72 PASS/13 DEGRADED/0 FAIL)。
  **任务A**: `ia_cli research-run --fanout --archive` 十一步 16 命令真跑(S8=诚实 unmapped:
  接地问答仅支持四类利率问题, 全景问题走 Agent 装配; S4/S5 零实体映射如实跳过)+
  13 节终报告(**13/13 节无空置**, 承 QB-010 结构, v2 面全数字更新)=QB-20261112-001。
  **任务B**: 17 档/15 机构矩阵(较 QB-033 +6 档: PBoC/OECD/BIS/UBS/Vanguard/MSIM-1106)
  +M 表八问拆解+分歧矩阵 5 轴+**新鲜 CPI/PPI 只作更新评注不重写历史档**(发现: 上游通胀
  PPI+5.0 在 17 档机构面完全空白=研究机会缺口登记)=QB-20261112-002。
  **任务C**: view_verifier 三型×17 档+`view_plausibility --build-all` 17 件 VP sidecar
  重建@v2(as_of 20261112)——**B 面 143 行 86 行非零移动, 23 行机械判定(11 against/
  5 supports/7 neutral, R5 覆盖面后首次批量出判)**; C 层 133 假设全未到期/不可机器判
  (首验窗 2026-12)=如实, 观点级六标签 17/17 INSUFFICIENT_EVIDENCE 维持契约;
  CN CPI/PPI 无假设映射=NOT_MACHINE_VERIFIABLE 缺口如实=QB-20261112-003。
  **开放题(现场生成防适配)**: 金油比 12 个月压缩 32.3% 后仍处 10 年 80.1 分位(45.63,
  剔负油日口径)——compare 滚动 60 相关 −0.3263(全窗 +0.022 近零)+6 段 Episode 条件前视
  (n=6 小样本如实, 后 63 日 SPX 中位 +8.45%/VIX −18.61%, 禁外推)+「能源→通胀预期→金」
  传导缺席双确认=QB-20261112-004。四 QB 全显式绑 v2 快照指针。
- **测试**: 执行轮零引擎代码改动;全套回归 **129 文件=128 exit0+1 环境性 FAIL**
  (test_p0_baseline_lock_equivalence 的「worktree 清单回零」断言检测到本 fork 自身的
  活 worktree /tmp/ac7-wt=环境性;同套件干净 clone 31/31 绿=非回归,CI 基线 129 绿佐证)。
- **AC7=EXECUTED**(FINAL_ACCEPTANCE 已记; 终判留 AC 覆盘轮)。**下一波=R8 独立验证轮**
  (他席对 QB-001~004 复算, 开发者不自验)。

## 前一快照: 2026-11-11 (HKT, R5+R6 已发布 v0.11.0-alpha·LIVE 已同步)

- **发布态**: main=**9051e7f**(merge R5+R6),tag v0.11.0-alpha,Release 441903695,
  CI 43052903525 绿=**基线129**;LIVE=**v0.11.0 面**(三 key 重注入+生产树真实拉取
  终验 cpi=0.9@2026-09-30)。合并纪律已更正(2026-11-11 用户指令): 波次验收绿
  即合并发布不逐次请批,逐次报批仅剩付费类;CN_PPI tushare 积分档=用户裁定
  暂不付费先跑通其他(PPI 如实缺席留后议)。**下一波=AC7 端到端首跑**
  (docs/autonomous-rd/AC7_RUN_PLAN.md,三任务+一开放题)。

## 前一快照: 2026-11-11 (HKT, R6 采集面修复轮·操作者网络轮)

- **R6(采集面修复 D1/D2)已完成**: 分支 `dev/rd-r6-collection-fixes`(自
  dev/rd-r5-stage-coverage 切出,R5 未合并故链式携带)——
  **D1 CPI/PPI 换源**: G-P1-15 金十通道(2025-08 停更后持续写旧值)→
  tushare pro `cn_cpi.nt_yoy`/`cn_ppi.ppi_yoy`;新纯函数
  `_tushare_monthly_last`('YYYYMM'最大有值月→月末观测日,NaN/坏月跳行);
  registry **v2.8.0→v2.8.1**(两 source_symbol 同步+notes 前插)。真实拉取
  冒烟(LIVE token 只读): **cpi_yoy=0.9@2026-09-30 新鲜**;ppi_yoy=服务端
  拒「没有接口(cn_ppi)访问权限」=token 权限档不足(与 cn_cpi 同族不同档;
  金十族复测全死/akshare 1.18.47 无 EM-PPI 包装[源码 grep]/东财 datacenter
  reportName 试探 0 行)→ **卡点②候选报批项**,批前如实缺席。
  **D2 CN_OMO_7D=源端全阻登记**: 四路免费候选实测全灭(tushare 无 OMO 接口/
  央行官网 502/akshare 零逆回购端点+无 telegraph/东财 cookie 门)→
  source-blocked 不造数(台账三之四,后续路径=chinamoney/EM reportName 深挖
  P3 观察)。
- **测试**: wp_e 26 OK(T4 换 tushare 桩+新 t56 纯函数判定;版本锁随升)/
  data_batch1 38/0/charter6_p2 88/0(两处锁随升)/R1 52/R2 47/R5 38/
  snapshot 46 **全绿零回归**。
- **基线**: main = `be8dabd`(v0.10.0-alpha);CI 绿=128 槽。R5+R6 波次
  **待用户批准合并 main**(卡点①逐次请批)。
- **无头自主运行(卡点④)**: 常态运转(每 4h);R6=操作者网络轮(无头禁外发,
  D1/D2 需真网故由操作者会话执行)。

## 前一快照: 2026-11-11 (HKT, R5 阶段证据覆盖面轮·无头自主执行)

- **R5(阶段证据覆盖面)已完成**: 分支 `dev/rd-r5-stage-coverage`——R1 发现
  「阶段B 16 指标快照缺席」全量分解为四类缺陷并收口(`audit/R5_STAGE_COVERAGE_INVENTORY.md`):
  ①假设引用超出观点 subjects 映射面+③mode A 事实面截断过杀=引擎覆盖面缺口**已修**
  (`view_verifier.metric_evidence_table/verify/verify_at_publish` 增
  `extra_metric_ids` 并面;approx_filtered 支截断序列尾值近似,
  `level_source=series_tail_le_publish`+DEGRADED 披露;`build_vp` 汇总假设
  metric_refs 传入 A/B 两型);②CPI_YOY 语义层 id 错配(注册表实有 CPI/CORE_CPI)
  =missing 注记精确化,重指留 Agent 层禁猜;④CN_OMO_7D/BUND_10Y 真缺席=台账
  (`../P2_DATA_GAP_LEDGER.md` 三之四)。**17 份 VP 重建对照**: 既有行零丢失/
  零变动、C 层零变动、新增 64 行(A51/B13)、7 假设 INSUFFICIENT→有判
  (3 SUPPORTED/4 CONTRADICTED,方向全为获得判断)。新套件
  `tests/test_rd_r5_stage_coverage.py` 38 判定绿;R1 52/52、c9_modes 57/57、
  charter8 41/41、vp_sidecar 40/40 无回归;全套回归 129 文件批跑: 其余 128 全 PASS,
R5 套件初跑 3 判定 FAIL=**套件自身判定缺陷**(写死「在档=前R5版」假设,批跑中他套件
真重建 VP 后破裂;引擎零改动),改为逐字节前后不变式后 38/38 绿(全仓口径 130 含根
test_env.py 环境探测)。
  **新发现 P0**: CN_CPI_YOY/CN_PPI_YOY 陈旧值(2025-08 停更源)仍被证据引擎
  采信(R5-D1)+CN_OMO_7D 字段从未采集(R5-D2)——登记 OPEN_ISSUES/台账,
  待有网络环境轮修。
- **基线**: main = `be8dabd`(v0.10.0-alpha);CI 绿=tests/ 128 槽(全仓口径 129
  =+根 test_env.py);本轮后 tests/ 增 1 槽(R5 套件)→ 预期 129/130。
  R5 波次**待用户批准合并 main**(保留卡点①逐次请批)。
- **无头自主运行(卡点④)**: 已由用户放行落地(launchd 拉起本无头轮,提示词
  常驻);本轮=R5 首个无头自主轮。`~/agent-loop/` 在无头会话权限面外
  (rounds/index 追加受限,如实记录)。

## 前一快照: 2026-11-11 (HKT, 用户「全部审批通过」四卡点执行后)

- **基线**: main = `be8dabd`(v0.10.0-alpha,长期自主研发第一波 R1-R4+审计闭环);
  Release 441746111 上线,CI 43030767965 绿 = main 基线 **128 槽**(CI 口径=tests/;
  全仓口径 129 含根 test_env.py 环境探测)。merge --no-ff dev/rd-r2-research-orchestrator,
  分支链 53aa4fe→946625b→ac40ef8→cb98106→fc18590→1721ecc→b9d5cf6→be8dabd。
- **LIVE(本地 Mac launchd)**: **已部署 v0.10.0 面**(2026-11-11 卡点③执行毕)。
  git archive be8dabd 覆盖提取+三 key 重注入 env_config 默认位+.env/data/logs/output/
  archive 全保护;冒烟绿(changes/research-map 10问/research-run 14 步 0 败/
  report_generator+app 导入/launchd 两任务在场)。已知: weekly exit2=既有 Gate A
  数据缺口(ZQ_IMPLIED_AVG 采集缺席,10-31 与 11-07 同因)非部署回归——采集面排查
  已列 RESUME R5 候选③。明晨 07:00 daily=新面首跑。key 备份=~/.ia-live-deploy-backup/。
- **引擎**: 停于唯一日历门——F 补证轮观察钟 2026-12-05 满自动触发,此前无排程任务。
- **长期研发章程**: 2026-11-11 用户《总指令》原文已落位 `PRODUCT_GOAL.md`;
  《长期自主研发系统启动指令》原文已落位 `RUN_MANDATE.md`(自主循环/环境自检/AC11–AC12)。
  FINAL_ACCEPTANCE.md: AC3 = **PARTIAL**(R1+审计收口),AC6 = **PARTIAL**(R2 编排器真执行),
  其余 NOT_VERIFIED。
- **R2(一键研究真执行)已完成**: 分支 `dev/rd-r2-research-orchestrator` @`ac40ef8`+
  R1.1 并入(merge `946625b`)——`scripts/research_orchestrator.py` 十一步确定性管线
  (S1 分解→S11 归档):每步真 `ia_cli` 子进程执行+信封留档,process-ok 与 semantic-ok
  分记,L3 AI 推断/L4 条件情景恒 declared-not-produced(诚实面),逐数证据索引
  (L1 每行挂 snapshot fact_id/L2 挂 VP-id),实体映射零命中=如实 unmapped 不猜,
  归档默认关。入口 `ia_cli.py research-run --question …`。自测 31 判定绿;R1 无回归;
  **全套回归 129/129 exit 0**(全仓口径=tests/128+根 test_env.py 环境探测脚本)。
  **R2 独立审计已收口**(七维对抗: 真执行面/诚实面/证据索引/实体映射/红线/测试真实性/
  Skill 对照——无 BLOCKER,2 MAJOR+4 MINOR+5 NIT;证据索引实测对上快照、红线全过、
  31 判独立;报告 `/tmp/r2_audit_report.md`)。**R2.1 已修**(MAJOR-1 S7 gate 改取
  compare 对齐门 `data.alignment.research_mode_gate`+记 gate_source,修死代码;
  MAJOR-2 L4 五行回归纪律16 权威模板+L3 补 E1/E2/E3 指路+research_map RQ9 统一;
  MINOR-1 analog 诚实拒答豁免 run_ok;MINOR-2 compare 截断披露;MINOR-3 台账语义列)。
  套件 38 判定绿(+7 回归);R1 50/50、research_map 32/32 无回归。剩余 MINOR-4+5 NIT
  转 OPEN_ISSUES。
- **R3(十问扇出入口)已完成**: 同分支 @本提交——`research-run --fanout` 把
  research_map.QUESTION_COMMANDS 十问命令清单确定性执行(16 条命令 ia_cli/scripts
  双通道真子进程+信封留档);Agent 层问(RQ3/RQ9)declared-not-produced;占位符确定性
  替身且如实披露(VIEW-…→观点库首条,A_ID,B_ID→命中指标前二,替身≠相关性选择);
  report.md 增十问扇出台账;run_step 泛化为 _run_proc(支持 scripts/ 直跑)。套件
  47 判定绿(+9);全套回归 129/129 exit 0。AC6 剩余差距收窄=AC7 端到端 3 任务+1
  开放题+真实案例积累。
- **R1(三型证据落库)已完成+审计收口**: 分支 `dev/rd-r1-stage-evidence` @ `26d4ef7`——
  VP sidecar v1.1(阶段A/B 结构化+stage_labels,mode C 契约零变动)、research-map 命令清单
  可执行化(14 条实解析)、页③三阶段证据披露;本地 17 份 VP 重建(A面 12 INSUFFICIENT/
  4 PARTIALLY_SUPPORTED/1 MIXED;B面 12 INSUFFICIENT/5 MIXED)。**全套回归已绿**(2026-11-11
  在 R1 分支干净重跑: 129/129 文件全部 exit 0,零 FAIL;此前章程分支上的作废运行系测试文件
  被分支切换污染)。**独立审计已收口**(2026-11-11,对抗式 6 维: 无前视/标签纪律/方向归因/
  契约真实性/可复算性/B面抽验——六维全 PASS,交付物 17/17 清洁、逐字节重建一致、31 数值
  独立复算全中;结论=无 BLOCKER,2 MAJOR 潜伏缺陷+6 MINOR+3 NIT,报告 `/tmp/r1_audit_report.md`)。
  **R1.1 已修**(MAJOR-1 `interval_change` 入口日期归一 `_norm_ymd`(无横线端锚字符串比较
  使封顶整年失效)→ 根治含阶段B端锚与回落序列;MAJOR-2 `_hypothesis_directions` 废双基
  容忍、定 1-based 单基+provenance 记 `forecast_index_basis`;MINOR-3 词表否定护栏
  ('不再加息'/'no further cuts'/'supply-driven'→None)+英文词边界正则)。回归: 套件增至
  50 判定全绿+受影响 8 文件全 exit 0;**对照实验**(HEAD 代码 vs 修复代码、同一份真数据、
  独立进程、同种子重建 17 份)= 语义零差异 0/17,证明修复不改今日产出。剩余 MINOR 转
  `OPEN_ISSUES.md` 技术待办。章程分支已并入 R1 分支(merge 87afebe,统一历史线)。
- **自主机制**(2026-11-11 配置): 项目级 `.claude/settings.json`(gitignore,仅本地)挂
  PreCompact+SessionStart hooks——PreCompact 提醒完成检查点,SessionStart 提示恢复入口
  (CLAUDE.md→RESUME.md)。stderr 级提醒,无写操作;对在未来于本仓启动的会话生效。

## 里程碑脉络(详录 = `ITERATION_LOG.md`)

38/38 工作包全收口(11-08 四层封版)→ MW-V1 章程校准 → OSS 产品化 v0.1 → Skill 化 v0.2 →
v1.1 整改 v0.3 → Model-Agnostic v2.0(v0.4)→ v2.1 整改+glm 清零(v0.5)→ Charter 6 十年深度(v0.6)→
Charter 7 能力建设(v0.7/v0.7.1)→ Charter 8 机构观点交叉验证(v0.8)→ Charter 9 研究闭环+一键研究(v0.9)。

## 当前差距要点(详表 = `CAPABILITY_MATRIX.md`)

- 机构观点库六标签全库 INSUFFICIENT(库龄函数,首验窗 2026-12)。
- LIVE 面落后 dev 面(v0.7.1 vs v0.9.0)。
- 数据缺口台账 18 项(`../P2_DATA_GAP_LEDGER.md`);HY_OAS 族 = 源端 3 年授权窗如实注记。
- 历史遗留(`../REMAINING_ISSUES.md`,2026-10-17 版): P0 空,余 P1 观察项。

## 用户保留卡点(状态: 2026-11-11「全部审批通过」)

- ① 封版合并 main — **已批准已执行**(本波 R1-R4=be8dabd+v0.10.0-alpha+Release 441746111)。
  后续波次合并 main 仍逐次请批(红线不变)。
  *(2026-11-11 同日更正: 验收绿即合并发布,不再逐次请批;逐次报批仅剩付费类。)*
- ② 新数据源凭证/付费 — **原则获批**,暂无即需项;HY_OAS ICE BofA 3 年授权窗等
  实际采购仍按需逐次报批。
- ③ LIVE 部署 — **已批准已执行**(v0.10.0 面,见快照)。
- ④ 无头自主运行 — **已批准,落地被权限分类器拦**(启动器提示词文件写入=
  [Create Unsafe Agents] 类别);待用户在场放行后建
  (方案: launchd 每 4h `claude -p` 单轮+STOP 文件+--max-budget-usd 界+允许清单
  禁 push/ssh/curl/npm/pip、合并 main 与付费仍留用户)。
