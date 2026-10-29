# IA-P0-2-W2-FIX3 交付报告: 混合精度与未知时区比较错误认证修复

- 任务: IA-P0-2-W2-FIX3 (指令 IA-P0-2-W2-FIX3-DEV-v1.0, 缺陷 IA-P02-W2-FIX2-DEF-001)
- 分支: dev/p0-2-w2 | 仓库: bojing951-hash/investment-agent (DEV=/Users/cast/investment-agent-dev)
- 日期: 2026-10-30
- 状态结论: **CODE FIXED — 独立验收材料齐备, READY FOR W2 INDEPENDENT ACCEPTANCE**
  (最终裁决权属 Agent 4; 政策批准原始证据复现性与独立核验路径见§8)

## 1. 开发前基线

- 起点: `d1ceac60bf47cc0e79b84b18478e03fa983c487b` (W2-FIX2 失败验收 Commit,
  工作树clean, §4只读预检通过: 独立仓库/无symlink/HEAD=d1ceac6)
- origin/main: `50b5d13` (P0-1封版, 全程未合并main/未force push)
- W1 封版: `69d7fc7` (累计diff基线)

## 2. 最终提交

- FIX3 实现提交: 见 git log(本文档首次随实现提交入库; SHA见§14 CI运行#1 head_sha)
- FIX3 最终交付提交: 本文档CI/隔离核验补录提交(仅docs)即最终提交,
  其SHA见§14运行#2 head_sha 与 `git log -1 dev/p0-2-w2`。

## 3. 变更范围

- 增量 diff(d1ceac6→实现): 统计见§14(页面compare链接以分支名解析到最终提交)
- 累计 diff(69d7fc7→实现): 同上
- 改动文件: scripts/freshness_policy.py(区间证明原语+_utc_bounds+比较器B/C/D
  分支重写+assess注释), scripts/fact_engine.py(UNVERIFIED_PRECISION纳入INFO
  披露分支+注释), tests/test_p02_w2_fix3.py(新增39检查), 
  tests/test_p02_w2_fix2.py(仅E2一处期望变更, §12逐项说明),
  docs/P0_2_W2_FRESHNESS.json(HSAHP gate_b_impact 1行, §9), 本交付文档
- 未改: config/metric_registry.json生效窗口(HSAHP=7/SB_FLOW=10/HSI=5/HSCEI=5),
  P0-1/W1身份与来源逻辑, Gate A三态, 新闻采集器, 历史数据, Mac LIVE, launchd

## 4. FIX3-01: 缺陷定义与修复

**缺陷**(DEF-001): FIX2比较器在混合精度下仍以名义日期差作确定性依据——
date-only发布×时间戳截止(任意日差)与naive时刻×aware截止(|日差|≥2)均可能
返回确定性RELEASED_BEFORE, 经assess()升为point_in_time.status=OK。原注释
"相差≥2日任何±14h时区解释都无法翻转先后"在极端偏移组合下为假。

**组一反例**(§5.2): release='2026-10-24'(date-only), as_of=
'2026-10-25T08:00:00+08:00'(=10-25T00:00Z)。实际可能发布10-24T23:00-04:00
(=10-25T03:00Z)晚于截止——date-only不能证明发布先于时刻级截止。
修复后: `UNVERIFIED_PRECISION`, assess=`POINT_IN_TIME_UNCERTIFIED`, fe=INFO。

**组二反例**(§5.3): release='2026-10-24T23:59:00'(naive), as_of=
'2026-10-26T00:00:00+14:00'(=10-25T10:00Z)。发布按UTC-11解释=10-25T10:59Z,
晚于截止59分钟——名义差2日不可为凭。修复后: `UNVERIFIED_TZ`(detail明示
"名义日差2日不足为凭"), 点时不认证。

**修复设计**(§5.4/§5.5, 保守而简单):
1. 双aware完整时间戳→绝对时刻比较(granularity=INSTANT, 不变);
2. 双date-only→历史日粒度比较(granularity=DAY, 语义="截止日之前已发布",
   不证明日内时刻先后, 不变);
3. 同一名义日(至少一侧带时刻)→UNVERIFIED_SAME_DAY(不变);
4. 其余混合精度(date-only×时间戳, 或含naive时刻)→**唯一确定性依据=
   现实时区界UTC区间证明**: `_utc_bounds()`给出每侧可能UTC时刻闭区间
   (aware=精确单点; naive墙钟W→[W−14h, W+12h]; 日历日D→
   [D 00:00−14h, D 23:59:59.999999+12h], 界=tz数据库在用极值−12:00~
   +14:00)。区间无交→RELEASED_BEFORE/AFTER(granularity=**RANGE**,
   detail披露区间值与"发布缺时刻/时区"事实); 区间有交→UNVERIFIED_TZ
   (含naive)或UNVERIFIED_PRECISION(纯精度失配)。**绝不再以名义日差
   (含|dd|≥2)作确定性认证依据**;
5. 未实现全球时区上下界以外的推理; RANGE结论=先后已证但发布具体时刻
   未知, 不冒充INSTANT精确认证(§5.4语义命名映射: EXACT_INSTANT→INSTANT/
   DATE_LEVEL→DAY/区间证明→RANGE/UNVERIFIED_PRECISION与TIMEZONE_UNSPECIFIED
   →UNVERIFIED_PRECISION与UNVERIFIED_TZ/INVALID→INVALID_*)。

**区间证明正确性边界**(§5.5"严谨算法+极端时区测试", 见§5):
- 组二翻转机理: naive墙钟区间上界=W+12h(−12:00解释), aware截止可在其
  墙钟−14h处(+14:00解释), 两侧合计26h不确定性>名义2日差48h减去两侧
  日内位置后的余量时即可翻转——故确定性只能来自区间无交, 不能来自日差;
- 极端偏移测试: +14:00截止与naive区间上界差1秒仍有交(D3); −12:00侧
  同理对称覆盖(D2反向); RANGE正向两方向(D4/D5)。

## 5. FIX3-06 D族关键用例(区间证明边界)

| 用例 | 输入 | 区间 | 判定 |
|---|---|---|---|
| D2正 | naive 10-24T08:00 × aware 10-25T08+08 | [10-23T18Z,10-24T20Z] vs 点10-25T00Z | 无交→RELEASED_BEFORE(RANGE) |
| D2反 | aware 10-25T08+08 × naive 10-24T20:00 | 点10-25T00Z vs [10-24T06Z,10-25T08Z] | 有交→UNVERIFIED_TZ |
| D3极 | naive 10-24T23:59 × aware 10-26T00:00:01+14:00 | 上界10-25T11:59Z vs 点10-25T10:00:01Z | 有交(差1秒59分)→UNVERIFIED_TZ |
| D3远 | naive 10-24T23:59 × aware 10-28T00:00+14:00 | 上界10-25T11:59Z vs 点10-27T10:00Z | 无交→RELEASED_BEFORE(RANGE) |
| D4正 | date 10-20 × aware 10-26T08+08 | 上界10-21T11:59Z < 点10-26T00:00Z | RELEASED_BEFORE(RANGE)+点时OK |
| D4反 | date 10-28 × aware 10-24T08+08 | 下界10-27T10:00Z > 点10-24T00:00Z | RELEASED_AFTER(RANGE)+NOT_AVAILABLE+fe FAIL |
| D5 | date 10-24 × aware 10-27T08+08 | 上界10-25T11:59Z < 点10-27T00:00Z | RELEASED_BEFORE(RANGE)——同发布远截止可证, 近截止(组一)不可证 |

D4反=FIX1未来发布保护(CPI obs 09-01/release 10-28/as_of时刻)在混合精度
下经区间证明保留: date-only未来发布仍FAIL NOT_AVAILABLE_AT_AS_OF, 绝不
因精度失配而放行(§11 E2E链路级复验, 见§10)。

## 6. FIX3-02: 正式消费端一致性

- fp.compare_release_availability: 不再虚报确定性RELEASED_BEFORE(§4);
- fp.assess: RELEASED_BEFORE透传granularity(INSTANT/DAY/RANGE三者语义
  分明); UNVERIFIED_SAME_DAY/UNVERIFIED_TZ/**UNVERIFIED_PRECISION**→
  POINT_IN_TIME_UNCERTIFIED(fresh=True仅观测新鲜维度, §5.6两维度分离);
- fe.validate_fact: RELEASED_AFTER(INSTANT/DAY/RANGE)→FAIL
  (NOT_AVAILABLE_AT_AS_OF); 三个UNVERIFIED_*→INFO"点时未认证"(新增
  UNVERIFIED_PRECISION入列); 无release→RELEASE_UNKNOWN(月频WARN, 不变);
- dv.is_fresh_anchor/stale_anchor_warning/metric_registry_info: 经assess
  status分发自动一致; 警示披露[RANGE+区间依据(E3); registry_info的
  release_provenance维持"未独立核验"表述(E2);
- rp.recompute_gate_a/gate_status: Gate A研究截止三态不变(§12 F1回归);
  点时先后由事实层全精度判定(既有注释契约保持);
- Gate B: 仅拒绝性消费RELEASED_AFTER; 观测新鲜(fresh=True)不得冒充点时
  认证——E1断言fresh=True与POINT_IN_TIME_UNCERTIFIED同时成立且消费端
  (fe/dv/dpo)无一将其当已验证发布(E1/E2/E5);
- 两维度强制验证(§6"强制验证"): 组一/组二均以**真实项目函数**全链调用
  (compare→assess→validate_fact→is_fresh_anchor/stale_warning→
  真实快照Gate A→da/rg正式入口), 非模拟分支(A1/A2/E族/F5)。

## 7. FIX3-03: 历史兼容与正向对照(test_p02_w2_fix3.py B/C族)

- 双aware早于×2组偏移(+08同区B1, −04×+02跨区B2)+等于(+08×Z同一时刻
  两种写法B3)→正常认证(INSTANT);
- 双aware晚于(B4)→拒绝(INSTANT+NOT_AVAILABLE+fe FAIL);
- 不同偏移名义日期误导序两方向(B5)→按UTC正确处理;
- 双date-only跨日(C1)→RELEASED_BEFORE(DAY)+点时OK但granularity=DAY
  (明确粒度, 不冒充INSTANT); 跨日未来(C2)→RELEASED_AFTER(DAY)+
  dv"点时不可得"(FIX1 B4兼容);
- 同日守恒态(C3): date-only×ts同日与双date-only同日均UNVERIFIED_SAME_DAY;
- 缺release(C4)→RELEASE_UNKNOWN+新鲜度按观测窗(FIX1 B1兼容);
- 无效日期(C5×5+C5b)→INVALID_RELEASE受控拒绝; None=函数级缺席→
  RELEASE_UNKNOWN(与显式非法值区分);
- 发布早于观测(C6)→RELEASE_BEFORE_OBS语义非法;
- 显式非法research_as_of→Gate A三态fail-closed不回退(F1);
- 正常月频发布滞后: 月频缺release=WARN披露不FAIL既有数据(E5快照级:
  组一date-only release进入真实快照→事实不FAIL+INFO+gate_a不受损);
- 过期BTC按现行2天规则: W2/W1全量回归零变更(§11), 未动注册表窗口。
- 未删除/弱化FIX2已通过测试(除E2一处, §12逐项说明)。

## 8. FIX3-04: 政策批准原始证据(不重复生成, 只读复现+独立核验路径)

**既有索引**: docs/P0_2_W2_FIX2_APPROVAL_FORENSICS.md(四轮UUID/call_id/
时间戳/逐字问答/行号/摘录SHA-256), 原始记录未修改。

**本轮只读复现结果**(2026-10-30, 开发者级C+D):
1. 原始JSONL为append-only: 当前14,455,807字节(取证后本会话追加),
   **前12,553,908字节SHA-256=34b23023a6b0eb6db47895ed994332c080c9124128
   90b1f853ba9e03f82245f5, 与取证记录逐字节一致**——四轮内容未被改动;
2. 四轮配对逐项复现(行号/call_id/时间戳全符):
   R1=2248/2249 call_3e926492…(07:55:51.871Z→07:57:50.613Z);
   R2=2303/2304 call_68e287b4…(08:08:20.160Z→08:37:35.660Z);
   R3=3759/3764 call_d7072289…(11:19:26.283Z→11:25:31.034Z);
   R4=4431/4432 call_2f9f0965…(13:21:35.613Z→**14:31:53.712Z**);
3. R4逐字内容复现: AskUserQuestion问题含"HSAHP/并集/SB_FLOW/维持10天",
   tool_result含所选"缩短至7天（推荐）"。

**最小只读独立核验指令**(Agent 4或用户在本机执行, 零修改):
```bash
python3 - <<'EOF'
import hashlib, json
p='/Users/cast/.claude/projects/-Users-cast-AI--/b16f1517-4837-4cee-9466-4b517752687b.jsonl'
raw=open(p,'rb').read()
print('前缀不变:', hashlib.sha256(raw[:12553908]).hexdigest()
      =='34b23023a6b0eb6db47895ed994332c080c912412890b1f853ba9e03f82245f5')
L=raw[:12553908].decode('utf-8',errors='replace').splitlines()
for ln in (2248,2303,3759,4431):
    a=json.loads(L[ln-1]); r=json.loads(L[ln])   # 问/答相邻行(R3答在3764)
    print(ln, a['message']['content'][0]['id'],
          r.get('timestamp'))
print('R4所选:', '缩短至7天' in L[4431])
EOF
```

**证据等级与授权边界**(如实区分, 不伪称):
- 历史四轮授权: 已由开发者只读复现(C+D级); **U级升级=Agent 4或用户
  按上述指令读取本机JSONL原文**;
- 若Agent 4无法读取本机JSONL: **用户在Agent 4对话中直接确认当前生效
  政策**(HSAHP=7天/SB_FLOW=10/HSI=5/HSCEI=5/DFEDTARU与L=10/月频60/
  中国大陆日频10/BTC=2)即构成**新的明确批准记录**——它确立当前政策
  授权, 但不等于已核实原始JSONL的历史真实性, 两者不得混同;
- 开发者不替代用户重新批准政策; 完整JSONL不上传GitHub; 摘录仅含
  政策问答本体, 无密钥/无关对话。

## 9. FIX3-05: HSAHP时效矩阵文档修订

docs/P0_2_W2_FRESHNESS.json 仅HSAHP行`gate_b_impact`1行(其余80项与同文
6项未动, metric_id锚定替换):
- 旧文(错): "旧7天/daily(china前缀=7(无.close字段))→新10天/daily…"——
  "新10天"为FIX1阶段口径, FIX2后失真;
- 新文: "三版本口径(FIX3-05厘清,不得混同): W2开发前Gate B旧规则≈7天
  /daily(china前缀=7,无.close字段); FIX1阶段曾达10天/daily(round-2
  批准,身份经canonical映射+注册表策略,频率误判消除); FIX2以后实际
  7天/daily(第四轮10→7,与Gate A一致)——现行生效=7天(registry approved)"。
- 核查: MD矩阵HSAHP行/总量行/Gate A影响行与注册表一致(effective_now=7,
  SB_FLOW=10/HSI=5/HSCEI=5不动); windows块历史字段(registry_pre_w2=5/
  engine_legacy=7/gate_b_legacy=7)本就准确, 未动。**未改任何生效窗口**。

## 10. FIX3-06与§11: 专项测试+联合E2E

tests/test_p02_w2_fix3.py **39检查全过**(A强制反例5/B正向5/C兼容9/
D未知时区5/E消费端5/F回归+E2E 6/G敏感性2+快照打印2):
- A: 两组反例真实函数链+指令算例对照(A1b/A2b用aware版本证明风险真实);
- E5: 组一进入真实快照(date-only release+时刻级research_as_of): 事实
  INFO不FAIL+gate_a不受损——不因混合精度不确定而误伤/编造;
- §11联合E2E(F4~F6): 真实发布事务(exit0+GLM恰1次)→四对象(周报/发布
  状态/thesis.json/allocation_views.json)SHA-256基线→**混合精度非法
  认证尝试**(新采集日构建前注入date-only未来发布10-29×时刻级截止→
  事实FAIL NOT_AVAILABLE+Gate A不可用→数据包拒exit2+周报拒exit2+
  GLM=0+零状态回写)→四对象SHA-256全程不变+无新报告/状态文件+
  published=true仅发布日+formal身份有效+scan不变;
- G敏感性: monkeypatch真实重引入FIX2名义日差比较器→A族条件由真变假+
  组二不再UNVERIFIED+assess点时被升为OK三路同时触发(检测非常量),
  退出后真实比较器恢复无残留。

## 11. §12 完整继承回归与期望变更清单

36套全绿(35 exit=0+test_glm_live按契约跳过): W2(44)/W2-FIX1(53)/
W2-FIX2(43)/W2-FIX3(39)/W1(46)/W1-FIX1(41)/P0-1 FIX1~11/E2E
(four_weeks/frozen14/orig14)/gate_chain/fact_engine/snapshot/round3~6/
p0~p7/phase3~4/datafix。

**既有测试期望变更仅1处**(逐项说明, 无断言删除/弱化):
- test_p02_w2_fix2.py E2: UNVERIFIED_TZ→RELEASED_BEFORE(RANGE)+
  点时POINT_IN_TIME_UNCERTIFIED→OK(RANGE粒度)+无"点时未认证"INFO。
  理由: FIX2"相邻日一律不可证"对该输入(naive墙钟10-24T08:00×aware截止
  10-25T08+08)是**欠声称**——naive最晚可能UTC(10-24T20:00Z)严格早于
  截止(10-25T00:00Z), 指令§5.5第5条明示可验证时间范围证明允许确定性
  结论。变更是**收紧谎报**(把"说不可证"改为"区间已证但标RANGE非
  INSTANT"), 非放宽; 断言数由4增为6(新增granularity=RANGE与无INFO
  断言), 原断言意图(不假设UTC/HKT/本地时区)保留于D2反向用例。
- 另: docs/P0_2_W2_FRESHNESS.json 1行文档修订(§9, 非测试期望)。

## 12. §13 允许修改范围遵守

实际改动=允许清单子集: freshness_policy.py/fact_engine.py(必要消费接口)/
test_p02_w2_fix3.py/必要既有W2测试(仅fix2 E2一处)/FRESHNESS.json/.md核查
(仅json 1行)/交付文档。未动: metric_registry生效窗口/P0-1与W1身份来源
逻辑/新闻采集器/历史回补/真实数值验收/新工作流/LIVE/launchd/main。

## 13. §4 隔离(开发前预检+最终核验)

- 开发前(只读): DEV git根=/Users/cast/investment-agent-dev(独立仓库, 无
  symlink), branch=dev/p0-2-w2, HEAD=d1ceac6, 工作树clean(无未提交修改
  需核实保留), origin/main=50b5d13;
- 最终核验(FIX3提交后只读): 见§14回填(DEV HEAD=FIX3最终SHA; LIVE inode/
  blob对比/launchd目标与FIX2轮一致未动)。

## 14. GitHub CI与版本交付

- 工作流: offline-tests.yml, workflow_dispatch, ref=dev/p0-2-w2
- 运行#1(实现提交): 最终提交后回填(run id/head_sha/逐套退出码);
- 运行#2(最终交付提交): 本文档补录push后dispatch, head_sha=最终提交
  (代码/测试与运行#1零差异, 仅docs)。验收入口: Actions→offline-tests→
  dev/p0-2-w2最新运行, head_sha须等于`git log -1 dev/p0-2-w2`;
- 增量diff: d1ceac6→dev/p0-2-w2; 累积diff: 69d7fc7→dev/p0-2-w2
  (https://github.com/bojing951-hash/investment-agent/compare/69d7fc7...dev/p0-2-w2)。

## 15. 未解决事项与证据等级

| 事项 | 状态 | 证据等级 |
|---|---|---|
| DEF-001 代码修复 | 已修复, 39+36套件证据 | 开发者离线验证(C+D), 待Agent 4独立复核 |
| 历史四轮政策批准 | 原始记录未改+前缀哈希复现+四轮配对复现(§8) | C+D(开发者复现); U级=Agent4/用户读JSONL |
| 当前政策授权(如需) | 用户可在Agent 4对话直接确认现行窗口(§8清单) | 用户当场确认=新批准记录(不伪称已核历史) |
| 恒指官方方法事实 | 指令交付(Agent 4已确认)+URL佐证 | 承FIX2轮结论不变 |
| CI 最终运行 | 运行#2=最终提交后dispatch(§14回填) | GitHub公开可验证 |
| DEV-LIVE 隔离 | 最终提交后只读核验(§13/§14回填) | Mac本地只读 |
