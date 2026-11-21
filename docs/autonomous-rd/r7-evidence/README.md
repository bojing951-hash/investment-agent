# Audit-R7 真实运行与可复放证据包(R7-03)

目的: 两轮真实网络采集及刷新的命令/日志/状态/查询结果/哈希**交付入仓**
(此前只在 /tmp);新 B 原始宏观输入及 provenance 补全;复算脚本净检出
可直接重放;执行源码版本绑定可核对。不含任何密钥/令牌/敏感环境信息
(FRED key=既有 LIVE 只读授权,进程内环境变量注入,零落盘零日志)。

## 一、清单与哈希

| 件 | sha256(前16) | 证明 |
| --- | --- | --- |
| `realnet/round1.log` | 见文件尾注 | 第一轮真实采集(US FRED 22 项+CN 226 月×2,fresh 10:58:29Z) |
| `realnet/round2.log` | 同上 | 第二轮连续采集+美国刷新(fresh 11:00:04Z,CN 不被遮蔽) |
| `realnet/query_round1.txt` | — | 第一轮后 ia_cli history 信封(collection_status 三分+零警告;宏档 sha 37edb169…,已被同日第二轮覆写——同日重跑语义,数值面不变) |
| `realnet/query_round2.txt` | — | 第二轮后信封(CN 两指标 fresh,宏档 sha 1276673a…) |
| `realnet/stamp_and_binding.txt` | — | 引擎树 CODE_VERSION 印章+git_state 三级绑定实测 |
| `../cn-task-b-20261117T083954Z/macro_input/macro_20261117.json` | `be1f7680ce7a650e` | 新 B 原始宏观输入(与 B 包 README 哈希表一致,provenance 完整) |

完整 64 位 sha256 以 `shasum -a 256` 现场重算为准(上表前 16 位对勘)。

## 二、真实两轮(脱敏命令)

```sh
# 引擎树=/tmp/audit_r7/engine(本仓工作树快照+CODE_VERSION.json 印章)
# FRED_API_KEY 经既有 LIVE 只读授权进程内注入(不写入任何文件/日志)
cd /tmp/audit_r7/engine && FRED_API_KEY=<redacted> \
  python3 scripts/macro_collector.py | tee round1.log   # 第一轮
FRED_API_KEY=<redacted> python3 scripts/macro_collector.py \
  | tee round2.log                                        # 第二轮(连续+美国刷新)
python3 ia_cli.py history --metric CN_PMI_MFG            # 信封采集状态
```

结果: 两轮 run_ok(US 22 项全绿+CN 两指标 fresh n=226,
2008-01..2026-10);第二轮 last_success_at 由 10:58:29Z 前移 11:00:04Z
(连续采集成功非续存);美国刷新不清除 CN(R6-02 语义在 R7-02 状态面
复证);信封 `collection_status.mode=fresh`+`last_observation_period=
2026-10-01`+零警告——R7-02 贯通链(采集→档→loader→工作台→信封)真网验证。

## 三、版本绑定(引擎树=代码副本不再 null)

- 印章 `/tmp/audit_r7/engine/CODE_VERSION.json`: `git_head=
  4e2f94cfaa097aad333aebcbf3ed5b1adbd2f56b`(R7 审计基线)+
  `git_diff_sha256=70b83f575cb7…`(工作树未提交差异+未跟踪件指纹,
  R7 修复在飞面)+源树路径+时戳。
- `_git_state` 三级链实测: 仓内运行→`run_root`;engine-root 注入运行
  →`code_tree`;引擎侧自跑→`code_version_stamp`;全不可得→(None,
  None,None) 如实。
- 新 B(run.git_head=null)根因与补全见其归档
  `AUDIT_R7_ANNOTATION.md`。

## 四、干净检出重放(B 复算)

```sh
cd <repo> && python3 docs/autonomous-rd/cn-task-b-20261117T083954Z/\
review_seat/recompute_r6b.py ; echo rc=$?
# rc=0,105/105 OK;产物 review_seat/recompute_replay_out.txt 与冻结档
# 核心段(162 行)逐行一致(--seat/--out 可覆写;失败=非零退出)
```

研究席重放(一条命令)见 B 包 README;输入哈希表含 macro_input。

## 五、四态区分

- **已实现**: R7-01/R7-02/R7-03 全部代码与测试(见 AUDIT_R7_REPORT)。
- **离线验证通过**: 三反例回归+正例+九场景(37/0)+全电池。
- **真实在线验证通过**: 本包两轮采集/刷新/查询(§二)+R6 真网四步
  (AUDIT_R6_REPORT §三)。
- **尚未验证(NOT_VERIFIED 面)**: 无本轮新增;历史遗留面=旧 B 契约门
  基线重跑 CONTRADICTED(归档注记处置,新链替代)+HY_OAS 族源端授权窗
  (Charter6 注记)。
