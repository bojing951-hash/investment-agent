# IA-P0-2-W4-FIX1 交付说明(四项确定性缺陷定向修复)

任务: IA-P0-2-W4-FIX1-DEV-v1.0 | 冻结契约: IA-P0-2-W4-FIX1-AC-v1.0
性质: W4首轮独立验收失败后的定向修复(增量修复,不重建审计器)
基线: W4首轮失败验收Commit `62c1661efb0efd29b57cc805b72972de9818cd3c`(W4最终CI
run 41186509449);W4实现Commit `62ed379f9b58a3b9cfbbc288f81f6c40f44b9fee`;
W3封版 `497b02c7b770d4eadb9086d453fea14d275bd4c9`;GitHub main仍=P0-1封印
`50b5d13db6c477084c6f4b3944b7bd08a8e329d6`。

---

## 1. W4失败基线(Agent 4首轮验收结论的四项确定性缺陷)

1. **连续区间用自然日阈值**(`segment_split`日/周/月10/21/92天)——月频跨缺失
   月份仍判连续(06-15→09-15缺7/8月判连续);同月两个日期当两个独立月度样本。
2. **`cross_file_duplicate_records = max(auth_raw - 唯一日, 0)`**把全部重复
   算成跨文件重复——文件内重复被冒充跨文件重复。
3. **`rzye_billion`(融资余额,亿元)被当`MARGIN_BAL`(注册语义=两融余额合计)
   权威历史观测写入**——口径不一致的数值获得了权威覆盖身份。
4. **`discover_files()`只查`global_*.json`+`macro_*.json`决定是否进入daily/**
   ——china-only等合法输入的daily/目录不被识别(NO_INPUT误报)。
   附: 机器报告缺`audit_commit`/`generated_at`审计执行元数据。

## 2. FIX1实现(全部修改限于scripts/historical_coverage_audit.py)

增量Diff(`62c1661→FIX1最终SHA`): scripts/historical_coverage_audit.py
(1033→1238行,纯增量修复+元数据,不重建);tests/test_p02_w4.py(错误预期修订,
见§12);新增tests/test_p02_w4_fix1.py(40检查);docs/P0_2_W4_FIX1_DELIVERY.md
(本文件)。**未触碰**: fact_engine/snapshot_builder/trading_calendar/采集器/
metric_registry.json/W1~W3/Gate/生产数据/长期状态。

### FIX1-01 连续覆盖按真实观测槽位
- 新`split_slots(auth_dates, freq, calendar)`: 复用`expected_slots()`
  (daily=tc交易日历预期日/weekly=ISO周/monthly=自然月);权威观测日→槽位键→
  去重→按预期序列索引排序;**相邻实际槽位在预期序列中索引相邻才属同一连续段,
  中间任何缺失预期槽位必须断段**。段结构`{start_slot,end_slot,slots,start,end}`
  (start/end=段内实际观测日首末,兼容既有Schema)。
- 不属于已知预期日历的额外观测单独披露(`extra_slot_keys_sample`),不入段。
- 预期槽位无法确定→不虚构连续覆盖(segments=[],`slots_unavailable_reason`
  披露;findings3回退自然日判据并标注`slots_unavailable_natural_day_fallback`)。
- **两个计数并存不混淆**: `unique_observation_dates`(原始日期数,数据描述)
  与`unique_observation_slots`(独立槽位数);weekly/monthly的连续段/最长连续段
  (`longest_continuous_segment_slots`)/`usable_intervals`(≥2槽位)/
  SINGLE_OBSERVATION分类全部按槽位;`classify()`签名增`n_slots`位。
- `max_internal_gap_days`保留为描述性自然日统计(不再判定连续性);
  `segment_split`(自然日算法)保留为描述性参考函数,不再决定覆盖连续性。
- summarize findings3(严重断点)与连续段同一口径: 连续段≥2段=存在缺失
  槽位断段(旧实现按自然日间隔>阈值,与连续段口径不一致)。

### FIX1-02 重复计数按真实文件身份拆分
- 新纯函数`split_duplicates(auth_records)`(以权威观测为范围): 按
  `(file, obs_date)`计数——`same_file_extra_duplicate_records`=同一文件同一
  观测日每多一条权威记录计一次;`cross_file_duplicate_records`=同一观测日出现
  在多个不同文件按不同文件额外出现次数计。
- 指令§五固定例: 文件A同日3条+文件B同日1条→权威4/唯一日1/同文件2/跨文件1
  (tests/test_p02_w4_fix1.py::test_b4)。
- 计数不变量(逐指标): 权威原始记录=唯一观测日+同文件额外+跨文件额外。
- 保留: 同日不同值冲突候选/跨采集日修订/非权威不增覆盖/原始有效记录数/
  严格日期与值校验/采集日期不代替观测日期/原始重复记录不删除。

### FIX1-03 MARGIN_BAL身份修复
- 只有同口径`balance`(两融余额合计,注册语义)是MARGIN_BAL权威观测;
  `rzye_billion`(融资余额,亿元)/`rzye`(融资余额,元)/`rqye`(融券余额,元)
  均与注册口径不一致→**不写入MARGIN_BAL权威历史**(不用于earliest/latest/
  coverage/continuous_segments),逐键经unmapped独立披露`identity_mismatch`
  并标明字段语义(融资余额/融券余额);margin块其他未注册字段同样披露。
- 同日并存balance与rzye_billion: balance入权威,rzye_billion仍独立披露。
- 未越界: 未修改metric_registry.json/未改指标名/未自动把融资余额解释成两融
  总余额/未以其他数据代替/未伪造融券余额;两融合计重建须另行确认来源/单位/
  公式(明确注记"不自动以rzye+rqye推算")。

### FIX1-04 五通道任意子集发现
- daily/进入条件=CHANNEL_PATTERNS五通道(global/china/macro/rate_economy/
  research_snapshot)任一模式命中;china-only的daily/正确识别(指令§七固定
  反例: data/daily/china_20261020.json唯一→COMPLETED,81项全输出)。
- 输入根与daily/同时有合法输入: 固定选daily/(生产采集布局,规则经
  `excluded.selection_rule`公开可复核),未选根层通道文件数经
  `excluded.unselected_root_files`披露(只数不读,不暗中混合);
  daily/存在但五通道无命中→`daily_present_without_channel_files`披露。
- 不以其他路径旧数据补齐缺失通道;symlink继续拒绝并披露;
  by_channel只计实际入清单文件;不修改输入文件。

### FIX1-05 审计报告元数据
- `audit_commit`: `git rev-parse HEAD`真实取得(40位hex;工作区脏项数经
  `audit_commit_worktree_dirty_files`披露,脏时附`audit_commit_disclosure`
  "不得声称报告完全对应干净已提交版本";git不可得→如实注明不声称对应任何
  已提交版本)。INVALID_PATH/NO_INPUT结果同样先取得元数据。
- `generated_at`: 真实UTC系统时钟(`datetime.now(timezone.utc)`),MD头部
  与JSON/日志均披露。
- `run_id`仍由输入Manifest摘要决定(同输入同ID);确定性语义: 相同输入数据+
  相同代码版本⇒相同覆盖统计(不要求执行时间相同);SCHEMA_VERSION升至
  `w4-coverage-audit/1.1`。MD头部新增披露: audit_commit/generated_at/
  审计结果状态/实际输入数据根目录(realpath)/输入清单摘要(manifest_digest)。
- 逐项表新增"独立槽位"列(日期计数与槽位计数并列可见)。

## 3. 增量与累积Diff
- 增量Diff: `62c1661..FIX1最终SHA`——scripts/historical_coverage_audit.py
  (+273/-49行级修改)、tests/test_p02_w4.py(预期修订)、tests/test_p02_w4_fix1.py
  (新增)、docs/P0_2_W4_FIX1_DELIVERY.md(新增)。
- W4累积Diff: `497b02c..FIX1最终SHA`(W3封版以来全部W4+FIX1新增)。
- 实际SHA/行数以Git与CI为准(见§13)。

## 4. 槽位连续性规则(公开定义)
连续段=相邻实际观测槽位在expected_slots预期序列中索引相邻;任何缺失预期
槽位断段;日历外观测单独披露不入段;预期槽位无法确定时不虚构连续覆盖。
交易日历由trading_calendar全系统权威提供;日历近似限制(cn仅2026精确/hk
最小集/fx周一五近似等)逐指标经`calendar_limitations`披露,阈值定义维持
工程描述约定(非金融事实)。

## 5. 日期计数与槽位计数区别
`unique_observation_dates`=不同观测日数量(原始数据形态描述,同月两日期=2);
`unique_observation_slots`=不同预期槽位数量(weekly/monthly按ISO周/自然月,
同月两日期=1)。覆盖率(observed/expected)、连续段、最长连续段、可用区间、
SINGLE_OBSERVATION分类按槽位;观测日期数量继续作为原始数据描述输出。

## 6. 文件内与跨文件重复定义
见§2 FIX1-02;两计数+不变量+6场景见tests/test_p02_w4_fix1.py B组
(同文件point+series同日/同文件series内重复/不同文件同日/指令固定混合例/
同日不同值/权威与非权威重复)。

## 7. MARGIN_BAL口径修复
见§2 FIX1-03;正向(balance获权威)与负向(仅rzye_billion不得获权威)及
真实键组合(rzye/rqye/rzye_billion)见C组。

## 8. 五通道任意子集发现
见§2 FIX1-04;D组覆盖: china-only固定反例/五单通道+全部10个两通道组合/
直接传daily目录/空目录/无目标文件(根层排除项与daily内排除项两形态)/
symlink拒绝披露/根与daily并存选择规则。

## 9. audit_commit与generated_at
见§2 FIX1-05;E组覆盖: 真实git HEAD相等性/UTC时钟窗口/固定代码版本一致/
脏工作区披露与git不可得披露/同数据覆盖确定性(剔除generated_at比较+manifest
字节级一致)/输入SHA-256不变/MD头部披露。

## 10. 新专项测试(tests/test_p02_w4_fix1.py,40检查)
A组9(槽位连续: NFP缺月断段/WTI月内3日期2槽/单月两日期1槽/周五→周一连续/
缺预期交易日断段/周频缺周断段/日历外槽位披露/两计数并存/槽位不可确定不虚构)
+B组6(重复拆分6场景+全指标不变量+纯函数复算)
+C组5(仅rzye无权威/balance权威/同日并存/真实键组合披露/无权威连续区间)
+D组7(china-only反例/15种子集/直接传daily/空目录/两形态无目标文件/
symlink/根与daily并存)+E组8(audit_commit/generated_at/版本一致/脏披露/
INVALID_PATH元数据/确定性/SHA不变/MD头部)
+F组5(负向敏感性: 自然日退化/旧公式退化/rzye当权威退化/global+macro-only
发现退化/无元数据退化——五类退化均被检出)。
全部经真实`run_audit()`/`main()`/模块函数执行,不复制实现自证。

## 11. 旧测试修订(tests/test_p02_w4.py,场景全保留,预期修正+理由)
1. **test_a09**: SHCOMP连续段2→3。原预期把10-16(周五)→10-20(周二)判连续
   (自然日间隔4<10),违反FIX1-01——中间缺预期交易日2026-10-19必须断段。
   保留BTC断言,增段边界与缺槽断言。
2. **test_a18**: MARGIN_BAL first=2026-10-20+field_semantics注记→MISSING+
   unmapped identity_mismatch披露。原预期即FIX1-03所指缺陷(rzye_billion当
   权威观测);fixture不变(仍只有rzye_billion),预期改为身份正确行为。
3. **test_c22**: JSON/MD字节级一致→manifest字节级一致+JSON/MD剔除
   generated_at后一致。FIX1-05新增真实执行时间后,完整字节一致仅在同秒执行
   时偶然成立(时序运气);确定性语义(同输入+同代码⇒同覆盖统计)不变,另增
   audit_commit两次执行必须一致的断言。
4. **test_e5**: classify负向mock签名同步新签名(增n_slots位),注入语义不变。
   其余32检查未改动。

## 12. 全量历史回归(本地,推送前)
tests/下48个test_*.py: 47套执行全部exit=0(test_glm_live按workflow契约
排除);含test_p02_w4.py(修订后36检查OK)、test_p02_w4_fix1.py(40检查OK)、
W4原36检查、W3及FIX1~5、W2及FIX1~6、W1/W1-FIX1、P0-1 FIX1~11、原始14项E2E、
Gate A/B、来源内容摘要、正式报告及长期状态保护、月报季报等全部通过
(逐套件退出码见§13 CI实证,CI清单与本地一致)。

## 13. GitHub最终CI(workflow_dispatch,dev/p0-2-w4)
实现Commit/最终固定Commit/Actions Run/Job ID/checkout head_sha/逐套件退出码:
见本文末"CI实证"节(最终固定Commit后回填;两轮CI均46+1套件,新增
test_p02_w4_fix1.py)。**W4首轮的46套绿色CI不作为FIX1验收结果**。

## 14. 正式真实数据审计(FIX1-07,最终Commit后执行)
- 数据: 优先复用W4已授权冻结副本/Users/cast/audit/w4-real-data(848文件);
  复用前重新核验: 目录存在/授权范围/文件计数与SHA-256与LIVE原件对应/来源
  清单——**不因旧文档提到该路径即自动假定仍完整可信**;核验记录入Git外附件。
- 用最终固定SHA代码重跑(工作区必须干净→audit_commit=最终SHA,无脏披露);
  产出最终输入Manifest/81项JSON/MD/执行日志/代码SHA/实际执行时间/输入前后
  摘要/来源授权说明/未验证事项(输出至独立目录,不覆盖W4旧产物)。
- **W4旧分布(72 OBSERVED/2 SPARSE/1 MISSING/6 DERIVED_ONLY)不得沿用**:
  FIX1-03使MARGIN_BAL失去全部权威观测(真实848文件中188个china文件的margin
  均只有rzye/rqye/rzye_billion,无balance);FIX1-01使连续段/最长段/可用区间/
  断点结论按槽位重算;新分布按新报告如实交付(数字以最终审计JSON为准,
  记入Git外附件IA-P0-2-W4-FIX1-REAL-AUDIT-*.txt与对话报告,不入Git)。

## 15. 最终DEV/LIVE只读隔离证据
最终Commit后按§十四⑩执行,产出
/Users/cast/audit/IA-P0-2-W4-FIX1-POSTCOMMIT-ISOLATION-<SHA7>.txt(Git外):
核验时间/DEV HEAD与分支/远程三分支/GitHub main/DEV与LIVE realpath+inode/
launchd两服务路径/LIVE核心源码SHA-256 vs P0-1封印/W4+FIX1产物未部署LIVE/
生产数据与长期状态只读元数据/真实审计冻结副本与授权来源关系/未能独立证明的
历史瞬时事项。此前W4隔离证据(62c1661版)对该Commit不再适用。

## 16. 未验证事项
- 真实生产数据的金融数值真实性/W5研究充分性(超出W4/FIX1范围,全部指标
  research_sufficiency=UNDETERMINED)。
- LIVE生产目录在冻结副本之后的新增文件不在本次授权数据集内(审计只针对
  848文件冻结副本;冻结时点后的生产变化不构成本轮结论的一部分)。
- 日历近似(cn仅2026精确/hk最小集/fx周一五/FRED按NYSE近似)导致的单日级
  断点判定近似性——逐指标经calendar_limitations披露,非金融事实。
- MARGIN_BAL两融合计的重建(须另行确认来源/单位/公式,本轮不开发)。
- 历史瞬时事实(如"审计期间某进程未写入")只能以单次快照+SHA复检证明,
  无法事后独立复现。

## 17. 最终状态
三选一结论见对话交付报告(材料齐全→READY FOR W4 INDEPENDENT ACCEPTANCE;
确定性阻断→FAILED;缺真实审计或隔离材料→NOT VERIFIED)。不合并main
(main=50b5d13 P0-1封印)、不部署Mac LIVE、不实施W5/P0-3。

---

## CI实证(最终固定Commit后回填)

(待回填: 实现Commit+CI run#1/最终Commit+CI run#2的Run/Job ID/head_sha/逐套件退出码)
