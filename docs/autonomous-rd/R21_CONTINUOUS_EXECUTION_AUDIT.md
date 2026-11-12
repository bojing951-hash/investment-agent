# R21 — Charter 10 阶段二: 持续执行验证波报告

> 波次: dev/rd-r21-continuous-exec(基线 6a33c2c)·2026-11-12。
> 依据: CHARTER_10_RECTIFICATION.md §四(P0)——「不得根据历史文档声称已经配置成功,
> 必须检查真实配置、运行日志和执行结果」;§4.4 七项「如实标 PASS/NOT_VERIFIED/FAIL,
> 不得假装成功」。
> 本报告全部结论来自本席当日实查(命令亲跑/文件亲读/日志亲 tail),历史档只作交叉
> 对照、不作证据。

## 1. §4.4 执行环境验收矩阵(七项终判)

| # | 验收项 | 终判 | 证据(全部当日实查) |
|---|---|---|---|
| 1 | 一轮完成后自动进入下一轮 | **PASS** | launchd `com.investment.rd-headless` plist 实读: `StartInterval=14400`(4h)+ `round.sh` 全链;真日志 5 轮: 11-11 22:15 → 11-12 02:57 / 07:22 / 12:18 / 18:21(`ls -t ~/agent-loop/headless/logs/`),各轮产出 `rounds/index.md` 行,零用户交互;18:21 轮 18:48:08 `round done rc=0`。**诚实注记**: 触发依赖 Mac 唤醒——实际间隔 4.5~6h 漂移(深夜/会议睡眠窗),4h 为名义值;非缺陷,环境特性 |
| 2 | 上下文压缩后恢复 | **PARTIAL** | 交互面=PASS 真证: 本操作者会话 2026-11-12 当日真实经历上下文压缩,R21 分支波(本波)无损续跑(恢复链=仓内状态档+检查点,不依赖聊天记录);无头面=**NOT_VERIFIED**: `-p` 无头会话有原生 auto-compact 机制,但既有轮日志(≤90min 墙钟)无已观测压缩事件,「压缩后恢复」在无头路径无实例证据——如实不判 PASS |
| 3 | 新会话从检查点恢复 | **PASS** | R20 恢复验收套件(62 判,`tests/test_rd_r20_recovery.py`: `python -I` 零上下文正例 RECOVERY-OK+负例 rc 3/4/5)+真实例证: 本 R21 fork=全新上下文仅凭 RESUME/STATE 文件开工;18:21 无头轮=第二实例从仓内状态接手 R20 |
| 4 | 任务失败后安全重试 | **PASS** | 真实撞车事件: 11-12 18:21 无头第二实例检测 `/tmp/r20-wt` 并发改写(ps+文件变异探活)→ **零提交零 finalize 让席**,index.md 留诚实让席行,rc=0;门拒路径(refuse rc=1 无日志行/浅克隆等)套件内反复演练 |
| 5 | 资源限制触发后正确停止 | **PASS**(两子面如实注记) | **本席活测**(19:16): STOP 文件在场→`SKIP: STOP 文件在场…移除后恢复调度` rc=0;锁在场→`SKIP: 上一轮仍在跑(age=0s)` rc=0;测后环境复原(STOP/lock 均清)。机制面: 90min 墙钟(`round.sh:12` MAX_WALL_SEC=5400,看门狗 `:68-71`)与 $5 预算上限(`:13`+`--max-budget-usd :53`)实现齐备但**未观测到真实触发**(轮均提前完成,launchd.err 的 watchdog Terminated 行=正常收尾清理痕迹,非超时击杀)——机制在场、实例未观测,如实注记不冒认 |
| 6 | 无法获得授权时正确停止 | **PASS** | 权限面实读 `round.sh:63-65`: deny `git push*`/`git remote*`/`ssh *`/`scp *`/`curl *`/`npm *`/`pip *`/`rm -rf *`/`git switch main*`;PROMPT.md 明文「被允许清单拒绝=如实记录为阻塞,不是让你绕过」+「付费类须用户在场亲批」。真实实例两侧: 无头轮零越权记录(5 轮日志无 push/付费尝试);操作者侧 LIVE 部署曾被分类器两次拦截→脚本停放 /tmp 待用户终端亲跑(R9/R10 记录),无绕行 |
| 7 | 外部监督程序在授权范围内恢复中断任务 | **PASS** | launchd 即外部监督者: 02:57/07:22 两轮在操作者不在场时段自动拉起并完成(日志时间戳+rc=0);授权边界=第 6 项 deny 面;恢复语义=第 3 项 RESUME 链;全程零越权动作 |

**矩阵结论**: 6 PASS + 1 PARTIAL(第 2 项无头面 NOT_VERIFIED 子面),零 FAIL、零冒认。
PARTIAL 的补救路径=候选钩子包(§3)+未来无头轮真实压缩事件积累。

## 2. 钩子与上下文机制真相清单(逐项实查,非文档口径)

| 检查面 | 实查命令 | 真相 |
|---|---|---|
| 用户级钩子 | 读 `~/.claude/settings.json` | 仅 gstack Stop 钩子(timeline-stop-hook);**无** investment 相关 PreCompact/SessionStart |
| 项目级钩子 | 读 dev 树 `.claude/settings.json` | PreCompact/SessionStart 在场,但仅 `echo … >&2` 提醒(弱);**`.claude/` 在 `.gitignore:16`**→ worktree/CI 克隆/干净装机(AC9 面)全部不存在=本地不可移植 |
| 上下文压缩 | 本会话亲历 | 原生 auto-compact 真实可用(交互面当日两次续跑);压缩纪律文档=RESUME「快照纪律」节+CLAUDE.md(人读面) |
| 机器强制力 | CI 工作流实读 | 一致性门六项=CI 硬门(offline-tests.yml)+finalize 管线内嵌,与钩子无关、随克隆走 |
| 分类结论 | — | 钩子=提示层(弱+不可移植);强制层=门+管线(强+可移植)。**修复**: 钩子升级为随仓分发的候选安装物(§3),SessionStart 从 echo 升级为只读跑门播报 |

## 3. launchd 与无头 runner 实查发现

- **三个任务实存**(`launchctl list | grep -i investment`): `rd-headless`(last exit 0)/`daily`(last exit **1**)/`weekly`(last exit **2**)。
- `com.investment.rd-headless.plist` 逐键: bash round.sh / StartInterval 14400 / RunAtLoad=false / 日志=launchd.out/err.log。无代理环境键(无头轮=dev 面工作,采集非其职责,如实注记)。
- `round.sh`(73 行)约束实现行号: 急停 STOP `:10,:19-23`;互斥锁(陈锁>6h 清)`:11,:25-39`;**90min 墙钟** `:12,:68-71`;**$5 预算** `:13,:53`;**禁 push/remote/ssh/scp/curl/npm/pip/rm-rf/切 main** `:63-65`。
- 无头轮节奏真况: 5 轮全在 11-11~11-12;rounds/index.md 22 行含 R5→R20 全记录+1 条并发让席行。
- **LIVE 生产面观察(非本波范围,如实登记)**: daily 07:12 退出码 1(`daily_20261112.log`: 4 关键步骤失败,Gate A ZQ 族采集缺口=已知既有项,当日面为 v0.15.0 部署**前**旧面);weekly 上周六 exit 2 同因(既有非回归,观察钟 11-14 周六)。明日 07:00 daily 首跑 v0.15.0 面——**移交操作者关注**。

## 4. 防死循环与 finalize 协议加固(本波代码交付)

- **`scripts/rd_progress_watch.py`(新)**: 从 git 对象重建每轮改动面(finalize 事件=`git log -G` RD-CHECKPOINT 块行;轮改动面=相邻 finalize 间 diff),三分 code/tests-only/docs-only;**漂移预警**(连续≥2 轮无生产代码进展→§4.3 根因复审)+**返工预警**(同一生产文件连续两轮被改,tests/data 豁免);恒 exit 0(顾问非门),`--strict` exit 3,浅克隆/观察窗不足降级注记。真仓狗粮: 当前窗=1 区间(仅 R20 有盖章史)——机制随轮次积累自动生效。
- **`rd_checkpoint.py` 接线**: 盖章成功后随行播报顾问输出(降级不阻断)。
- **CI 新步**: 一致性门后跑顾问(非阻塞,预警可见性)。
- **finalize 协议事故弧回归锁**(`tests/test_rd_r21_deadloop.py` D 节,18 判): 盖章→门绿 → 再落代码提交→**①基线红**(R20 事故形态被门拦截)→ 重新盖章(幂等)→门绿=对账自愈。finalize=分支最后一笔纪律从此有机器证。
- **预期自证**: R20→R21 因 `rd_checkpoint.py` 连续两轮被改,合并后顾问将如实弹**返工预警**——这正是 §4.3「重复修复同一问题?根因复审」的正确行为(根因=R20 事故补防线,非死循环),留此注记免误读。

## 5. 候选安装物 `ops/hooks-candidate/`(安装属操作者席)

`session_start.sh`(恢复入口四步+只读跑一致性门播报 PASS/FAIL,FAIL=「禁止直接开发,先对账」)/`pre_compact.sh`(检查点提醒+`--verify` 尾三行)/`settings.fragment.json`(待合并 hooks 片段)/`README.md`(真相表+安装四步+诚实边界)。两钩子本席活测 rc=0、播报真出(stderr 亲见)。**未安装**——修改运行环境配置超出本波权限面。

## 6. 测试

- 新套件 `tests/test_rd_r21_deadloop.py`: **18/18 绿**(分类单元 5+合成仓库漂移/返工 4+降级与退出码 5+finalize 事故弧 4)。
- **全量离线套件(CI 同法循环,本席 worktree 内实跑)**: 134 套件跑毕,**131 绿 / 3 红,三红全部环境性、零代码回归**:
  1. `test_p0_baseline_lock_equivalence` R-还原断言 `git worktree list`==1 行——本席 fork worktree 自身即第二行。**干净单 worktree 克隆复跑 31/31 全绿**(CI 环境=干净克隆,等效绿)。
  2. `test_rd_r20_state_checkpoint` E1/E2 + 3. `test_rd_r20_state_consistency` C1 真仓 ratchet——波中态(分支代码提交超前 R20 基线 dfad40e、未 finalize)①基线合法红,套件头文档明示「未 finalize 前如实红=狗粮负例」;finalize 后复验见下。
- 收口序列机证(见 ITERATION_LOG R21 行): finalize(分支最后一笔)后重跑门=6/6、两 R20 套件真仓 ratchet 转绿。
- 顾问真仓实跑 `rc=0`;候选钩子活测 `rc=0`×2;STOP/锁负路径活测 `rc=0`×2(环境复原)。

## 7. 异常与移交

1. 第 2 项 PARTIAL: 无头压缩恢复无实例——留待未来轮真实事件;钩子包安装后 SessionStart 播报可前移发现。
2. LIVE daily/weekly 昨今 exit 1/2=已知 ZQ 族采集缺口(观察钟 11-14),明日首跑 v0.15.0 面,移交操作者观察。
3. 候选钩子包待操作者席安装(README 四步)。
4. Mac 睡眠致 4h 名义间隔实际 4.5-6h——环境特性如实登记,非整改项(可选 caffeinate 属生产环境改动,须用户授权)。

### 附注(2026-11-12 操作者合并后): 实际兑现的返工预警与根因

合并+热修后主面实跑顾问,兑现的是 `offline-tests.yml` 的 R21→R21 返工预警
(非 §4 预测的 rd_checkpoint.py): 根因=同一次 CI 三连红事故波内,fork 的
顾问步(R21)与操作者 fetch-depth 热修(d8c420d,重盖章后区间仍标 R21)两次
触及同一文件的不同 hunk——非「重复修复同一问题」,属一次根因的两个修复面。
预警机制本身按设计工作(非阻塞可见性);阶段三起若再现同文件连轮改,按 §4.3
根因复审流程处理。
