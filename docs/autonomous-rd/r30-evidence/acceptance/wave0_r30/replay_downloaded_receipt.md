# Audit-R30 重下实包离线重放回执(任务4 新增项)

执行: 2026-11-22 02:23–02:26(本地),脚本 /tmp/r30x/replay_downloaded_r30.sh

## [D0] 远端核对与重下
- fetch origin dev/audit-fix-r1 → remote HEAD=`ebe2061413c5ed2da47377674e0610b167f2eaf9`
  = local HEAD ✓
- `git archive ebe2061` 干净树提取交付包:
  - `docs/autonomous-rd/r30-evidence/acceptance/session_A3_formal`
  - `docs/autonomous-rd/r30-evidence/acceptance/session_B3_formal`
- manifest 版本核对: 两包 code_version 均=`59dcc096fff5138429105214bbd24ccd3ce003bb`
  (产出代码=候选 SHA),frozen_inputs 三件。

## [D1] 引擎=远端 HEAD 重放 → 版本门拒(证据)
- rc=1,blocked=`code_version_mismatch`(payload 存档 dl_mismatch_refusal_payload.json)
- 判读: 交付包绑定产出它的代码版本;文档尖(ebe2061)引擎重放被拒——
  版本门真实咬合,非旗标装饰。

## [D2] 引擎=git archive(manifest 版本 59dcc09)+部署态印章 六步离线重放
- 印章: CODE_VERSION.json git_head=59dcc09(build_tree 同一写法;裸 archive 无印章
  → 版本不可核验必拒——部署态印章=部署件,非仓内容,与 LIVE 部署口径一致)
- **A3 包**: [0]严格面 rc=0 byte_equal+frozen 四查全绿(present/digests/
  match_report/verdict_binding_threeway)/[1]换本地日历逐字节 IDENTICAL/
  [2]重复重放包 UNTOUCHED+IDENTICAL/[3]缺冻结件 rc=1 拒/[4]篡改一字节 rc=1 拒/
  [5]manifest 单侧改写 rc=1 拒
- **B3 包**: 六步同样全绿(三通过 rc=0/IDENTICAL/UNTOUCHED+三拒绝 rc=1)

## 结论
- 重下→按清单版本→干净目录离线重放链路成立: 逐包退出码 0、byte_equal、
  源摘要匹配终裁(frozen_inputs_match_report+verdict_binding_threeway)全绿;
  版本门/缺件/篡改/改写四面拒收。
- 与本地 arc_ 目录重放(/tmp/r30-accept/install 引擎)互为独立复核。
