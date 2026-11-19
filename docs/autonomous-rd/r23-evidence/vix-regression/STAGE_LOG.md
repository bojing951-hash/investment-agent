# Audit-R23 独立 VIX 工单复测(R22 判断档重贴,新代码面 b316e88)

隔离树 /tmp/r23v = git archive b316e88 + 20261118 通道面
(china/ea/global/japan/jp/macro/shiller_20261119→20261118 族+rate_economy_20261118
+ea/japan/jp_20261105+hk_index_history;与 R22 /tmp/r22v 同通道集)。
CODE_VERSION.json 印章 git_head=b316e88b2b4a98e95ab23aeac71a304485e78b0f。

## 链(全部经 ia_cli.py research-one,--engine-root /tmp/r23v)

1. snapshot_builder --date 20261118: Gate A=DEGRADED(事实104,71 PASS/12
   DEGRADED/0 FAIL,core 缺失0,非核心缺失8: BUND_10Y/BUND_2Y/CN_OMO_7D/
   CN_POLICY_OVERNIGHT/EA_REAL_GDP_YOY 等——与 R22 面一致)
2. plan(工单原文同 R22): run_ok=True,run 20261119T173250Z,
   report.run.git_head=b316e88…(git_head_source=code_version_stamp)
3. attach(R22 终档 agent_judgment.json 重贴): **attached=True**
   ——非地图问句,R23 新契约面(quarter_token/bp/as_of_leak 均在
   _map_checks 门内)正确不触发,旧档零漂移
4. report: deliverable=False(审查门待裁)→ FULL_REPORT 正文 VIX 月窗
   **+38.07%(+7.02),2026-10-19 18.44→2026-11-17 25.46 于新代码面逐位复现**
   (grep 计 38.07%×4/+7.02/18.44/25.46 全在场)
5. 独立零上下文审查席(独立子代理,只读,52 复算点): **UPHELD(Round-1)**
   ——VIX 月窗界日(周日 10-18→最近邻 10-19)/HY_OAS +0.05pp/SPX −4.55%/
   日度相关 0.5493(n=751)/analog 5 行/validate violations=0/report.md
   逐字节=render;0 MAJOR+3 MINOR(warnings 指针落空/两端点口径未注记
   窗内区间/SCN 证伪阈值中性带)+2 NIT;PROSE-round1.md+VERDICT-round1.json
   在 run 目录 verdicts/
6. record_semantic_verdict(reviewer=independent-zero-context-seat-round1)
   → rev=1;report 复跑 **deliverable=True**(verdict=UPHELD/fresh=True)
7. archive(缺省目标): exit=0,content_sha256=a3db4776c5928b87…,
   manifest verdict=UPHELD=裁决档 overall,三方摘要一致;
   非地图问句 map_report_sha256=None(绑定仅地图问句,如实)

## 交付物

final/=归档九件套(AGENT_SEAT_ENVELOPE/ARCHIVE_MANIFEST/FULL_REPORT/
agent_judgment/evidence_index/report.json+md/verdicts(含 Round-1 两件+
登记档)/views_digest)。
