# r29-evidence — Audit-R29 验收证据包

隔离验收树(真实会话+真实采集+实包重放;LIVE 数据树只读复制,
零 LIVE 写入)。树基线: wave-0=`2412968`/`37b8713`,wave-1=`b7f9ccf`。

## questions/ — 四问原文(question_A/B/open + 未参与调试新问 NEW)

## wave0_2412968/ — wave-0 三席日志(A 异步席位剥离/B 绑定手工化实雷/C 草稿)

## session_A2_formal/ — 原问·健康树(37b8713)
- 全链: REVISE→修订→UPHELD(两裁 frozen 自动绑定 a09e4119…)
- arc_A2 归档件(manifest/裁决链/读者报告/工单)+ deliverable=true

## session_B2_formal/ — 换问·健康树(37b8713,绑定机械化首证)

## session_C2_degraded_defect/ — C2 实雷实录(37b8713)
- 缺 EA 核心组的地图被旧判定放行归档(arc_C2/arc_C2b manifest)
- DEFECT_NOTE.md: 根因/修复(b7f9ccf §E)/同报告直调复核

## session_C3_degraded_fixed/ — 残缺树·终 SHA(b7f9ccf)
- 草稿交付 + 操作侧归档拒绝(map_core_dimension_missing)实录

## session_OPEN2_formal/, session_NEW2_formal/ — 开放问原文/新问(终 SHA)

## replay_A2_real/, replay_B2_real/ — 实包六步重放回执(matched engine)
- 严格面 byte_equal/换本地日历逐字节不变/重复重放原包不动/
  缺件拒/篡改一字节拒/manifest 单侧改写拒
- 版本门旁证: 异版引擎重放=code_version_mismatch 拒(回执内注记)
