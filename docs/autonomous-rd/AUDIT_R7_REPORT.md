# Audit-R7 第七轮审计修复报告

- 受审基线: `4e2f94cfaa097aad333aebcbf3ed5b1adbd2f56b`(分支 `dev/audit-fix-r1`,
  PR #1;外审第七轮三项缺口 R7-01/R7-02/R7-03)。
- 纪律: 每项先在基线复现反例,再最小修复,回归测试经生产入口与交付门;
  真实网络验收;保留已有工作(R6-03 裁决链/身份与算法校验/required 阻断
  与 optional 降级/新中国 B 与 E2E 统计/研究归档能力);未扩展产品功能、
  未瘦身、未削弱验收要求、未提交密钥令牌;合成裁决仅用于标明身份的
  机器门测试。完成后停在等待外部最终审计,不合并 PR、不部署。

## 一、三项缺口关闭表

| # | 缺口 | 状态 | 证据锚 |
|---|------|------|--------|
| R7-01 | 任务起止日期统一解析与窗口覆盖 | ✅关闭 | §二;`tests/test_audit_r7_gate.py` §E/§T/§G(E1-E9,T1-T13,G1-G4) |
| R7-02 | 采集状态贯通与时效判断 | ✅关闭 | §三;§F(F1-F10 九场景+信封面);真网两轮 `r7-evidence/` |
| R7-03 | 真实运行与可复放证据 | ✅关闭 | §四;`docs/autonomous-rd/r7-evidence/`+两归档注记+参数化复算 |

## 二、R7-01 任务起止日期与窗口覆盖

**基线反例复现**(三项,基线 4e2f94c):
1. 近五年 PMI:168 点中窗内实际 1 点,系统记 n_in_window=168 放行;
2. 近十年 BEI_10Y:2016-11-14..2026-11-12 共 2499 点,边界满足容差,仅因
   不足 252×10=2520 被拒;
3. 明确区间 2020-01-01..2025-12-31 DXY:输入只有 2026 年 60 点,被当作
   max_available 通过。

**修复**(`scripts/research_orchestrator.py`):
- **统一解析** `_question_window`: 相对年限+明确日期区间一个入口。日期
  词形四类(ISO/紧凑八位/中文年月日/年-月),缺月日按侧别补齐(起=期首,
  止=月末——「到2025年12月」=2025-12-31);「X以来」=起界无终界(终界
  =研究时点)、「截至X」=终界无起界;**单日期提及≠区间**;词序倒置/
  非法日期(如2020年13月)=指定了但无法解析→阻断,不回落 max_available,
  不静默重排。显式区间与相对年限并存→显式胜(相对记入 basis)。
- **实际观测面**: 窗内有效观测从**实际 dates/values** 计算(去重/剔无效,
  `_effective_window_obs`);快照序列面与 S4 信封面**同一判定**
  (T10: 同 dates 两面 n_in_window 一致);信封无 dates=窗口成员不可核验
  →阻断(不得凭 first/last 裁剪或总量冒充)。
- **日历期望替代 252×年数**: `_expected_in_window` 按频率族计日历期望
  (daily=工作日数/weekly=ISO 周数/monthly=自然月数/quarterly=自然季数),
  下界=期望×半额——真实十年日频因节假日少数十点不再误拒(反例2 由拒
  转满足,n=2499≥floor 1304);月频 59/61 月=合理缺口不再硬否决
  (R5 套件 S3 钉值随口径更新并加 S3b 真负例)。
- **严重断档**: 窗内相邻有效观测**逐对最大间距**超频率族上限
  (daily 30/weekly 60/monthly 130/quarterly 260 天)即阻断——双段密集中
  隔三年洞(总量超半额)被拦(T8, max_gap=1126>30)。
- **错误区间/未知频率/时点不可核验**维持阻断序;未限定范围
  max_available 口径保留(R6 W8 CN 226 月全史不误拒);report 与
  archive 同一判据源(§G 双门)。

**修复后**(§T/§G 37 项中 R7-01 面): 反例1 窗内 n=1<31 阻断;反例2
satisfied(边界容差+日历半额);反例3 窗内 n=0 阻断(window=explicit
2020-01-01..2025-12-31,不当 max_available);正例=五年月频 59 月/
十年交易日 2549 点(节假日缺席,工作日历非周末人工序列)/月频发布滞后
72 天/「X以来」终界对齐;负例=两年冒充五年/三年洞/无 dates 信封/
无法解析词形。测试经 `_evaluate_data_requirements`(生产判定函数)+
`ia_cli research-one --stage report/archive`(生产交付门)。

## 三、R7-02 采集状态贯通与时效判断

**基线缺陷**: 状态经历史加载和查询后丢失(provenance 在 loader 提取时
丢弃);故障注入两项序列截至 2020-12-01 各 156 点,采集失败后
history.ok=true、warnings=[],report/archive 仍通过。

**修复**(贯通链六处,`collection_status_of` 唯一口径不两处漂移):
- `research_history_query.load_metric_series`(macro 面): `item.provenance`
  → payload `collection_status`{mode,last_success_at,
  last_observation_period,carry_forward_from,carry_forward_reason,
  source_sha256,file}——**文件写入时间(source.file_date)/最后成功采集
  时间(fetched_at)/数据统计期(序列末观测)三分**;
- `snapshot_builder.merge_macro_series(prov_out=)`: provenance 随序列入
  快照平节 `series_provenance`(序列未入档状态同不入,防孤儿);
- `workbench_data.metric_series`: 快照面(series_provenance)与采集档面
  (loader)双路透传;root=该数据树持有根(FIX7 可信边界授权缝,生产
  默认与缺省可信根同一,零行为差);
- `ia_cli history` 信封: series.collection_status 随信封+两类如实警告
  (carry_forward 续用/末观测落后研究时点超频率族容忍)——查询层不再
  静默;
- `_evaluate_data_requirements`: 采集状态+**任务时效判定**
  `_freshness_vs_task`——参考端=任务窗止(限定范围;合法历史回放=回放
  窗止不误判)或研究时点(max_available);末观测落后参考端超频率族止侧
  容差(发布滞后已含)=新 outcome **stale_for_task**;仍满足任务窗的
  续用数据=披露放行(basis+spec+报告渲染「续用披露」),不一律判失败;
  状态与时效入 spec(`collection_status`.freshness)随档;
- `agent_judgment.blocked_class_of`+orchestrator notes+`_render_md`:
  stale_for_task 入必要缺口集(attach/report/archive 同源三级),
  报告面「数据陈旧(采集状态贯通判定)」+「续用披露」可见。

**九场景**(§F,全链 collector→loader→工作台→判定→report→archive,
断言查询输出/报告状态/归档结果而非仅原始 JSON): 首次 fresh(三分状态)/
连续第二次(last_success_at 前移)/美国刷新保 CN/单项失败续存(披露
放行)/两项失败(双 carry,最后成功采集不冒充)/无历史可续用(absent
如实缺席,查询无序列+判定 missing)/合理续用(report 渲染披露+
deliverable)/**严重陈旧续用(stale_for_task,report 拒+archive 拒——
外审反例关闭)**/合法历史回放(as_of 钉 2021-01-15,satisfied 不误判);
外加 F10=生产 cmd_history 真调信封采集状态+续用警告。R6 §C 既有
(fresh/续存/净环境/同日重跑/美国刷新遮蔽)不回退。

## 四、R7-03 真实运行与可复放证据

- **两轮真实网络入仓**(`docs/autonomous-rd/r7-evidence/`): round1
  (US FRED 22 项+CN 两指标 fresh n=226,10:58:29Z)+round2(连续第二次
  +美国刷新,11:00:04Z,CN 不被遮蔽);脱敏命令/日志/信封查询/宏档
  sha256/印章绑定实测全部交付;FRED key=既有 LIVE 只读授权进程内注入,
  零落盘零日志(全证据 grep 零命中)。真网验证 R7-02 贯通链:信封
  collection_status=fresh+统计期三分+零警告。
- **新 B 原始输入补全**: `cn-task-b-20261117T083954Z/macro_input/
  macro_20261117.json`(sha be1f7680…,与 B 包 README 哈希表一致,
  provenance 完整: fetched_at/coverage/revision_policy/
  observation_anchor)。
- **recompute_r6b.py 参数化**: `--seat/--out` 覆写+默认 `__file__` 相对
  定位;校验失败非零退出;净 cwd 重放 rc=0,105/105,产物与冻结档核心段
  162 行逐行一致(冻结档尾席位追加 6 行 append-only 保全,不覆写)。
- **版本绑定**: `_git_state` 三级链(运行树 git 库→代码树→
  CODE_VERSION.json 印章)+run.git_head_source/git_diff_sha256 随档;
  引擎树(代码副本,新 B run.git_head=null 根因)自此可绑定——R7 引擎树
  实测印章命中(基线 4e2f94c+工作树差异指纹 70b83f57…)。
- **新旧 B 注记**(append-only,原档零改动): 旧 B=执行版本(engine_cn
  含未合并 R45 席位改动)+当前复验 CONTRADICTED 3/9+NOT_VERIFIED 标记+
  新链替代;新 B=null 根因+输入侧版本锚定+复算重放口径。
- **干净检出重放**: r7-evidence README §四+B 包 README(一条命令研究席
  重放+独立席复算重放)。

## 五、交叉核对(版本/输入/研究/裁决/归档)

新 B: 输入(快照 e2e91525…+macro be1f7680…,macro_input 随包)→研究席
重放(与 R5 冻结输出逐字节一致)→判断档 v3(数字零改动)→契约门
(VERIFIED 6=4V+2STALE,与 attach 记录一致)→独立席 r6-b-review
(105/105,参数化重放 162 行核心一致)→归档(content_sha256 06624da7…,
链 UPHELD fresh)——五面互证;run.git_head=null 已注记补锚。R7 两轮:
命令→日志→宏档 sha→信封状态→印章哈希,可独立复核。

## 六、测试与验证

- `tests/test_audit_r7_gate.py`(新增): 37/0(§E 9+§T 13+§G 4+§F 11)。
- 既有面不回退: R5 30/0(S3 钉值随 R7-01 口径更新+S3b 真负例)、
  R6 25/0(W2 钉值 1304/2609 同因)、R4 29/0、R1 34/0、arch-t3/DFF/
  stage-coverage/C7-P2/GAP08 等受影响面逐件绿。
- 全电池与 CI: 见 §七(最终 HEAD)。
- 四态: 已实现=R7 三项代码+测试;离线验证通过=上述套件+九场景;
  真实在线验证通过=两轮真网采集/刷新/查询;尚未验证=旧 B 契约门基线
  重跑 CONTRADICTED(注记处置,新链替代)。

## 七、最终版本与 CI

- 分支 `dev/audit-fix-r1`,本轮代码尖=`8620ea8b81e4827a1adb37b92042befaab575811`
  (单波: 三缺口代码+新套件+证据包+注记;PR #1 open,未合并未部署)。
- CI run [44072231584](https://github.com/bojing951-hash/investment-agent/actions/runs/44072231584)
  (12dc6cf)三 job **全绿**: `tests (3.11)`/`gates`/`tests (3.12)` 均 success
  (含本轮新套件 test_audit_r7_gate.py——CI 按 tests/test_*.py 全枚举自动纳入)。
- 全电池(直跑口径,与 CI 同形): **178 绿+1 已档设计红+1 SKIP**——
  唯一红=`test_arch_reform_phase6` D3「整改树工作面净」在本轮未提交
  修改件上的提交前红(设计行为,R5/R6 同判例),**提交后净树复跑 29 PASS/
  0 FAIL rc=0(本轮已亲验)**;1 SKIP=`test_model_live`(CI 既有跳步)。

## 八、剩余限制(如实)

1. 显式日期词形解析覆盖四类规范形+侧别缺省;非规范自然语(如「疫情
   以来」「去年」)仍走相对年限/未限定口径,不猜词义。
2. 时效容忍按频率族止侧容差(含发布滞后),不按指标级发布日历精判
   (注册表 release_date_available 面未接入本判定——增量面,如实移交)。
3. 旧 B 契约门 CONTRADICTED 面: 引擎侧 R45 修复合入 main 前两代码线
   行为不一致(R6 §七移交项,超本轮范围)。
4. FRED/CN 真网验证截至 2026-11-17T11:00Z 两轮;持续采集面的稳定性
   由后续正式采集轮次继续佐证。

> 没有证据的项目标记 NOT_VERIFIED。本报告完成时停止在「等待外部最终
> 审计」;不合并 PR、不部署。
