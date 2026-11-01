# IA-P0-2-W5-FIX1 交付说明(七项确定性缺陷增量修复)

- 指令: IA-P0-2-W5-FIX1-DEV-v1.0 | 契约: IA-P0-2-W5-FIX1-AC-v1.0
- 失败基线: 78f4c9a83962fd7b6bdaa0328a917122a0cfd2e6(W5首轮,Agent4判FAILED)
- 分支: dev/p0-2-w5 | 开发: Agent 3 | 验收: Agent 4(独立)
- FIX1实现Commit: f1b6e42 | 最终固定Commit: (见§8回填)
- 范围纪律: **从78f4c9a增量修复七项确定性缺陷及必要验收证据,不重建W5**;
  W5已通过能力(八项外部对照/独立复算/三态综合/证据保全/32用例)全部保留。

## 1. 七项缺陷 → 修复对照

### FIX1-01 FRED密钥失败路径脱敏
- `_register_secret(s)`: 登记明文+`quote(s)`+`quote_plus(s)`三种形式;
  main()加载FRED密钥后立即登记,运行时已知明文全部进入脱敏路径。
- `sanitize_text`: `api_key=`参数模式(不重复处理已脱敏标记,幂等)+
  已知密钥任意形式出现→`***REDACTED***`。
- `_clip_safe(s, n)`: 截断后若尾部与任一已知密钥前缀重叠(≥2字符)则
  回退截断点——截断不得制造密钥部分暴露。
- `_safe_error(err)`: `"{异常类型}(HTTP {状态}): {消息}"`,保留错误类型与
  HTTP状态(401/403仍可确认),消息经全量脱敏+截断,复核残留→整体脱敏占位。
- 写前最终检查: JSON(`sweep_secrets`)/MD/LOG逐行/ZIP(raw正文写盘前
  `find_secret`)。
- 测试一律使用虚构密钥(FAKEKEY…/BOUNDARYKEY…等),无真实密钥入日志。

### FIX1-02 复算价格字段校验
- 期末: `fact.value` vs 独立序列`close`(相对容差`RECOMPUTE_PRICE_TOL_PCT`
  =0.01%,覆盖金融两位小数舍入)+ 结束观测日期核对;引擎提供`derived.end`
  才核对end(既有数据契约: china通道不填end,不强加)。
- 逐期: 独立有基准时引擎**必须**提供`basis_date`与`basis_value`——缺失、
  日期不一致、基准价格不一致均进`period_failures`→FAIL;**百分比相同也不得
  跳过价格字段核对**;收益率百分点容差不放宽(仍`RECOMPUTE_TOL_PP`)。
- 固定反例(基准100/期末110/独立10%): 期末价111/基准值999/缺基准日期/
  缺基准值/仅pct对→全部FAIL(B1组逐一断言)。

### FIX1-03 完整复算门槛
- `recompute_check`新增`complete_recompute`/`verified_periods`/
  `insufficient_periods`;WEEK/MTD/YTD三期全部有效一致才算完整PASS,
  部分成功=INSUFFICIENT_HISTORY+note明示"部分复核…不冒充完整PASS"。
- `evaluate_overall`整体PASS三条件: ①原外部同口径门槛②原复算数量门槛
  不降低③`recompute_complete≥1`(至少一条真实资产序列三期完整独立复算),
  覆盖统计新增`recompute_complete`字段。

### FIX1-04 SHCOMP历史盘中价阻断
- `check_shcomp`: 任意报价日期一律要求收盘口径——`time`缺失或
  `<15:30:00`→NOT_VERIFIED(历史日期豁免取消);`≥15:30:00`+价格吻合→
  PASS;日期不匹配NOT_VERIFIED;真实收盘超差FAIL。历史报价比较能力保留
  (C4组: 历史15:30与当日15:31均PASS)。

### FIX1-05 输出路径安全
- `path_conflict(data_dir, out_dir)`: `os.path.realpath`+`os.path.commonpath`,
  拒绝完全相同/输出在输入内部/输出为输入祖先/`..`真实路径重叠/符号链接
  真实路径重叠;字符串前缀相同但真实路径无关不误拒。
- main(): 参数解析后、任何写入/快照构建/外部API调用**之前**检查,非法→
  明确拒绝信息+exit 2+零写入+零网络+输入逐字节不变(A7组实测)。

### FIX1-06 八项检查来源绑定
- 稳定`CHECK_IDS`: EXT-UST-2Y/10Y/30Y/EXT-BTC/EXT-GOLD-F/EXT-SHCOMP/
  EXT-SPX/EXT-WTI-F——不重复不缺失(D1组精确集合断言)。
- 行级`external_source`/`source_identity`/`evidence_ids`+`external`镜像;
  `_ours`保留`fact.source`(D2组);三UST共享年度CSV证据、FRED各自
  (EV-FRED-SP500≠EV-FRED-DCOILWTICO)、Coinbase BTC/PAXG各自
  (D3组);所有`evidence_ids`可在`external_evidence`定位,零悬空。
- 无FRED密钥: 来源明确为空(`external_source=None`/`evidence_ids=[]`),
  不构造任何虚假ID(D6组)。

### FIX1-07 Treasury跨年度
- 三期限各自观测日按年分组→每年请求官方年度CSV→`rows.update`合并索引
  →逐年证据保留(EV-TSY-{year})→各期限单独匹配。
- 固定场景(UST_2Y=2025-12-31,UST_10Y/30Y=2026-01-02): 必须发起2025与
  2026两年度请求,各自同日匹配全PASS(D4组);某年失败仅影响该年日期
  (D5组: 2025失败→UST_2Y NOT_VERIFIED,10Y/30Y不受影响)。

### FIX1-08 专项测试 `tests/test_p02_w5_fix1.py`(32用例,全绿)
- A组安全(8): 401/403/超时/杂类失败脱敏+诊断保留、运行时明文+URL编码
  形式、截断边界、递归清扫幂等、path_conflict五类拒绝+前缀不误拒、
  main级内部/相同/祖先/符号链接拒绝(零写入零网络+输入SHA不变对照)。
- B组金融(5): 固定反例5项全FAIL+观测日期错位FAIL;真实引擎快照扩展序列
  三期完整PASS(mtd基准2026-09-30/ytd基准2025-12-31);部分复核
  INSUFFICIENT_HISTORY不冒充;evaluate_overall四场景(双部分→含三期完整
  理由、单完整、多完整→PASS、任一周期错→FAIL)。
- C组价格语义(6): 历史10:30/00:00/同日无时间→NOT_VERIFIED;收盘口径
  吻合(历史15:30/当日15:31)→PASS;日期错位NOT_VERIFIED;超差FAIL。
- D组来源(6): 八check_id精确集合唯一齐备;ours.source保全;evidence_ids
  零悬空+UST共享两年度+SPX≠WTI+PAXG;跨年两年各调各匹配;单年失败隔离;
  无密钥空绑定不造ID。
- E组退化敏感性(7): 对真实源码做七类最小退化替换后importlib加载
  (E5退化main的ROOT_DIR指向真实仓库根仅为解析metric_registry输入指纹,
  不改变被退化逻辑本身),断言退化版与正确版行为分离——恢复任一FIX1缺陷
  必使对应断言失败(证明测试非实现复制品)。

## 2. 旧测试必要修订(理由,§二报备)
1. `test_p01_fix8.py` I3 与 `test_p02_w5.py` E组: out-dir从数据目录内
   迁移至独立temp目录——FIX1-05生效后"输出位于输入内部"属明令拒绝模式,
   旧用法在main入口即exit 2。安全断言(拒绝信息/Gate A信任边界/exit码)
   与测试语义全部保留,只迁移输出位置。
2. `test_p02_w5.py` A6: 历史日期00:00:00报价预期由PASS翻转为
   NOT_VERIFIED——FIX1-04取消历史豁免后该行为即缺陷本体,旧预期是
   对缺陷的固化;A6同时新增历史15:31→PASS保留对照。
3. `test_p02_w5.py` B4/B5/E1/E3: 复算断言从"≥2 PASS"改为部分复核语义
   (INSUFFICIENT_HISTORY/complete_recompute=False/week已核),E3扩展
   global历史序列至2025-12-31+2026-09-30后断言recompute_complete≥2。
   历史安全用例零删除,均只随契约语义更新。

## 3. 全量历史回归(本地)
52套件 exit=0(`tests/test_*.py`全量;`test_glm_live`按契约排除):
其中`test_p02_w5.py` 32/32、`test_p01_fix8.py` 52/52、
`test_p02_w5_fix1.py` 32/32。

## 4. 正式真实数据验收执行计划(§十二)
最终固定SHA后实际执行(不留未来计划):
- 输入: `/Users/cast/audit/w4-real-data/daily`(848文件冻结副本,完整性
  重确认);输出: 独立目录(与输入无路径冲突,FIX1-05先决检查)。
- 数据授权: 非LIVE生产数据,冻结副本+只读;LIVE/launchd/生产数据零改动。
- 外部: Treasury.gov/Coinbase/sina/FRED(密钥经env注入不打印)真实调用;
  不可达如实NOT_VERIFIED;Gate A失败不绕过;重大差异不放宽阈值按原契约FAIL。
- 产物: 9件正式输出(JSON/MD/LOG/外部raw/SHA256SUMS等)入证据包。

## 5. CI实证(回填区)
(最终固定Commit推送后workflow_dispatch offline-tests.yml,回填Run/Job ID/
checkout SHA/52套件逐套件退出码。)

## 6. 隔离取证(§十三,回填区)
(最终DEV/LIVE只读取证: HEAD SHA/远程同步/main与W4封版未动/DEV≠LIVE。)

## 7. 证据包(§十四,回填区)
IA-P0-2-W5-FIX1-ACCEPTANCE-EVIDENCE.zip(实际交付路径+SHA256)。

## 8. 版本
- FIX1实现Commit: f1b6e42(本文件之前)
- 最终固定Commit: (回填)
- 增量Diff: 78f4c9a→(回填最终SHA)
