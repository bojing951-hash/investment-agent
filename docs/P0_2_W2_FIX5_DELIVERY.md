# IA-P0-2-W2-FIX5 交付报告(W2独立验收失败后的定向整改)

- 指令: IA-P0-2-W2-FIX5-DEV-v1.0
- 缺陷: IA-P02-W2-FIX4-DEF-001(observation_freshness误用综合结论)与
  IA-P02-W2-FIX4-DEF-002(as_of真值判断吞掉显式非法值)
- 分支: `dev/p0-2-w2`(未合并main,未force push)
- 结论自检: 实现完成+全量回归38套件0失败+CI全绿;**READY FOR W2 INDEPENDENT
  ACCEPTANCE**(不自行宣布W2 PASS,不关闭P0-2,最终验收由Agent 4独立完成)

---

## 1. 基线(FIX4最终提交,开发前只读预检)

- FIX4最终提交: `cc5143aa526e0296aa92c4ba65ca0f35240c1036`(CI run 40921349015,success)
- FIX5开工预检(2026-10-30,只读): DEV root=`/Users/cast/investment-agent-dev`
  (独立仓库,realpath一致), branch=`dev/p0-2-w2`, HEAD=`cc5143a`(=基线,无他人
  修改), 工作树clean, origin/main=`50b5d13`(未动),
  origin/dev/p0-2-w2=`cc5143a`(=本地HEAD), LIVE
  realpath=`/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent`,
  launchd plist执行目录=LIVE(venv `AI内容/venv/bin/python3`,本轮未触碰)。

## 2. FIX5提交

- 实现提交: `db586638c9d58e0ebd58c83b50d8191176f2d3ba`(5文件,+989/−89,
  CI运行#1见§17)
- 最终交付提交(本文档,docs-only): 其SHA见§17运行#2 head_sha与
  `git log -1 dev/p0-2-w2`

## 3. 增量差异(cc5143a..实现db58663)

```
scripts/allocation_engine.py | 101 +++++---
scripts/data_validator.py    |  65 +++-
scripts/freshness_policy.py  | 102 +++---
tests/test_p02_w2_fix4.py    |  30 +-
tests/test_p02_w2_fix5.py    | 780 +++++++++(新增)
5 files changed, 989 insertions(+), 89 deletions(-)
```
compare: https://github.com/bojing951-hash/investment-agent/compare/cc5143a...dev/p0-2-w2
最终提交相对实现提交仅docs增量(本文档),代码/测试零差异。

## 4. 累计W2差异(69d7fc7..实现db58663, W1封板后全整改链)

36 files changed, 9678 insertions(+), 218 deletions(-)(实测
`git diff 69d7fc7..db58663 --stat`)。
compare: https://github.com/bojing951-hash/investment-agent/compare/69d7fc7...dev/p0-2-w2
与前轮FIX4交付口径衔接: FIX4最终提交cc5143a时点35 files 8778+/218−,FIX5增量
+989/−89(§3)得36 files 9678+/218−(test_p02_w2_fix5.py为新增第36个文件)。

## 5. DEF-001修复(observation_freshness纯观测化)

- 病灶: `data_validator.anchor_time_qualification`原以
  `fp.assess()`综合verdict的`fresh/status`直接填充`observation_freshness`
  ——已知发布晚于研究截止时综合结论`fresh=False/NOT_AVAILABLE_AT_AS_OF`
  反噬观测维度,发布时序改变了纯观测新鲜判定。
- 修复: `observation_freshness`改由新增纯观测函数
  `fp.assess_observation_freshness()`供值(见§7),release_date绝不进入;
  综合拒绝语义完整迁移至新增`evidence_eligibility`(见§9)。
- 指令§5.4强制反例(实测): CPI obs `2026-09-01`/as_of `2026-10-24`/release
  `2026-10-28`/窗60 → `observation_freshness={FRESH,fresh=True,lag_days=53,
  window=60}`,`point_in_time=RELEASE_AFTER_AS_OF`,
  `evidence_eligibility={usable=False,NOT_AVAILABLE_AT_AS_OF}`,
  verify整项拒(测试A4/E2E F2)。
- 指令§5.5反向(实测): obs `2026-08-16`(滞后70>窗60)+发布`2026-09-20`已证明
  早于截止 → 观测`STALE`+点时`OK`(certified=True)+资格`usable=False[STALE]`,
  verify拒"数据过期…滞后70>60"(测试A5)。

## 6. DEF-002修复(as_of存在性判断)

- 病灶: `allocation_engine.verify_evidence_items`原以`if as_of_date`真值
  判断决定是否取时间资格——`as_of_date=""`/`0`/`False`/`[]`/`{}`等显式非法
  值与`None`(合法默认→诊断)混同,非法输入静默落入诊断兼容路径。
- 修复: 新增`_as_of_mode()`三态判定——`as_of_date is None`→`diagnostic`
  (受限诊断,DIAGNOSTIC_ONLY);date/datetime实例或经`fp.parse_instant`
  严格解析合法的字符串→`formal`;其余一律`invalid`→整项拒收
  (拒收文本含`研究截止非法`与非法值repr),先于身份核验(截止非法时一切
  时间资格无从谈起,亦满足§7.4"拒收必须含非法研究截止原因")。
- 覆盖值族(实测,测试B1): `''`/纯空白/`2026-10-24INVALID`/`2026-13-01`
  (非法日历)/`2026-10-24T25:00:00`(非法时刻)/`0`/`False`/`[]`/`{}`——
  9种全部verified空+拒收含`研究截止非法`+无`AS_OF_UNKNOWN`路径+无
  fail-closed误报。

## 7. 三维度独立契约(FIX5-01)

| 维度 | 载体 | 语义 | 消费release_date |
|---|---|---|---|
| A 观测新鲜 | `observation_freshness{fresh,status,lag_days,window}` | 身份合法+观测日合法+as_of合法+obs≤as_of+滞后≤已批准窗 | **绝不** |
| B 点时可得 | `point_in_time{status,granularity,release_date,reason}`+`point_in_time_certified` | 既有`compare_release_availability`精度保持判定原样 | 是(唯一判据) |
| C 证据资格 | `evidence_eligibility{usable,status,reason}` | 综合正式资格=身份MAPPED∧fp.assess三问综合 | 经综合层 |

§5.6两条禁止性捷径双双证伪(测试A9): "未来发布→observation_freshness=False"
不成立(A4纯观测FRESH);"observation_freshness=True→正式证据一定可用"不成立
(A4资格拒+verify拒)。发布字段无关性实测(测试A8): 同一锚点仅release不同
(None/已发布/未来发布),三份`observation_freshness`逐字段相等,而综合资格
分别为True/True/False。

## 8. 纯观测函数(freshness_policy新增,唯一新增接口)

`assess_observation_freshness(metric_id, obs_date, as_of)`: 只回答
A已观测+C滞后窗两问,输入仅metric_id/obs_date/as_of(同`fp.parse_instant`
严格解析+`policy_for`已批准窗口),无release_date参数,无`point_in_time`键。
`assess()`**复用**该函数作基底(单一解析与窗口来源,无第二套政策),并在其上
按既有冻结顺序叠加B问: obs∈{UNREGISTERED,INVALID_DATE,NOT_OBSERVED,
FUTURE_DATE}时综合结论=纯观测结论(与既有语义一致);obs∈{FRESH,STALE}时
B问早退(INVALID_RELEASE/RELEASE_BEFORE_OBS/NOT_AVAILABLE_AT_AS_OF)优先于
STALE落定——FIX1~FIX4全部综合判定逐例保持(冒烟+全量回归验证,比较器
`compare_release_availability`排序算法零改动)。

## 9. 综合证据资格(evidence_eligibility)

- `usable=True`: 身份MAPPED∧三问综合fresh(含RELEASE_UNKNOWN与
  POINT_IN_TIME_UNCERTIFIED的观测层兼容——既有FIX4政策,不收紧不放松);
- `usable=False`: NOT_AVAILABLE_AT_AS_OF/STALE/FUTURE_DATE/INVALID_DATE/
  NOT_OBSERVED/INVALID_RELEASE/UNREGISTERED/UNMAPPED/IDENTITY_UNVERIFIED;
- `status`如实携带综合状态,`reason`携带首条结构化理由;
- `is_fresh_anchor`改投影`evidence_eligibility.usable`(FIX5-02): **语义与
  FIX4完全一致**(未来发布仍False;scorecard遗留10天/身份fail-closed/非法
  日期全保留,fix1~fix3既有断言未改即过)——布尔是综合资格投影,不是纯观测
  投影;若误改为纯观测,已知未来发布数据将返回True被正式消费方误用
  (负向敏感性E3证明: 该形态下stale_anchor_warning丢失"点时不可得"警告、
  dpo长期观察放行——真实消费接口级检出)。
- `stale_anchor_warning`逐维度如实(§6.3): 数据过期→"数据过期…滞后X>窗Y";
  未来发布→"点时不可得…晚于研究截止[粒度;详情]";日期非法→"无法判龄…
  研究截止非法/观测日缺失或非法";来源非法→"无法认证时效…来源家族不符/
  身份冲突"——绝不把已知未来发布写成数据过期,既有四族警告文案零丢失
  (fix1/fix2既有断言未改即过)。

## 10. None/""区分与诊断路径边界(FIX5-03)

- `None`→受限诊断: 不做时效门禁(既有语义),**身份/来源家族核验照常执行**
  (§7.3A,不能因缺研究截止接受跨来源伪装——测试C5: 非法来源+None→拒收
  "身份不可认证");verified项pit=`AS_OF_UNKNOWN`+理由含`DIAGNOSTIC_ONLY`
  标记+certified=False,不得claim任何形式时效认证(测试B0/S4)。
- `""`等显式非法→拒收,不进诊断(§7.4强制负例,测试C6):
  键`global_market.data.CPI.close`(authority=macro_collector→非法来源身份)
  ×`as_of_date=""`→verified空+拒收含"研究截止非法"+无AS_OF_UNKNOWN路径+
  身份未获任何绕道认证。
- 正式回写(rg/ae)恒传合法date-only today,不受影响。

## 11. verify_evidence_items核验顺序与verified结构(FIX5-04)

顺序: ①metric+锚点存在 ②**as_of存在性/合法性**(`_as_of_mode`,非法即拒,
先于身份) ③身份/来源家族(formal经tq.identity;diagnostic经
`fp.verify_anchor_identity`直核) ④数值吻合 ⑤obs_date对齐(严格解析)
⑥**综合证据资格门禁**(`evidence_eligibility.usable`,拒收按综合状态分流:
  NOT_AVAILABLE→点时不可得/FUTURE_DATE→未来数据/STALE→数据过期/
  INVALID_DATE→研究截止非法/else→时间资格不成立) ⑦点时结构随verified返回
  ⑧诊断标记(DIAGNOSTIC_ONLY)。verified项结构:
`{metric,value,obs_date,as_of,mechanism,contrary,explained,neutral,
observation_freshness:"FRESH",point_in_time{status,granularity,
release_date,reason},point_in_time_certified}`——FIX4形状零变化
(进入verified即综合可用,纯观测维度必为FRESH,故字符串值语义不变)。
正式verified=综合资格可用(已知未来发布即便纯观测FRESH也整项拒);
RELEASE_UNKNOWN/UNCERTIFIED→观测层兼容全状态透传;诊断不claim时效认证。
时间校验模块不可用→fail-closed拒收(FIX4语义保留,fix4-D3未改即过)。

## 12. 星级/评级/论点回归(FIX4成果零回退)

- 星级门槛/STAR_RULES/支持计数/反证规则/同基底去重/同ISO周观察期/
  评级变更门槛(≥2新增)/论点终态门禁/预测生命周期: **零改动**;
- desc认证分解`/点时认证: 支持项N中已认证x·未认证y(未认证按观测层证据参与)`
  (测试D1)、last_change.via未认证披露+evidence逐项pit/certified(测试D2)、
  evidence_ledger `point_time_certified/point_time_uncertified`(测试D2)、
  旧台账记录缺字段按未认证读+不回填(测试D3)、未来发布拒收文案
  "点时不可得…晚于研究截止"(测试D4)——逐项与FIX4交付一致。

## 13. 联合E2E(FIX5-06四场景, tests/test_p02_w2_fix5.py §F, 全真实模块)

- S1 正常发布: exit0+GLM恰1次+四对象落盘+SHA基线;
- S2 观测新鲜但已知未来发布(真实采集→sb→fe→Gate A→da→rg):
  事实FAIL(NOT_AVAILABLE)+Gate A FAIL→数据包拒(exit2)+周报拒(exit2,
  GLM=0);适配接口三维度=纯观测FRESH(lag55≤窗60)+点时RELEASE_AFTER+
  资格拒;证据层verify整项拒("点时不可得");
- S3 `as_of=""`+非法来源锚点: 正式核验verified空+拒收"研究截止非法"
  (无AS_OF_UNKNOWN);状态层经真实`update_allocation_status`零改写
  (评级保持标配+无last_change+无evidence_ledger;拒收提案留档属合法审计);
- S4 合法未认证观测层证据(naive时间戳发布×date-only截止): 状态照常更新
  且记录保留限度(via"未完成点时认证"+台账0/2,无伪造认证);
- 四对象保护: S2/S3/S4全部场景后weekly_report/report_status/thesis.json/
  allocation_views.json四对象SHA-256==基线,无新报告/状态文件,published=true
  仅发布日,formal身份有效,scan不变——合法更新只发生在独立合成状态文件。

## 14. 负向敏感性(FIX5-05 E, 真实重新引入缺陷形态→断言必失败)

- E1 DEF-001回归(observation_freshness改回`bool(assess fresh)`):
  同§5.4输入下buggy fresh=False/NOT_AVAILABLE≠真实True/FRESH——A4/A8必失败;
- E2 DEF-002回归(`is None`改回真值判断): as_of=''下buggy放行进verified
  +AS_OF_UNKNOWN≠真实空+拒收——B1必失败(经真实verify_evidence_items);
- E3 is_fresh_anchor改判纯观测: 已知未来发布(10-29>10-25)下buggy返回True+
  stale_anchor_warning丢"点时不可得"警告(None)+dpo观察放行(None)≠真实
  False/警告在场/问题在场——真实正式消费接口级检出;verify经
  evidence_eligibility仍拒(双保险)。

## 15. 全量回归(§11, 排除test_glm_live按策略SKIPPED)

本地: **38/38套件0失败**(含W2/W2-FIX1~FIX5、W1/W1-FIX1、P0-1 FIX1~11、
原14 E2E、来源身份/批次/SHA-256、Gate A/B、报告保护、长期论点/观点/预测
生命周期、月度/季度、round3~6对抗)。
既有测试预期调整**2处**(均在test_p02_w2_fix4.py,逐处附原因+负向断言):
- A0: 适配接口键集4段→5段(新增evidence_eligibility,ADD-ONLY;断言收紧为
  五段精确匹配+UNCERTIFIED情形usable=True——结构变化即失败);
- A3: DEF-001语义整改的直接结果——该反例(发布晚于截止)下纯观测维度
  =FRESH/fresh=True/lag53(观测本身在窗内),综合拒绝迁移至
  evidence_eligibility(usable=False/NOT_AVAILABLE);新增负向断言:
  综合资格不得为True、is_fresh_anchor保持False、verify拒收不消失。
其余36套件断言零改动。

## 16. 未修改项声明(§12边界)

- 未修改: 时间比较器排序算法(`compare_release_availability`/`_utc_bounds`
  零改动)、P0-1来源门禁、W1语义、81项指标注册表与金融窗口、星级/评级/
  论点阈值、新闻采集、历史覆盖、真实数据验收、P0-3、Mac LIVE、launchd、
  GitHub main。
- `freshness_policy.assess()`的修改仅为抽取/共享纯观测判断(§8),其综合安全
  判定未弱化(NOT_AVAILABLE/UNCERTIFIED/INVALID_RELEASE全部早退保留,
  fix1~fix3既有断言未改即过)。

## 17. GitHub Actions

- 运行#1(实现提交): run **40988022340**, job **123843500719**(`tests`),
  head_sha=**db586638c9d58e0ebd58c83b50d8191176f2d3ba**, workflow_dispatch,
  **success**(2026-10-30T01:48:38Z→01:49:12Z);日志核验: 39套件其中38个
  `exit=0`+`test_glm_live: SKIPPED(真实GLM付费调用,不进CI)`,0 Traceback,
  `test_p02_w2_fix5 exit=0`在列。
- **运行#2(最终提交=本文档提交)**: 本文档push后dispatch,head_sha=最终提交
  (代码/测试与运行#1零差异,仅docs增量)。**验收入口**: Actions→
  offline-tests→dev/p0-2-w2最新运行,head_sha须等于`git log -1 dev/p0-2-w2`;
  运行编号与会话最终报告一致(不在本文档预写,避免自指编造)。

## 18. DEV/LIVE隔离证据(只读核验, 2026-10-30)

- DEV=/Users/cast/investment-agent-dev(dev/p0-2-w2@db58663), LIVE=
  /Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent(无.git,
  launchd指向LIVE)。
- 逐文件SHA-256比对(本轮涉及4文件): LIVE侧3个存在文件(allocation_engine/
  data_validator/report_generator所在口径承FIX4核验)全部=`50b5d13`(main
  基线,未部署,预期);`freshness_policy.py`LIVE不存在(50b5d13亦无,维持
  前轮结论)。
- 全程未触碰Mac LIVE/launchd/生产数据与状态;未读取或复制密钥;未执行真实
  GLM(测试GLM为≥500字本地替身,CI侧SKIPPED);测试全部使用独立沙箱与合成
  数据;未将JSONL上传公开仓库。

## 19. 未验证项/残留风险(如实声明)

1. `assess_observation_freshness`/`evidence_eligibility`为dev侧新接口,
   LIVE未部署——W2整体验收通过后的部署切换属后续决策,不在本指令范围。
2. 诊断路径(`as_of=None`)现为受限诊断(DIAGNOSTIC_ONLY+身份核验),生产调用
   (rg/ae)恒传合法as_of不受影响;若未来有新调用方依赖该路径产出,仍须先
   明确"非认证结论"的消费边界。
3. `evidence_eligibility.status`沿用fp.assess综合状态词汇;当身份不可认证时
   为UNMAPPED/IDENTITY_UNVERIFIED(适配层词汇),两套词汇并存但各段语义
   唯一,未做跨段换算。
4. CI runner依赖(pandas/yfinance等)由workflow安装固定版本区间,与本地版本
   存在差异——离线套件在两侧均为0失败,但环境差异风险如实声明。
5. verified项的`observation_freshness`字段为字符串"FRESH"(FIX4形状冻结);
   纯观测维度的结构化四元组仅在适配接口(`anchor_time_qualification`)暴露,
   未随verified项冗余传递(下游无消费需求,避免双口径)。

---

**执行声明**: 本轮以FIX4最终提交cc5143a为基线增量开发,优先关闭两个已确认
源码缺陷(DEF-001纯观测/综合分离,DEF-002存在性判断),未重新设计已通过的时效
与研究系统,未删除FIX1~FIX4任何工程成果(下游披露/持久化逐项回归保持)。
**报告: READY FOR W2 INDEPENDENT ACCEPTANCE**(不得自行宣布W2 PASS;
不得关闭P0-2;最终验收由Agent 4独立完成)。
