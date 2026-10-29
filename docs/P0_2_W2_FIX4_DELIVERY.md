# IA-P0-2-W2-FIX4 交付报告(点时认证状态传递与消费)

- 指令: IA-P0-2-W2-FIX4-DEV-v1.0
- 缺陷: IA-P02-W2-FIX3-DEF-001(`POINT_IN_TIME_UNCERTIFIED`在正式证据链丢失)
- 分支: `dev/p0-2-w2`(未合并main,未force push)
- 结论自检: 实现完成+全量回归36套件0失败+CI全绿;**READY FOR W2 INDEPENDENT ACCEPTANCE**(不自行宣布W2 PASS,不关闭P0-2)

---

## 1. 基线(FIX3最终提交)

- FIX3最终提交: `6d7526a5d0a7053d8185717f9c27fe61cc9f1209`(CI run 40911146854,success)
- FIX4开工预检: branch=dev/p0-2-w2, HEAD=6d7526a, 工作树clean, origin/main=50b5d13未动

## 2. FIX4提交

- 实现提交: `965d397969023eda0f6ebe7a8a7238c641c5e4cc`(6文件, +931/−38, CI运行#1全绿)
- 最终交付提交(本文档,docs-only): 其SHA见§14运行#2 head_sha与`git log -1 dev/p0-2-w2`

## 3. 增量差异(6d7526a..实现965d397)

```
scripts/allocation_engine.py | 119 ++++++++++--
scripts/data_validator.py    |  97 ++++++++-
scripts/report_generator.py  |  14 ++-
tests/test_p02_w2_fix1.py    |   6 +-
tests/test_p02_w2_fix2.py    |   3 +-
tests/test_p02_w2_fix4.py    | 730 +++++++++(新增)
6 files changed, 931 insertions(+), 38 deletions(-)
```
compare(页面按分支名解析到最终提交): https://github.com/bojing951-hash/investment-agent/compare/6d7526a...dev/p0-2-w2
最终提交相对实现提交仅docs增量(本文档),代码/测试零差异。

## 4. 累计W2差异(50b5d13..实现965d397, 含W1起全整改链)

44 files changed, 11987 insertions(+), 223 deletions(-)(实测`git diff 50b5d13..965d397 --stat`)。
compare: https://github.com/bojing951-hash/investment-agent/compare/50b5d13...dev/p0-2-w2
与前轮FIX3交付口径(6d7526a时点32 files 7703+/199−)衔接: FIX4新增6文件931+/38−+docs增量。

## 5. 接口修改说明(为什么这样改,未新建第二套比较器)

- **未触碰已通过的时间比较器**: `scripts/freshness_policy.py`与`scripts/fact_engine.py`在FIX4零改动(`git diff`为空)。`compare_release_availability`/`assess`/`validate_fact`原样。
- 新增唯一接口: `data_validator.anchor_time_qualification(anchor_key, info, as_of_date)`——轻量**适配**层,内部仅调用`fp.verify_anchor_identity`+`fp.assess`(同一份已批准时效策略与同一套严格日期解析),把三问分离结果组织为可持久化结构,不重复任何比较逻辑。
- `dv.is_fresh_anchor`改为该接口观测维度的布尔投影(单一来源,行为等价: scorecard遗留10天/身份fail-closed/INVALID路径全部保留,fix1~fix3全部断言未改即过)。
- `ae._anchor_fresh`保留为薄兼容包装,但其ImportError分支由**返回True改为fail-closed返回False**(审计结论: 旧分支在时间校验模块缺席时把证据静默放行为"已核验",属指令点名必改项)。

## 6. 新鲜度与点时认证分离(两维度不互冒充)

`anchor_time_qualification`返回四段:

| 段 | 内容 | 语义 |
|---|---|---|
| `identity` | MAPPED/UNMAPPED/UNVERIFIED+metric_id+reason | 身份不可认证→不授予任何时间资格 |
| `observation_freshness` | {fresh, status, lag_days, window} | A已观测+C滞后窗(数值可用性维度) |
| `point_in_time` | {status, granularity, release_date, reason} | B问as_of时点已发布(历史可得性维度) |
| `point_in_time_certified` | bool | 仅`point_in_time.status==OK` |

`fresh=True`绝不解释为"已证明研究截止前发布";反之`POINT_IN_TIME_UNCERTIFIED`不推翻观测新鲜。认证OK的理由固定附注"锚点元数据声明,未独立核验"(release_date不构成外部独立认证,来源信任限度保留)。

## 7. verify_evidence_items返回结构(形状不变,字段增密)

返回值仍为`(verified, rejects)`。每项verified新增三字段:

```json
{"metric": ..., "value": ..., "obs_date": ..., "as_of": ...,
 "mechanism": ..., "contrary": ..., "explained": ..., "neutral": ...,
 "observation_freshness": "FRESH",
 "point_in_time": {"status": "POINT_IN_TIME_UNCERTIFIED",
                    "granularity": "DAY", "release_date": "2026-10-24",
                    "reason": "发布缺时刻/时区,与截止区间有交,先后未证…"},
 "point_in_time_certified": false}
```

八步核验顺序: ①metric+锚点存在 ②身份/来源家族合法(`verify_anchor_identity`,置于数值比对之前) ③数值吻合 ④obs_date对齐(既有FIX1-01严格解析) ⑤as_of合法 ⑥新鲜度政策 ⑦发布已知时点时判断 ⑧结构化时间资格随verified返回。四情形处置:
- **A 已证明发布早于截止**: 正常verified+certified=True(granularity=INSTANT/DAY/RANGE如实);
- **B 发布晚于截止**: **整项拒收**(rejects,不进verified),原因如实`点时不可得:已知发布…晚于研究截止…`——不再误导性归因为"数据过期";
- **C 精度不足未证明**: 保留为verified(观测层证据),标注`POINT_IN_TIME_UNCERTIFIED`,永不certified;
- **D 缺release_date**: `RELEASE_UNKNOWN`(历史兼容,不伪造);
- 辅助: 诊断路径(调用方未传as_of)→`AS_OF_UNKNOWN`且certified=False(不默认认证);时间校验模块不可用→fail-closed整项拒(`时间校验模块不可用`)。

## 8. 下游消费结果(逐点)

| 消费点 | FIX4后行为 |
|---|---|
| `split_evidence_direction` | 逻辑零改动;分类结果携带逐项认证字段自然向下传 |
| `star_level_from_evidence` | 门槛/STAR_RULES零改动;desc追加`/点时认证: 支持项N中已认证x·未认证y(未认证按观测层证据参与)` |
| `new_supporting_metrics`/`new_contrary_metrics` | 零改动(身份=基底+观测日,与认证维度正交) |
| `update_allocation_status` | 评级变更门槛(≥2新增/触发器/关键传导)零改动;证据路径`via`追加`ae.uncertified_note`(有未认证项才出现,已认证集为空串不虚报);`last_change.evidence`(verified/supporting切片)逐项保留pit dict+certified布尔 |
| `evidence_ledger`(观点, ae) | 新增`point_time_certified`/`point_time_uncertified`两计数(verified全集口径),其余字段原样 |
| `update_thesis_status`(rg) | 论点门禁(≥2新增/invalidation/upgrade触发器)零改动;三处证据路径via同规则追加未认证披露;`last_change.evidence`同构;论点台账同构新增两计数 |
| `uncertified_note`(新增助手) | 缺字段旧记录按未认证计(不推定);全认证返回空串 |

**任何via/ledger/提案文本不含"已完成点时认证"式表述**;需要"已证实历史截止时可得"的表述均不出现于未认证路径。

## 9. 未认证证据是否继续参与观测层分析+边界

**继续参与**(既有兼容政策,阈值一律未动): 未认证但数值/观测核验通过的证据照常计入支持数量/星级/新增判定/评级与论点变更门禁。**边界**: ①正式记录必须可见其未认证(desc分解/via披露/ledger计数/last_change逐项字段);②永不计入"已证实研究截止时可得"类计数;③B情形(发布晚于截止)整项出局,不得参与任何层级;④无任何新门禁以"点时已认证"为前提(现有体系无此先决条件,未引入)。

## 10. 未来发布拒绝(指令FIX4-02 B情形)

- 证据层: `verify_evidence_items`→`点时不可得:已知发布X晚于研究截止Y(区间证明/时刻比较细节)——as_of时点该值不可得,不得作当前证据`,不进verified(测试A3/G3)。
- 上游既有防线原样: fe.validate_fact FAIL(NOT_AVAILABLE_AT_AS_OF)→Gate A不可用→data_assembler exit2→周报exit2(fix4 G3在真实链路复验)。
- 状态层: 拒收进入`ev_rejects`→评级变更理由/提案留档含拒收原因,评级保持(G3断言`proposals[].reason`含`点时不可得`)。

## 11. 真实E2E(test_p02_w2_fix4.py §G, 全真实模块)

固定复现(§A, 真实函数链): 反例1 CPI obs 2026-09-01/release 2026-10-24/as_of 2026-10-25T08:00:00+08:00/value 316.0→FRESH+UNCERTIFIED且不丢弃不冒充;反例2 naive 10-24T23:59×+14:00截止→不认证+精度理由保留到正式接口;反例3 aware 10-24T20:00+08>截止→NOT_AVAILABLE整项拒;正向对照双aware→INSTANT认证+`未独立核验`限度;兼容对照缺release→RELEASE_UNKNOWN可用。
E2E(§G): 正常合格研究真实发布(GLM替身≥500字)→四对象SHA-256基线→**未认证但新鲜场景**(采集端naive时间戳发布经真实sb透传→事实INFO"点时未认证"不FAIL→真实锚点→verify保留两项UNCERTIFIED→`ae.update_allocation_status`+`rg.update_thesis_status`状态照常更新且记录保留认证限度)→**负向未来发布**(真实链路fact FAIL→Gate A不可用→da exit2/rg exit2/GLM=0;证据层拒收→评级被拒留档提案,评级保持)→**四对象保护**(SHA-256全程不变+无新报告/状态文件+published=true仅发布日+formal身份有效+scan不变)。所有合法状态写入发生在**独立合成状态文件**(SYN_V/SYN_T/SYN_V3),未冒充为已发布对象污染。
前后记录: 四对象=weekly_report_20261024.md/report_status_20261024.json/thesis.json/allocation_views.json,SHA-256基线==攻击后(G4断言逐对象比对)。

## 12. 敏感性与计数纪律(指令FIX4-05 C/F)

- 两项有效但未认证合成证据: certified计0,desc明示`未认证按观测层证据参与`,verified/supporting计数不被新字段重复计入;`.prev`同基底去重/反证不计支持/中立不计入/同ISO周=1观察期全部保持(C1/C2)。
- 敏感性: ①删除verified的点时字段→认证分解失真(已认证1·未认证2→已认证0·未认证3)且台账计数由1变0,B1/B3断言必失败;②未认证项certified强改True→台账计数表达式1→3,B3断言必失败(F1/F2,非自证常量)。

## 13. 回归(全量, 排除test_glm_live)

本地: **36/36套件0失败**(含W2/W2-FIX1~FIX4、W1/W1-FIX1、P0-1 FIX1~11、原14 E2E、来源身份/批次/SHA-256、Gate A/B、报告保护、长期论点/观点/预测生命周期、月度/季度)。
既有W2断言更新**2处**(措辞如实化,非放松): fix1 B7与fix2 B5——未来发布拒收原因由误导性`数据过期`改为如实`点时不可得…晚于研究截止`(该情形观测并不滞后,不可得的是as_of时点;断言同时收紧为双关键词匹配)。
CI(GitHub Actions offline-tests): 见§14。

## 14. GitHub Actions

- 运行#1(实现提交): run **40920384499**, job **123611694174**(`tests`), head_sha=**965d397969023eda0f6ebe7a8a7238c641c5e4cc**, workflow_dispatch, **success**(2026-10-29T17:20:29Z→17:21:16Z);日志核验: 37套件`exit=0`(test_glm_live按策略SKIPPED),0 Traceback。
- **运行#2(最终提交=本文档提交)**: 本文档push后dispatch,head_sha=最终提交(代码/测试与运行#1零差异,仅docs增量)。**验收入口**: Actions→offline-tests→dev/p0-2-w2最新运行,head_sha须等于`git log -1 dev/p0-2-w2`;运行编号与会话最终报告一致(不在本文档预写,避免自指编造)。

## 15. DEV/LIVE隔离证据(只读核验, 2026-10-30)

- DEV=/Users/cast/investment-agent-dev(dev/p0-2-w2@965d397), LIVE=/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent(无.git,launchd指向LIVE)。
- 逐文件SHA-256比对(W2整改涉及的8文件): LIVE侧7个存在文件**全部=50b5d13(main基线)**——`data_assembler.py`三方一致(本轮未改);`allocation_engine/report_generator/data_validator/fact_engine/snapshot_builder/research_provenance`6个LIVE=50b5d13≠dev(dev整改未部署,预期);`freshness_policy.py`LIVE不存在(50b5d13亦无,维持前轮结论)。
- 全程未触碰Mac LIVE/launchd/生产数据与状态;未读取或复制密钥;未执行真实GLM(测试GLM为≥500字本地替身,CI侧SKIPPED);测试全部使用独立沙箱与合成数据;未将JSONL上传公开仓库。

## 16. 未验证项/残留风险(如实声明)

1. `anchor_time_qualification`为dev侧新接口,LIVE未部署——W2整体验收通过后的部署切换属后续决策,不在本指令范围。
2. 认证计数为**项级**口径(verified全集/支持集分别如§8),与星级的"独立证据基底去重"口径不同(desc已用`支持项N`标明口径);两者并排展示,未做跨口径换算。
3. `point_in_time_certified=True`仅证明"锚点元数据声明的发布不晚于研究截止",release_date本身未独立核验(理由字段固定附注);外部独立核验通道属后续工程。
4. CI runner依赖(pandas/yfinance等)由workflow安装固定版本区间,与本地版本存在差异——离线套件在两侧均为0失败,但环境差异风险如实声明。
5. 诊断路径(`as_of=None`)语义保持"不做时效门禁"——该路径仅为兼容保留,生产调用(rg/ae)恒传as_of;若未来有新调用方依赖该路径,须先补门禁。

---

**执行声明**: 现在执行W2-FIX4,优先保证时间资格从共享原语传递到正式证据、状态统计和持久化记录,而不扩大工程范围——已完成;未修改81项指标时效窗口及金融政策,未触碰W3~W5/P0-3/Mac LIVE/launchd,未force push/合并/推送main。**报告: READY FOR W2 INDEPENDENT ACCEPTANCE**(不得自行宣布W2 PASS;不得关闭P0-2)。
