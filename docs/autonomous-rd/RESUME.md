# RESUME — 新会话恢复指令

> 新会话仅凭仓库文件即可恢复工作,不依赖任何历史聊天记录。开场即按本档执行。

## 恢复步骤

1. 读根目录 `CLAUDE.md`(红线与启动纪律)。
2. 读 `PRODUCT_GOAL.md`(最高目标)。**若该文件不存在 = 总指令未落位**: 向用户索取原文,
   不得自行代拟;其余恢复步骤照常。
3. 读 `CURRENT_STATE.md`(快照)→ `OPEN_ISSUES.md`(卡点)→ `CAPABILITY_MATRIX.md`(差距)
   → `ITERATION_LOG.md` 末行(最近一轮)。
4. 引擎运转面如需(周报/采集/轮次): 另查 `~/agent-loop/STATE.md` 顶部速览与
   `~/agent-loop/HANDOVER-NEW-SESSION.md`。
5. 从「下一步」取首个可执行任务,进研发循环:
   **审计 → 定优先级 → 开发 → 测试 → 独立验证 → 更新状态 → 下一轮**。
6. 在 `dev/*` 分支工作;未经授权不合 main、不推送、不付费、不碰生产。
   结束前完成阶段检查点(纪律见 `CLAUDE.md`)。

## 下一步(2026-11-12 R12 AC9 干净环境全链覆盘轮收口后更新)

1. **[已毕·R9] 采集缺口波**: CN_SF_FLOW mofcom 直取(merge=bd8b853,v0.12.0-alpha,
   Release 442060959);BUND 双年限=四路证据源端封锁维持诚实缺席;JP_CPI_TOKYO=
   e-stat 需免费 appId 新凭证留用户裁定;CN_OMO_7D source-blocked 不动。
2. **[已毕·R10] tushare 月度缓存硬化**: 操作者已合并发布(a2afe5d,v0.13.0-alpha,
   Release 442290356);边界如实: 冷启动同瞬双拉仍可撞限流(收窄非消除,P2 台账)。
3. **[已毕·R11] noncore_missing 子源级注记细化**: 操作者已合并(12c3c0f 面)。
4. **[已毕·R12] AC9 干净环境全链覆盘**(dev/rd-r12-ac9-clean@9de4cc8+docs):
   ①安装器 --force 坑修复(matches_source_history 旧版面幂等刷新,16/0+32/0)
   ②干净环境七步链全真通(安装→配置→更新 15/15 v2 同日修订→研究两问→地图→
   追溯 3/3 sha256→归档 QB-20261112-001);首轮 Gate A 拒=港股双通道环境面
   (LIVE 同日同败铁证),补 HTTPS_PROXY 恢复设计姿态后闭环;**波次毕,待操作者
   合并**。
5. **[下轮=R13 候选·按序]**: ①USER_GUIDE 补代理说明(R12 用户文档面发现:
   macOS 系统代理不自动进 shell env,境外源(yfinance)在 shell/launchd 启动
   管线时须 HTTPS_PROXY=http://127.0.0.1:7890;R12 首轮 Gate A 拒即此因)
   ②japan 通道 source_key 补接(R11 审计 MINOR: 需先核实 japan_rate_collector
   是否持久化子源级 sources_status,再决定接线或改兜底措辞;含 jp 档
   FRED_POLICY/MOF_JGBCME 键与 BOJ_POLICY_RATE/JGB_* 的映射核对)③HK 双通道
   脆弱面观察(腾讯 WAF 深窗拦[2026-11-12 实测 2600 拦/320 通,与 11-10 记录
   的 >320 拦不同——阈值浮动,以当日实测为准;HK_INDEX_HISTORY_BARS env 缝=
   2000 根保底]+yfinance 依赖代理姿态)④china/macro 采集器子源失败落盘(现只
   print 不落盘,CN_OMO_7D 等 china 缺席只能兜底不可区分;落盘后可接线
   source_key 精确分类)⑤R2/R1 审计 MINOR 存量(OPEN_ISSUES 技术待办按需取用)。
6. **[待用户/操作者·无头权限面外]**: ①R12 波次合并 main+发布(验收绿即合并
   纪律,操作者会话执行)②v0.13.x LIVE 同步(R10 轮遗留,部署脚本已备
   /tmp/deploy_v013_live.py,分类器静态规则拦,待用户终端亲跑或加 Bash 白名单)
   ③AC7/AC9 终判覆盘轮(两行均 EXECUTED 已定,终判待用户裁定)。
7. **[日历门] 2026-12-05 F 补证轮由引擎自动触发,勿手工提前;六标签首验窗
   2026-12(注意: R5 后 7 假设有判=A/B 阶段面;C 层到期判定不受影响)**;
   金油比开放题观察钟 2026-12 同窗。

## 下一步存档(2026-11-12 R8 验证+合并后版)

1. [已毕·R7+R8] AC7 首跑+独立验证+合并: R8 七面零 BLOCKER(数值单项 FAIL
   ZQ−DFF 0.295→0.305 已出更正评注 C1,结论不变);merge=825eb4f+R8 记账
   033a869(docs-only 不另发 tag);R8 全文=R8_AC7_VERIFICATION.md。
2. [已毕·R9] 采集缺口波(见上第 1 条)。

## 下一步存档(2026-11-11 四卡点批准后版)

1. [已毕] R1-R4 全链 + 用户「全部审批通过」四卡点执行:
   ①合并毕(main=be8dabd,v0.10.0-alpha);③LIVE 部署毕(v0.10.0 面);
   ②原则获批无即需项;④无头自主运行=后被用户放行落地(R5 首轮)。
2. [已毕] R5 候选③诊断(ZQ_IMPLIED_AVG 采集恢复,周六 11-14 weekly 应自动
   恢复,零代码改动)。
3. [已毕·R5] 候选①数据覆盖盘点→升级为四类缺陷分解+引擎修复(见上)。

## 快照纪律

- 上下文过半: 更新 `CURRENT_STATE.md` + 本档「下一步」→ 继续工作。
- 上下文将尽/会话将终: 立即停止开新任务,先完成完整检查点
  (实际进度/测试与审计结果/能力差距修订/分支与 Commit/下一步),再收尾。
