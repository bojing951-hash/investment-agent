# IA-P03-W2-GLM-WP-G4 凭证使用登记件(CREDENTIAL REGISTRY)

> **登记制凭证使用登记件**(合同 IA-P03-W2-GLM-WP-G4-AC-v1.0 §零白名单必含件)。
> 头部=合同 §七.7 冻结模板(逐字段,一字不增删);**熔断阈值 CB-1~CB-4 与本模板均为
> 合同冻结值,执行段禁回改**。REGISTRY 只记标识符/别名/环境变量名——**凭证明文/密钥值
> 禁入本文件**(合同 §零凭证纪律)。
>
> 实批依据: 用户 2026-11-05 实批(原文「前三个全部审批」覆盖本包),批复行=
> PENDING-APPROVALS.md 2026-11-05 09:3x 节,批准对象=合同 §七.5/§七.7 已冻结参数包
> (CB-1~CB-4/日上限 USD 5.00/登记模板),非空白授权(合同冻结章②)。
> 凭证注入=驱动进程环境变量(单一来源),仅存在性检查,值零打印零落盘。
> tests 与 CI 的合成桩调用**不入本表**(非真实出站,合同 §七.6)。

## 一、凭证使用登记模板(合同 §七.7 冻结,头部逐字段)

| 字段 | 填写规则 |
|---|---|
| 登记编号 | `G4-CRED-<三位序号>` 顺序编号 |
| 时间(UTC) | 该面调用起时刻 |
| 调用面 | 模块/脚本: 函数(file:line) |
| 模型/端点标识 | 实批覆盖的端点/模型标识符 |
| 用途 | 对应 DESIGN §七 WP-G4 验收要点编号 |
| 凭证标识 | **仅别名/环境变量名,禁明文禁值** |
| 出站次数 | 本条次数 / 执行段累计 |
| 费用估算(USD) | 本条 / 累计 |
| 熔断器状态 | 未触发 或 TRIPPED-<条件编号> |
| 审批依据 | 实批留痕指针(PENDING-APPROVALS.md 批复行/引擎登记路径) |

## 二、登记表(逐面先登记后调用;运行后回填计数/费用/熔断状态,禁事后改前六列)

| 登记编号 | 时间(UTC) | 调用面 | 模型/端点标识 | 用途 | 凭证标识 | 出站次数 | 费用估算(USD) | 熔断器状态 | 审批依据 |
|---|---|---|---|---|---|---|---|---|---|
| G4-CRED-001 | 2026-11-05T01:59:17Z | scripts/glm_conclusion_client.py: run_smoke(L673)→run_live_conclusion(L565)→call_glm_once(L468,真实出站点L497) | glm-5.3 @ https://open.bigmodel.cn/api/paas/v4 | 要点①(真实调用冒烟: 结构化输出过校验器+数值接地核对;兼证要点③调用日志与用量记录落盘) | GLM_API_KEY(环境变量,值不落盘) | 3 / 3 | $0.0667 / $0.0667 | 未触发 | PENDING-APPROVALS.md 2026-11-05 批复行(合同冻结章②) |
| G4-CRED-002 | 2026-11-05T02:45:52Z | scripts/glm_conclusion_client.py: run_smoke(L673)→run_live_conclusion(L565)→call_glm_once(L468,真实出站点L497) | glm-5.3 @ https://open.bigmodel.cn/api/paas/v4 | 要点①补证据轮(合同 §九情形(c): 仅补真实重跑一次,冻结参数原样 temperature=0.2/reasoning_effort=low;操作者 2026-11-05 10:5x 追加指令;兼证要点③日志追加) | GLM_API_KEY(环境变量,值不落盘) | 0 / 3 | $0.0000 / $0.0667 | 未触发(零出站) | PENDING-APPROVALS.md 2026-11-05 批复行(合同冻结章②)+操作者补证据轮追加指令(2026-11-05 10:5x) |
| G4-CRED-003 | 2026-11-05T03:24:43Z | scripts/glm_conclusion_client.py: run_smoke(L673)→run_live_conclusion(L565)→call_glm_once(L468,真实出站点L497) | glm-5.3 @ https://open.bigmodel.cn/api/paas/v4 | 要点①补证据轮第4次尝试·操作者代执行(二复审处方2026-11-05 11:1x HKT「操作者择时重发第4次尝试或代执行,同CI dispatch先例」+处置§五;冻结参数原样 temperature=0.2/reasoning_effort=low;恰1次=RETRY_BUDGET 运行时置1[进程内],模块文件零改动) | GLM_API_KEY(环境变量,值不落盘) | 1 / 4 | $0.0220 / $0.0887 | 未触发 | PENDING-APPROVALS.md 2026-11-05 批复行(合同冻结章②)+二复审处方代执行(2026-11-05 11:24 HKT) |

## 三、登记说明

1. **实批覆盖调用面**(REPORT §0.5): F1=模式 A 真实调用冒烟(唯一实批面;DESIGN §三
   调用面B[模式B]经 L219 排除,不在本包实批覆盖内,零出站)。
2. 每次重试=同面新登记一次尝试(全部如实记录,禁重试凑结果;合同 §三 AC-02.4)。
3. 用量/调用日志: `data/research/glm4_usage_log_20261104.jsonl`(JSONL,逐次出站一条,
   字段含 ts_utc/face/attempt/ok/kind/model/endpoint_host/elapsed_s/usage/
   cost_est_usd/breaker_before_tripped/breaker_after/error_note;error 侧已脱敏,
   全记录零凭证明文);证据包收**脱敏后全文副本**。
4. CB 口径: CB-1 连续≥5 失败→TRIPPED(复位仅显式人工);CB-2 单执行段≤60 出站软停;
   CB-3 日估算费用≤USD 5.00;CB-4 单次>120s 计失败并入 CB-1(合同 §七.5 冻结值,
   实现常量 REPORT §二登记,tests 硬编码字面量复核)。

## 四、G4-CRED-001 执行段结果(如实,2026-11-05 UTC)

- 3 次真实出站全部传输层成功(ok/kind=ok: 流式返回+usage 捕获),单次 26.9s/26.1s/19.7s
  (均 < CB-4=120s);prompt_tokens 1949/2080/2063,completion_tokens 1810/1932/1636;
  费用估算 $0.0221+$0.0236+$0.0209=$0.0667(< CB-3 日上限)。
- **G2 管线终裁: ABSENT_REGISTERED**(径3 如实缺席): 三次尝试模型输出均未过
  gov.validate_output——尝试1 schema外字段(value_note 等);尝试2 limitations义务
  (Gate A 降级承接/替代解释指针)+接地失败(4000.0);尝试3 statement/limitations
  接地失败(25.0/1.0/60.0/0.3 不在证据包)。径1 反馈回注两轮生效(失败面逐步收敛:
  schema→义务→仅剩数值接地)但预算(gov.MAX_RETRIES=3)内未达 ACCEPTED。
- 结论: 接线链路(门控→六槽位 prompt→真实流式调用→熔断记账→G2 权威裁决→反馈回注
  →G3 结论记录→append-only 落档→用量日志)端到端工作正常;**模型遵从性(数值接地)
  在冻结参数(temperature=0.2/reasoning_effort=low)下 3 次尝试未过校验器**=如实结果
  (合同 §三 AC-02.4 合法如实),要点①按情形(c)登记「部分: 链路过/模型输出未过校验器」,
  禁重试凑结果;参数调整需另拟登记(运行后禁回改)。
- 熔断器: 未触发(consecutive_failures=0;3/60 出站;$0.0667/$5.00)。
- 产物: data/research/glm4_live_smoke_20261105T015850Z.json(报告)+
  glm_conclusions_archive.json(G3 结论记录,absence 版)+
  glm4_usage_log_20261104.jsonl(用量日志,零凭证明文)——均不 commit。

## 五、G4-CRED-002 执行段结果(补证据轮,2026-11-05 UTC;如实: 阻断零出站)

- **结果: 未执行成功——执行环境权限阻断,零真实出站**(2026-11-05T02:45:52Z~
  02:48:27Z 之间 4 次发起,均被本会话工具权限层拒绝于命令执行前,错误统一为
  「This command requires approval」,含一次显式非沙箱批准形式;无批准通道应答)。
- 冻结参数原样零改动(temperature=0.2/reasoning_effort=low/glm-5.3/16k/125s;
  代码与测试文件零改动,模块 sha256 不变);GLM_API_KEY 在场(存在性核验
  2026-11-05T02:44Z,len=49,值零打印)。
- 零出站独立佐证: 双面锚定 34/34 文件哈希不变(零新增零变更,post-run 复核
  2026-11-05T02:48:27Z);usage log 仍 3 行(零新记录);无新 smoke 报告文件;
  第 4 次命令从未到达执行层(real-run/live_smoke_F1_attempt2_blocked.txt=阻断
  记录工件,入证据包⑥)。
- 处置: 按操作者追加指令「恰 1 次,无论结果如何不追加」——阻断后停止发起,
  不重试凑结果;上轮(2026-11-05T01:59Z)同调用面 G4-CRED-001 真实出站成功,
  判定为本轮会话执行环境权限配置变更所致(非凭证/网络/实批问题)。处置权在
  操作者(择时重发/代执行;CI dispatch 先例=opd 代执行同)。
- 熔断器: 未触发(零出站零计数;跨执行段历史累计 3 次/$0.0667 不变)。

## 六、G4-CRED-003 执行段结果(补证据轮第 4 次尝试·操作者代执行,2026-11-05 UTC;如实)

- **先登记后发起**: 前六列登记于 git 提交 cf7c75c(登记时戳 2026-11-05T03:24:43Z),真实出站时戳 2026-11-05T03:26:33Z(usage log 第 4 行),次序机器可证(commit 时戳<出站时戳)。
- **结果: 1 次真实出站传输层成功,模型输出仍未过 G2 校验器,终裁 ABSENT_REGISTERED(如实)**。单次 34.3s(< CB-4=120s);费用 $0.0220;失败面=hypotheses[0].limitations 未承接 Gate A 降级影响面(径2义务)+hypotheses[1].statement 接地失败([0.3,25.0] 不在证据包)+hypotheses[1].limitations 未承接(径2义务)——与 G4-CRED-001 尝试 3 残余面(数值接地)同域,模型遵从性在冻结参数(temperature=0.2/reasoning_effort=low)下第 4 次仍未达。
- **恰 1 次实现**: RETRY_BUDGET 运行时进程内置 1(gcc.RETRY_BUDGET=1,处置§五「恰 1 次」;模块文件零改动,冻结 retry_budget=3 文件值原样;模型面参数 temperature/reasoning_effort/模型/16k/125s 分文未动)。
- 出站面: 操作者会话(二复审处方 2026-11-05 11:1x HKT「操作者择时重发第 4 次尝试或代执行,同 CI dispatch 先例」);凭证=LIVE env_config 三元组进程注入(RUN_GLM_LIVE=1),值零落盘零打印(存在性核验 len=49)。
- 预算纪律: 累计出站 3→4(CB-2 上限 60 远未及);累计费用 $0.0667→$0.0887(CB-3 日上限 $5.00 远未及);熔断未触发(本段 1 出站/0 连败)。
- 产物: data/research/glm4_live_smoke_20261105T032559Z.json(终态报告,registry_row 内嵌)+glm4_usage_log_20261104.jsonl 第 4 行+glm_conclusions_archive.json 追加结论记录——均不 commit。
- 处置: 处置§五预置分支生效——第 4 次 ACCEPTED→要点①PASS;再失败(本段=ABSENT_REGISTERED)→§二兜底终态(接受 (c) 如实缺席定稿,处置留痕于 rounds/029/OPERATOR-DISPOSITION-R029.md)。
