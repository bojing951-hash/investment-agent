# Audit-R31 重下实包离线重放回执 — 2026-11-23 02:51(推送后)

- 推送: `61f3130`(证据+报告)→ fetch origin 核对 **local==remote** ✓
- [D0] git archive 远端 HEAD 干净树重下两交付包(session_A4_formal/
  session_B2_formal);manifest code_version=ca916cdca7b749282e498d8c8f0eac8bf43b7372,
  frozen 三件在场
- [D1] 引擎=远端 HEAD(文档尖)重放 → **rc=1 blocked=code_version_mismatch**
  (版本门证据: 包绑定产出它的代码版本,文档尖引擎拒放行)——两包一致
- [D2] 引擎=git archive(manifest 版本 ca916cd)+CODE_VERSION 印章,
  六步离线重放(下载方视角,与本地验收树完全独立):
  - [0]严格面 rc=0 byte_equal+frozen 三查全绿+终裁三方绑定 ✓
  - [1]换本地日历逐字节不变 ✓ [2]重复重放包不动 ✓
  - [3]缺冻结件拒/[4]篡改一字节拒/[5]manifest 单侧改写拒(rc=1,
    failed_checks 正确)✓
  - A4dl/B2dl 双包全绿(原始输出 /tmp 接受区 dl_A4.log/dl_B2.log)
