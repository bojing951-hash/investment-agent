#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P3-WP-F: P3 终验 + 项目总封版(P3 收尾层第 6 实现包/族末包;#38 挂靠)

DESIGN docs/P3_DESIGN.md §7 WP-P3-F 行(L200-L208,基线工作树实读)确定性落地:
终验清单执行(七 AC 复演式终验/层序关闭核对/各层交付件归档索引)+ 总封版判定
材料汇编 + 横切运行时验收登记(L202「不预执行」——①②两项零执行面,登记 only)。

四组件:
- 登记面: 终验清单 24 项六段(S1 七 AC 复演 7/S2 层序关闭 11/S3 归档索引 1/
  S4 横切运行时登记 3/S5 清单纪律 1/S6 总封版判定 1)+计时基线(DP-10 定值
  (a)+(i): 起算=LIVE 部署日 2026-11-05,载体=R018 停泊件[注入摘要级对接],
  观察窗 30 天→终点 2026-12-05,补证轮=2026-12-05 后收口——确认面=用户
  2026-11-08 实批「现在就发 F」[冻结章 §十一 凭证,注入摘要非工作树实读],
  非执行Agent自决);
- 状态机: JSONL append-only 状态日志(baseline→started→compiled 单发链)+
  禁回改 digest 链(清单/计时常量 canonical sha256 逐级复核等值;L208④
  「终验开始后回改清单被拒」=propose_checklist_amendment 恒拒面+digest 失配
  fail-loud;§8.5 L220「终验清单只追加」红线);
- 执行面: 归档索引在场核验+sha256 指纹(154 件登记索引,F 自身 4 件自豁免)+
  层序关闭核对(关闭事实=冻结章 §十一 登记[注入摘要],在场核验=离线实检)+
  七 AC 复演汇编(verdict=REPORT §四 登记值输入,执行席自评,独立审计待
  R043——非模块自算,零自证);
- 判定面: 总封版判定规则(任一 FAIL→NOT_SEALED;否则任一 NOT_VERIFIED→
  PENDING_SUPPLEMENTARY_EVIDENCE;否则 SEALED)如实汇编,FAIL 项逐字留档
  不美化(L208⑤)。

纪律: 零网络零 GLM 零凭证零付费零 subprocess 零 datetime(import 白名单
{json,os,sys,hashlib};日历=纯字符串+月长表+闰年规则);零预执行(运行时
验收①②=登记面 only,证据汇编属 R018 载体/补证轮面);路径守卫=LIVE 根四
组件序列拒+data/daily 相邻组件拒(全部读写面);本模块输出为项目工程收尾
状态如实汇编,**不构成投资建议**(§8.3 L218 红线: 禁交易/禁仓位/禁收益
承诺)。
参数登记: docs/P3_WP_F_REPORT.md §零.4/§零.5(DP-10+P-F-01..P-F-21,
先登记后实现,运行后禁回改)。
"""
import json
import os
import sys
import hashlib

# ══ 登记型参数定值(REPORT §零.4/§零.5;登记定值即实现值,运行后禁回改) ═══

FA_SCHEMA_VERSION = 1                  # P-F-03 清单 schema
SEAL_DOC_SCHEMA_VERSION = 1            # P-F-14 判定材料 schema
JOURNAL_SCHEMA_VERSION = 1             # P-F-07 状态日志 schema

# P-F-02 DP-10 定值承载(DESIGN L239;确认面=用户实批[冻结章 §十一,注入摘要])
DP10_CLASSIFICATION = "LIVE类·确认权留用户+登记型(DESIGN L239)"
DP10_USER_APPROVAL = "user_approved_2026-11-08_now_dispatch_F"
DP10_OBSERVATION_START = "2026-11-05"  # 选项 (a)=LIVE 部署日
DP10_OBSERVATION_WINDOW_DAYS = 30      # DESIGN L206 逐字
DP10_OBSERVATION_END = "2026-12-05"    # =起算+30 天纯日历推导
DP10_CARRIER = "R018_parked_artifact"  # 选项 (i)
DP10_CARRIER_INTERFACE_LEVEL = "注入摘要级对接"
DP10_ZERO_PREEXECUTION = True

# P-F-04 补证轮登记(用户知悉采纳,冻结章 §十一,注入摘要)
SUPPLEMENTARY_ROUND_AFTER = "2026-12-05"

# P-F-05 运行时验收阈值(DESIGN L205-206 逐字数值;零执行面)
RT_MIN_SCHEDULED_EXECUTION_DAYS = 7    # ① ≥7 个真实计划执行日
RT_MIN_WEEKLY_REGRESSIONS = 1          # ① ≥1 次真实周报回归
RT_MIN_OBSERVATION_DAYS = 30           # ② 30 天生产观察
RT_MIN_TASK_SUCCESS_RATE_PCT = 95      # ② 计划任务成功率≥95%
RT_MIN_FORMAL_WEEKLY_REPORTS = 4       # ② ≥4 次正式周报

# P-F-03 verdict 值域与七 AC 复演输入契约(P-F-12)
ALLOWED_VERDICTS = ("PASS", "FAIL", "NOT_VERIFIED")
SEVEN_AC_IDS = ("AC-01", "AC-02", "AC-03", "AC-04", "AC-05", "AC-06", "AC-07")
_SELFCHECK_ROW_FIELDS = ("evidence", "note", "verdict")

# P-F-07 状态日志记录类型封闭集
JOURNAL_RECORD_TYPES = ("baseline", "started", "compiled")

# P-F-10 F 自身交付件自豁免(自指环豁免,沿 R019-D3 先例精神)
SELF_EXCLUDED_PATHS = (
    "scripts/project_final_seal.py",
    "tests/test_p3_wp_f.py",
    "docs/P3_WP_F_REPORT.md",
    "docs/P3_WP_F_DELIVERY.md",
)

# P-F-13 判定规则与释义
DETERMINATION_RULE_TEXT = (
    "任一 FAIL→NOT_SEALED;否则任一 NOT_VERIFIED→PENDING_SUPPLEMENTARY_"
    "EVIDENCE;否则→SEALED(登记规则 P-F-13,REPORT §零.5)")
DETERMINATION_LABELS = {
    "NOT_SEALED": "不封版(存在 FAIL 项,如实留档,不美化)",
    "PENDING_SUPPLEMENTARY_EVIDENCE": (
        "待补证(观察钟/独立审计/CI 登记面未闭合;2026-12-05 观察钟满后"
        "补证轮收口[用户知悉采纳,冻结章 §十一,注入摘要])"),
    "SEALED": "封版",
}

# P-F-14 免责词面(§8.3 L218 红线承接+macro_scorecard.py L32-33 先例)
DISCLAIMER = (
    "本判定材料为项目工程收尾状态如实汇编,不构成投资建议(禁交易/禁仓位/"
    "禁收益承诺);FAIL/NOT_VERIFIED 项如实留档,不美化")

# P-F-16 路径守卫组件(组件化比对,源码零连续字面量)
_RAW_DIR_GUARD = ("data", "daily")
_LIVE_ROOT_GUARD = ("AI内容", "🤖_AI投资项目", "每周宏观追踪", "investment-agent")

_PROVENANCE_FREEZE_CHAPTER = "冻结章 §十一(注入摘要,非工作树实读)"
_PROVENANCE_SELF_CHECK = "REPORT §四 登记值(执行席自评,独立审计待 R043)"
_PROVENANCE_ARCHIVE_RULE = (
    "机械转储自基线工作树(/tmp/p3-wp-f/gen_archive_table.py 生成件,"
    "2026-11-08T05:3xZ,证据包 06 类): docs/ 全档 144 件按文件名前缀分层+"
    "P3 族 A~E 代码/测试 10 件(上游各包 REPORT §零.2 登记清单对照同源)")

# ══ P-F-09 层序关闭登记表(11 行) ═══════════════════════════════════

_LAYER_ROWS = (
    ("L0-gov", "基线与治理层(架构v2/审计与计划档/P0-1基线重构/Gate A 修复链)",
     "层序闭合逐层核验 ✓+在场归档(" + _PROVENANCE_FREEZE_CHAPTER + ")",
     "L0-gov"),
    ("L1-p02", "P0-2 数据与守卫链(W1-W5+修复链+W5 封版件 P0_2_W5_SEALING 在场)",
     "层序闭合逐层核验 ✓+封版件在场(" + _PROVENANCE_FREEZE_CHAPTER + ")",
     "L1-p02"),
    ("L1w3-dataw3", "数据面 W3 修复链(DATA_W3 件)",
     "层序闭合逐层核验 ✓+在场归档(" + _PROVENANCE_FREEZE_CHAPTER + ")",
     "L1w3-dataw3"),
    ("L2a-e2ea", "P0-3 E2E-A(W1)",
     "层序闭合逐层核验 ✓(" + _PROVENANCE_FREEZE_CHAPTER + ")", "L2a-e2ea"),
    ("L2fa-p03fa", "P0-3 层终验件(P03 final acceptance)",
     "层序闭合逐层核验 ✓(" + _PROVENANCE_FREEZE_CHAPTER + ")", "L2fa-p03fa"),
    ("L2b-e2eb", "P0-3 E2E-B(B1-B5)",
     "层序闭合逐层核验 ✓(" + _PROVENANCE_FREEZE_CHAPTER + ")", "L2b-e2eb"),
    ("L3-glm", "GLM 研究结论层(G1-G4;G4 凭证面=PENDING 用户实批面,本包零触及)",
     "层序闭合逐层核验 ✓(" + _PROVENANCE_FREEZE_CHAPTER + ")", "L3-glm"),
    ("L4-p1", "P1 族(设计+对比+gap08+WP-A..G+收口)",
     "层序闭合逐层核验 ✓(" + _PROVENANCE_FREEZE_CHAPTER + ")", "L4-p1"),
    ("L5-p2", "P2 族(设计三件+WP-A..D)",
     "层序闭合逐层核验 ✓(" + _PROVENANCE_FREEZE_CHAPTER + ")", "L5-p2"),
    ("L6-p3ae", "P3 族前列包 A..E(A#31/32=R038+R067 merge b3628fd tip 202a09d2/"
     "B#33/34=R039+R068 merge c14931c tip e21789a/C#35=R040+整改续段 merge "
     "aeb39e8 tip 57eb3a3/D#36=R041 merge 91612378 tip f349b83/E#37=R042 "
     "merge 98f1a95 tip f74a126)",
     "同族前列包全部独立审计 PASS 落档(" + _PROVENANCE_FREEZE_CHAPTER + ")",
     "L6-p3"),
    ("L6-p3f", "P3 族末包 F(#38 本包: 执行席交付+自评)",
     "本包执行席交付+自评,独立审计 R043 待→NOT_VERIFIED@执行席", None),
)

# ══ P-F-10 归档索引(154 件冻结登记;禁随新增文件漂移) ═════════════

ARCHIVE_INDEX = {
    "L0-gov": (
        "docs/ARCHITECTURE_V2.md",
        "docs/P0_BASELINE_RESTRUCT_DELIVERY.md",
        "docs/P0_BASELINE_RESTRUCT_REPORT.md",
        "docs/P0_GATE_A_ACCEPTANCE.md",
        "docs/P0_GATE_A_REPAIR_01.md",
        "docs/P0_GATE_A_REPAIR_02.md",
        "docs/P0_GATE_A_REPAIR_03.md",
        "docs/P0_GATE_A_REPAIR_04.md",
        "docs/P0_GATE_A_REPAIR_05.md",
        "docs/P0_GATE_A_REPAIR_06.md",
        "docs/P0_GATE_A_REPAIR_07.md",
        "docs/P0_GATE_A_REPAIR_08.md",
        "docs/P0_GATE_A_REPAIR_09.md",
        "docs/P0_GATE_A_REPAIR_10.md",
        "docs/P0_GATE_A_REPAIR_11.md",
        "docs/P0_SB_FLOW_BACKUP_DELIVERY.md",
        "docs/PHASE0_AUDIT.md",
        "docs/REAL_REPORT_AUDIT.md",
        "docs/REMAINING_ISSUES.md",
        "docs/UPGRADE_PLAN.md",
        "docs/github_actions_tests.yml",
    ),
    "L1-p02": (
        "docs/P0_2_W1_DELIVERY.md",
        "docs/P0_2_W1_DEV_LIVE_ISOLATION.json",
        "docs/P0_2_W1_DEV_LIVE_ISOLATION.md",
        "docs/P0_2_W1_FIX1_DELIVERY.md",
        "docs/P0_2_W1_REGISTRY_AUDIT.json",
        "docs/P0_2_W1_REGISTRY_AUDIT.md",
        "docs/P0_2_W2_DELIVERY.md",
        "docs/P0_2_W2_DEV_LIVE_ISOLATION.json",
        "docs/P0_2_W2_DEV_LIVE_ISOLATION.md",
        "docs/P0_2_W2_FIX1_APPROVAL_EVIDENCE.md",
        "docs/P0_2_W2_FIX1_DELIVERY.md",
        "docs/P0_2_W2_FIX1_POLICY_DFEDTARL.md",
        "docs/P0_2_W2_FIX1_POLICY_HK_CALENDAR.md",
        "docs/P0_2_W2_FIX2_APPROVAL_FORENSICS.md",
        "docs/P0_2_W2_FIX2_DELIVERY.md",
        "docs/P0_2_W2_FIX2_POLICY_HSAHP.md",
        "docs/P0_2_W2_FIX3_DELIVERY.md",
        "docs/P0_2_W2_FIX4_DELIVERY.md",
        "docs/P0_2_W2_FIX5_DELIVERY.md",
        "docs/P0_2_W2_FIX6_DELIVERY.md",
        "docs/P0_2_W2_FRESHNESS.json",
        "docs/P0_2_W2_FRESHNESS.md",
        "docs/P0_2_W3_DELIVERY.md",
        "docs/P0_2_W3_FIX1_DELIVERY.md",
        "docs/P0_2_W3_FIX2_DELIVERY.md",
        "docs/P0_2_W3_FIX3_DELIVERY.md",
        "docs/P0_2_W3_FIX4_DELIVERY.md",
        "docs/P0_2_W3_FIX5_DELIVERY.md",
        "docs/P0_2_W4_DELIVERY.md",
        "docs/P0_2_W4_FIX1_DELIVERY.md",
        "docs/P0_2_W4_FIX2_DELIVERY.md",
        "docs/P0_2_W4_FIX3_DELIVERY.md",
        "docs/P0_2_W4_FIX4_DELIVERY.md",
        "docs/P0_2_W5_DATASRC_B_DELIVERY.md",
        "docs/P0_2_W5_DELIVERY.md",
        "docs/P0_2_W5_EMWIN_DELIVERY.md",
        "docs/P0_2_W5_FINALVERDICT_R2_INDEX.md",
        "docs/P0_2_W5_FIX1_DELIVERY.md",
        "docs/P0_2_W5_FIX2_DELIVERY.md",
        "docs/P0_2_W5_FIX3_DELIVERY.md",
        "docs/P0_2_W5_RERUN_2_DELIVERY.md",
        "docs/P0_2_W5_RERUN_3_DELIVERY.md",
        "docs/P0_2_W5_RERUN_4_DELIVERY.md",
        "docs/P0_2_W5_RERUN_DELIVERY.md",
        "docs/P0_2_W5_SEALING.md",
    ),
    "L1w3-dataw3": (
        "docs/DATA_W3_DELIVERY.md",
        "docs/DATA_W3_FIX_REPORT.md",
    ),
    "L2a-e2ea": (
        "docs/P03_W1_DELIVERY.md",
        "docs/P03_W1_E2EA_REPORT.md",
    ),
    "L2fa-p03fa": (
        "docs/P03_FINAL_ACCEPTANCE_DELIVERY.md",
        "docs/P03_FINAL_ACCEPTANCE_REPORT.md",
    ),
    "L2b-e2eb": (
        "docs/P03_E2EB_B1_DELIVERY.md",
        "docs/P03_E2EB_B1_REPORT.md",
        "docs/P03_E2EB_B2_DELIVERY.md",
        "docs/P03_E2EB_B2_REPORT.md",
        "docs/P03_E2EB_B3_DELIVERY.md",
        "docs/P03_E2EB_B3_REPORT.md",
        "docs/P03_E2EB_B4_DELIVERY.md",
        "docs/P03_E2EB_B4_REPORT.md",
        "docs/P03_E2EB_B5_DELIVERY.md",
        "docs/P03_E2EB_B5_REPORT.md",
        "docs/P03_E2EB_DELIVERY.md",
        "docs/P03_E2EB_DESIGN.md",
        "docs/P03_E2EB_QUERY_SURFACE_INVENTORY.md",
    ),
    "L3-glm": (
        "docs/P03_W2_GLM_DELIVERY.md",
        "docs/P03_W2_GLM_DESIGN.md",
        "docs/P03_W2_GLM_G1_DELIVERY.md",
        "docs/P03_W2_GLM_G1_REPORT.md",
        "docs/P03_W2_GLM_G2_DELIVERY.md",
        "docs/P03_W2_GLM_G2_REPORT.md",
        "docs/P03_W2_GLM_G3_DELIVERY.md",
        "docs/P03_W2_GLM_G3_REPORT.md",
        "docs/P03_W2_GLM_G4_CREDENTIAL_REGISTRY.md",
        "docs/P03_W2_GLM_G4_DELIVERY.md",
        "docs/P03_W2_GLM_G4_REPORT.md",
        "docs/P03_W2_GLM_INVENTORY.md",
    ),
    "L4-p1": (
        "docs/P1_CLOSE_DELIVERY.md",
        "docs/P1_CLOSE_REPORT.md",
        "docs/P1_DATA_NEEDS_INVENTORY.md",
        "docs/P1_DELIVERY.md",
        "docs/P1_DESIGN.md",
        "docs/P1_DESIGN_COMP_DELIVERY.md",
        "docs/P1_DESIGN_COMP_REPORT.md",
        "docs/P1_GAP08_DELIVERY.md",
        "docs/P1_GAP08_REPORT.md",
        "docs/P1_WP_A_DELIVERY.md",
        "docs/P1_WP_A_REPORT.md",
        "docs/P1_WP_B_DELIVERY.md",
        "docs/P1_WP_B_REPORT.md",
        "docs/P1_WP_C_DELIVERY.md",
        "docs/P1_WP_C_REPORT.md",
        "docs/P1_WP_D_DELIVERY.md",
        "docs/P1_WP_D_REPORT.md",
        "docs/P1_WP_E_DELIVERY.md",
        "docs/P1_WP_E_REPORT.md",
        "docs/P1_WP_F_DELIVERY.md",
        "docs/P1_WP_F_REPORT.md",
        "docs/P1_WP_G_DELIVERY.md",
        "docs/P1_WP_G_REPORT.md",
    ),
    "L5-p2": (
        "docs/P2_DELIVERY.md",
        "docs/P2_DESIGN.md",
        "docs/P2_INVENTORY.md",
        "docs/P2_WP_A_DELIVERY.md",
        "docs/P2_WP_A_REPORT.md",
        "docs/P2_WP_B_DELIVERY.md",
        "docs/P2_WP_B_REPORT.md",
        "docs/P2_WP_C_DELIVERY.md",
        "docs/P2_WP_C_REPORT.md",
        "docs/P2_WP_D_DELIVERY.md",
        "docs/P2_WP_D_REPORT.md",
    ),
    "L6-p3": (
        "docs/P3_DELIVERY.md",
        "docs/P3_DESIGN.md",
        "docs/P3_INVENTORY.md",
        "docs/P3_WP_A_DELIVERY.md",
        "docs/P3_WP_A_REPORT.md",
        "docs/P3_WP_B_DELIVERY.md",
        "docs/P3_WP_B_REPORT.md",
        "docs/P3_WP_C_DELIVERY.md",
        "docs/P3_WP_C_REPORT.md",
        "docs/P3_WP_D_DELIVERY.md",
        "docs/P3_WP_D_REPORT.md",
        "docs/P3_WP_E_DELIVERY.md",
        "docs/P3_WP_E_REPORT.md",
        "scripts/evidence_linkage.py",
        "scripts/personal_flow_integration.py",
        "scripts/prediction_review.py",
        "scripts/report_quality_review.py",
        "scripts/research_index.py",
        "tests/test_p3_wp_a.py",
        "tests/test_p3_wp_b.py",
        "tests/test_p3_wp_c.py",
        "tests/test_p3_wp_d.py",
        "tests/test_p3_wp_e.py",
    ),
}

# ══ P-F-03 终验清单(24 项六段;字段封闭集;kind 枚举 7 值) ═════════

_CHECKLIST_ROWS = (
    # S1 七 AC 复演式终验(7)——verdict=REPORT §四 登记值输入(P-F-12)
    ("FA-S1-AC-01", "S1", "七AC复演·AC-01",
     "F-AC-01 规格抄录与交付面登记正确性(REPORT §零 vs DESIGN §7 逐字一致+清单结构约束)",
     "SEVEN_AC_INPUT", "合同§一"),
    ("FA-S1-AC-02", "S1", "七AC复演·AC-02",
     "F-AC-02 验收要点逐条交付与证据映射(要点①-⑤映射表无漏检+落点真实)",
     "SEVEN_AC_INPUT", "合同§二"),
    ("FA-S1-AC-03", "S1", "七AC复演·AC-03",
     "F-AC-03 测试与确定性验证(全合成 fixture+黄金字面量+漂移维护策略专节)",
     "SEVEN_AC_INPUT", "合同§三"),
    ("FA-S1-AC-04", "S1", "七AC复演·AC-04",
     "F-AC-04 引用真实性与注入边界(file:line 可寻+注入摘要标注)",
     "SEVEN_AC_INPUT", "合同§四"),
    ("FA-S1-AC-05", "S1", "七AC复演·AC-05",
     "F-AC-05 范围/分支/生产隔离(diff 恰 A=4+纯线性+LIVE/launchd 零触碰)",
     "SEVEN_AC_INPUT", "合同§五"),
    ("FA-S1-AC-06", "S1", "七AC复演·AC-06",
     "F-AC-06 CI 与证据包交付(分支 run=操作者 CHECKPOINT 面@执行席不可达)",
     "SEVEN_AC_INPUT", "合同§六"),
    ("FA-S1-AC-07", "S1", "七AC复演·AC-07",
     "F-AC-07 研究纪律与使用边界(快照纪律/零真实调用/状态保护/零建议)",
     "SEVEN_AC_INPUT", "合同§七"),
    # S2 层序关闭核对(11)
    ("FA-S2-01", "S2", "层序关闭·L0-gov",
     "层关闭登记事实+交付件在场核验(L0-gov 基线与治理层)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-02", "S2", "层序关闭·L1-p02",
     "层关闭登记事实+交付件在场核验(L1-p02 P0-2 数据与守卫链)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-03", "S2", "层序关闭·L1w3-dataw3",
     "层关闭登记事实+交付件在场核验(L1w3-dataw3 数据面 W3 修复链)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-04", "S2", "层序关闭·L2a-e2ea",
     "层关闭登记事实+交付件在场核验(L2a-e2ea P0-3 E2E-A)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-05", "S2", "层序关闭·L2fa-p03fa",
     "层关闭登记事实+交付件在场核验(L2fa-p03fa P0-3 层终验件)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-06", "S2", "层序关闭·L2b-e2eb",
     "层关闭登记事实+交付件在场核验(L2b-e2eb P0-3 E2E-B B1-B5)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-07", "S2", "层序关闭·L3-glm",
     "层关闭登记事实+交付件在场核验(L3-glm GLM 研究结论层 G1-G4)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-08", "S2", "层序关闭·L4-p1",
     "层关闭登记事实+交付件在场核验(L4-p1 P1 族)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-09", "S2", "层序关闭·L5-p2",
     "层关闭登记事实+交付件在场核验(L5-p2 P2 族)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-10", "S2", "层序关闭·L6-p3ae",
     "层关闭登记事实+交付件在场核验(L6-p3ae P3 族前列包 A..E 全 PASS)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    ("FA-S2-11", "S2", "层序关闭·L6-p3f",
     "层关闭登记事实+交付件在场核验(L6-p3f P3 族末包 F 本包,独立审计 R043 待)",
     "LAYER_CLOSURE", "DESIGN L202/L203"),
    # S3 各层交付件归档索引(1)
    ("FA-S3-01", "S3", "归档索引·在场核验",
     "各层交付件归档索引构建与在场核验(154 件登记索引逐件在场+sha256 指纹;"
     "F 自身 4 件自豁免)", "ARCHIVE_INDEX", "DESIGN L202"),
    # S4 横切运行时验收登记(3,不预执行)
    ("FA-S4-01", "S4", "横切登记·①",
     "①≥7 个真实计划执行日 + ≥1 次真实周报回归(原始 P0 要求)——登记面承接,零预执行",
     "RUNTIME_WINDOW", "DESIGN L205"),
    ("FA-S4-02", "S4", "横切登记·②",
     ("②30 天生产观察 + 计划任务成功率≥95% + ≥4 次正式周报;日历时间不可压缩: "
      "LIVE 部署后尽早起算,与后续层开发并行计时——登记面承接,零预执行"),
     "RUNTIME_WINDOW", "DESIGN L206"),
    ("FA-S4-03", "S4", "横切登记·③",
     "③执行载体 = R018 停泊件(注入摘要级对接,本包零预执行)",
     "RUNTIME_CARRIER", "DESIGN L207"),
    # S5 清单纪律(1)
    ("FA-S5-01", "S5", "清单纪律·④",
     ("④终验清单与计时起点先登记后运行、禁回改(终验开始后回改清单被拒; "
      "digest 链 baseline→started→compiled 逐级等值)"),
     "DISCIPLINE", "DESIGN L208④+§8.5 L220"),
    # S6 总封版判定(1)
    ("FA-S6-01", "S6", "总封版判定·⑤",
     "⑤总封版判定材料如实汇编(FAIL 项如实留档,不美化;判定规则 P-F-13)",
     "DETERMINATION", "DESIGN L208⑤"),
)

ITEM_FIELDS = ("design_anchor", "item_id", "kind", "requirement", "section",
               "title")
KIND_VALUES = ("ARCHIVE_INDEX", "DETERMINATION", "DISCIPLINE",
               "LAYER_CLOSURE", "RUNTIME_CARRIER", "RUNTIME_WINDOW",
               "SEVEN_AC_INPUT")
SECTION_COUNTS = {"S1": 7, "S2": 11, "S3": 1, "S4": 3, "S5": 1, "S6": 1}
ARCHIVE_TOTAL_FILES = 154

LAYER_REGISTRY = tuple(
    {"layer_id": r[0], "title": r[1], "closure_provenance": r[2],
     "archive_layer": r[3]}
    for r in _LAYER_ROWS
)


def registered_checklist():
    """终验清单登记值(24 项;返回 dict 列表,字段封闭集 ITEM_FIELDS)。"""
    return [
        {"item_id": r[0], "section": r[1], "title": r[2],
         "requirement": r[3], "kind": r[4], "design_anchor": r[5]}
        for r in _CHECKLIST_ROWS
    ]


def registered_timing():
    """计时基线登记值(DP-10 定值 (a)+(i)+阈值五值)。"""
    return {
        "dp10_classification": DP10_CLASSIFICATION,
        "dp10_user_approval": DP10_USER_APPROVAL,
        "observation_start": DP10_OBSERVATION_START,
        "observation_window_days": DP10_OBSERVATION_WINDOW_DAYS,
        "observation_end": DP10_OBSERVATION_END,
        "supplementary_round_after": SUPPLEMENTARY_ROUND_AFTER,
        "carrier": DP10_CARRIER,
        "carrier_interface_level": DP10_CARRIER_INTERFACE_LEVEL,
        "zero_preexecution": DP10_ZERO_PREEXECUTION,
        "thresholds": {
            "min_scheduled_execution_days": RT_MIN_SCHEDULED_EXECUTION_DAYS,
            "min_weekly_regressions": RT_MIN_WEEKLY_REGRESSIONS,
            "min_observation_days": RT_MIN_OBSERVATION_DAYS,
            "min_task_success_rate_pct": RT_MIN_TASK_SUCCESS_RATE_PCT,
            "min_formal_weekly_reports": RT_MIN_FORMAL_WEEKLY_REPORTS,
        },
    }


# ══ 日历纯函数(P-F-15;零 datetime,3.9/3.11 行为一致由构造保证) ═══

_MONTH_LENGTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _is_leap(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _month_length(year, month):
    if month == 2 and _is_leap(year):
        return 29
    return _MONTH_LENGTHS[month - 1]


def parse_ymd(text):
    """严格规范形 YYYY-MM-DD(十位带杠;紧凑形/周形拒绝)。"""
    if (not isinstance(text, str) or len(text) != 10 or text[4] != "-"
            or text[7] != "-"):
        raise ValueError("日期须为规范形 YYYY-MM-DD: %r" % (text,))
    y_s, m_s, d_s = text[0:4], text[5:7], text[8:10]
    if not (y_s.isdigit() and m_s.isdigit() and d_s.isdigit()):
        raise ValueError("日期须为规范形 YYYY-MM-DD: %r" % (text,))
    year, month, day = int(y_s), int(m_s), int(d_s)
    if year < 1 or month < 1 or month > 12:
        raise ValueError("日期月/年越界: %r" % (text,))
    if day < 1 or day > _month_length(year, month):
        raise ValueError("日期日越界: %r" % (text,))
    return (year, month, day)


def ymd_to_ordinal(text):
    year, month, day = parse_ymd(text)
    days = 0
    for yy in range(1, year):
        days += 366 if _is_leap(yy) else 365
    for mm in range(1, month):
        days += _month_length(year, mm)
    return days + day


def ordinal_to_ymd(number):
    if not isinstance(number, int) or number < 1:
        raise ValueError("序数须为正整数: %r" % (number,))
    rest, year = number, 1
    while rest > (366 if _is_leap(year) else 365):
        rest -= 366 if _is_leap(year) else 365
        year += 1
    month = 1
    while rest > _month_length(year, month):
        rest -= _month_length(year, month)
        month += 1
    return "%04d-%02d-%02d" % (year, month, rest)


def add_days(text, n):
    return ordinal_to_ymd(ymd_to_ordinal(text) + n)


def days_between(date_a, date_b):
    return ymd_to_ordinal(date_b) - ymd_to_ordinal(date_a)


# ══ 序列化/摘要/IO helper(P-F-17: open 恰 3 helper 各 1 处) ═══

def _canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path):
    guarded = _guarded_path(path)
    with open(guarded, "rb") as handle:
        return handle.read()


def _append_journal_line(state_path, line):
    guarded = _guarded_path(state_path)
    parent = os.path.dirname(guarded)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(guarded, "a", encoding="utf-8") as handle:
        handle.write(line)


def _write_text_once(path, text):
    guarded = _guarded_path(path)
    parent = os.path.dirname(guarded)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(guarded, "w", encoding="utf-8") as handle:
        handle.write(text)


def _guarded_path(path):
    """路径守卫(P-F-16): LIVE 根四组件序列拒+data/daily 相邻组件拒,全部读写面。"""
    normalized = os.path.normpath(os.path.expanduser(str(path)))
    parts = [p for p in normalized.split(os.sep) if p not in ("", ".")]
    for i in range(len(parts) - 3):
        if tuple(parts[i:i + 4]) == _LIVE_ROOT_GUARD:
            raise ValueError("路径触及 LIVE 根(禁写红线): %s" % (normalized,))
    for i in range(len(parts) - 1):
        if tuple(parts[i:i + 2]) == _RAW_DIR_GUARD:
            raise ValueError("路径触及原始采集档 %s(快照纪律): %s"
                             % ("/".join(_RAW_DIR_GUARD), normalized))
    return normalized


# ══ P-F-08 禁回改执行器: digest 链+状态机 ═══════════════════════

def fa_digest():
    """终验指纹=sha256(canonical_json([清单登记值, 计时登记值]))。"""
    return _sha256_bytes(
        _canonical_bytes([registered_checklist(), registered_timing()]))


def _validate_as_of(as_of):
    if (not isinstance(as_of, str) or len(as_of) != 20 or as_of[10] != "T"
            or as_of[19] != "Z"):
        raise ValueError("as_of 须为规范形 YYYY-MM-DDTHH:MM:SSZ: %r" % (as_of,))
    parse_ymd(as_of[:10])
    hh, mm, ss = as_of[11:13], as_of[14:16], as_of[17:19]
    if not (hh.isdigit() and mm.isdigit() and ss.isdigit()):
        raise ValueError("as_of 时分秒须为数字: %r" % (as_of,))
    if int(hh) > 23 or int(mm) > 59 or int(ss) > 59:
        raise ValueError("as_of 时分秒越界: %r" % (as_of,))
    return as_of


def _validate_journal_record(obj):
    if not isinstance(obj, dict):
        raise ValueError("状态日志行须为 JSON 对象")
    rtype = obj.get("record_type")
    if rtype not in JOURNAL_RECORD_TYPES:
        raise ValueError("记录类型越界(封闭集 %s): %r"
                         % ("/".join(JOURNAL_RECORD_TYPES), rtype))
    if obj.get("journal_schema_version") != JOURNAL_SCHEMA_VERSION:
        raise ValueError("journal_schema_version 不符: %r" % (obj,))
    _validate_as_of(obj.get("as_of"))
    if not isinstance(obj.get("fa_digest"), str) or not obj["fa_digest"]:
        raise ValueError("fa_digest 缺失: %r" % (obj,))
    if rtype == "compiled":
        if not isinstance(obj.get("determination"), str):
            raise ValueError("compiled 记录缺 determination: %r" % (obj,))
        for key in ("materials_json_sha256", "materials_md_sha256"):
            value = obj.get(key)
            if value is not None and not isinstance(value, str):
                raise ValueError("compiled 记录 %s 类型不符: %r" % (key, obj))
    extra = set(obj) - {
        "record_type", "journal_schema_version", "as_of", "fa_digest",
        "determination", "materials_json_sha256", "materials_md_sha256"}
    if extra:
        raise ValueError("记录含封闭集外字段 %s: %r" % (sorted(extra), obj))
    return obj


def read_journal(state_path):
    """读状态日志(JSONL append-only;坏行/非 dict 行/记录违式→ValueError)。"""
    guarded = _guarded_path(state_path)
    if not os.path.isfile(guarded):
        return []
    records = []
    for line in _read_bytes(guarded).decode("utf-8").splitlines():
        if not line.strip():
            raise ValueError("状态日志含空行(档案损坏,fail-loud)")
        try:
            obj = json.loads(line)
        except ValueError as exc:
            raise ValueError("状态日志坏行(fail-loud): %s" % (exc,))
        records.append(_validate_journal_record(obj))
    return records


def _journal_counts(records):
    counts = {}
    for rec in records:
        counts[rec["record_type"]] = counts.get(rec["record_type"], 0) + 1
    return counts


def write_baseline(state_path, as_of):
    """登记基线(恰 1 次): 记录终验指纹。"""
    _validate_as_of(as_of)
    records = read_journal(state_path)
    if records:
        raise ValueError("状态日志非空: baseline 已登记(append-only 单发)")
    record = {"record_type": "baseline",
              "journal_schema_version": JOURNAL_SCHEMA_VERSION,
              "as_of": as_of, "fa_digest": fa_digest()}
    _append_journal_line(state_path,
                         json.dumps(record, sort_keys=True,
                                    ensure_ascii=False) + "\n")
    return record


def start_final_acceptance(state_path, as_of):
    """终验开始(恰 1 次;须在 baseline 之后): 复核指纹等值,不符=清单漂移拒开。"""
    _validate_as_of(as_of)
    records = read_journal(state_path)
    counts = _journal_counts(records)
    if counts.get("baseline", 0) != 1:
        raise ValueError("须先恰 1 次 baseline(当前 baseline=%d)"
                         % counts.get("baseline", 0))
    if counts.get("started", 0) or counts.get("compiled", 0):
        raise ValueError("终验已开始或已汇编(started/compiled 在案,单发)")
    baseline_digest = records[0]["fa_digest"]
    current = fa_digest()
    if current != baseline_digest:
        raise ValueError("终验清单/计时与登记基线不符(疑似回改,禁开): "
                         "baseline=%s current=%s" % (baseline_digest, current))
    record = {"record_type": "started",
              "journal_schema_version": JOURNAL_SCHEMA_VERSION,
              "as_of": as_of, "fa_digest": current}
    _append_journal_line(state_path,
                         json.dumps(record, sort_keys=True,
                                    ensure_ascii=False) + "\n")
    return record


def propose_checklist_amendment(state_path, note):
    """清单修订提案——恒拒(L208④: 终验开始后回改清单被拒;登记后亦禁回改)。"""
    records = read_journal(state_path)
    if not records:
        raise ValueError("未登记,无清单可改(先登记后运行纪律)")
    counts = _journal_counts(records)
    if counts.get("started", 0) or counts.get("compiled", 0):
        raise ValueError("终验开始后回改清单被拒(DESIGN L208④)")
    raise ValueError("已登记禁回改(先登记后运行纪律;DESIGN L208④)")


# ══ P-F-11 归档索引核验 ═══════════════════════════════════════

def _sha256_file(path):
    return _sha256_bytes(_read_bytes(path))


def _validate_index(index):
    if not isinstance(index, dict) or not index:
        raise ValueError("索引须为非空 dict(层→相对路径序列)")
    for layer_id, files in index.items():
        if not isinstance(layer_id, str) or not layer_id:
            raise ValueError("层标识须为非空字符串: %r" % (layer_id,))
        if isinstance(files, (str, bytes)) or not isinstance(files, (tuple, list)):
            raise ValueError("层 %s 文件集须为序列" % (layer_id,))
        for rel in files:
            if not isinstance(rel, str) or not rel:
                raise ValueError("文件路径须为非空字符串: %r" % (rel,))


def verify_archive_index(repo_root, index=None):
    """逐件在场核验+sha256 指纹;缺席如实记录(不美化)。"""
    use_index = ARCHIVE_INDEX if index is None else index
    _validate_index(use_index)
    root = _guarded_path(repo_root)
    layers = []
    total = present = 0
    missing_all = []
    digest_map = {}
    for layer_id in sorted(use_index):
        entries = {}
        missing = []
        for rel in use_index[layer_id]:
            full = os.path.join(root, rel)
            if os.path.isfile(_guarded_path(full)):
                entries[rel] = _sha256_file(full)
            else:
                entries[rel] = None
                missing.append(rel)
        digest = _sha256_bytes(_canonical_bytes(entries))
        digest_map[layer_id] = digest
        total += len(use_index[layer_id])
        present += len(use_index[layer_id]) - len(missing)
        missing_all.extend(missing)
        layers.append({"layer_id": layer_id,
                       "files_total": len(use_index[layer_id]),
                       "files_present": len(use_index[layer_id]) - len(missing),
                       "files_missing": missing, "digest": digest})
    return {"layers": layers,
            "layers_by_id": {row["layer_id"]: row for row in layers},
            "layer_digests": digest_map,
            "overall_digest": _sha256_bytes(_canonical_bytes(digest_map)),
            "total_files": total, "total_present": present,
            "total_missing": len(missing_all),
            "missing_paths": missing_all}


# ══ P-F-12 七 AC 复演输入契约+P-F-13 判定规则 ═══════════════════

def validate_seven_ac_selfcheck(table):
    if not isinstance(table, dict):
        raise ValueError("七 AC 自评表须为 dict")
    if tuple(sorted(table.keys())) != SEVEN_AC_IDS:
        raise ValueError("七 AC 自评表键集须恰为 %s" % (list(SEVEN_AC_IDS),))
    for ac_id in SEVEN_AC_IDS:
        row = table[ac_id]
        if not isinstance(row, dict):
            raise ValueError("%s 行须为 dict" % (ac_id,))
        if tuple(sorted(row.keys())) != _SELFCHECK_ROW_FIELDS:
            raise ValueError("%s 行字段封闭集 %s" % (ac_id, list(_SELFCHECK_ROW_FIELDS)))
        if row["verdict"] not in ALLOWED_VERDICTS:
            raise ValueError("%s.verdict 须属 %s: %r"
                             % (ac_id, list(ALLOWED_VERDICTS), row["verdict"]))
        if not isinstance(row["evidence"], str) or not row["evidence"].strip():
            raise ValueError("%s.evidence 须为非空字符串" % (ac_id,))
        if not isinstance(row["note"], str):
            raise ValueError("%s.note 须为字符串" % (ac_id,))
    return table


def determine(verdicts):
    values = list(verdicts)
    if "FAIL" in values:
        return "NOT_SEALED"
    if "NOT_VERIFIED" in values:
        return "PENDING_SUPPLEMENTARY_EVIDENCE"
    return "SEALED"


# ══ P-F-14 判定材料汇编与渲染 ═════════════════════════════════

SEAL_DOC_FIELDS = ("archive_index", "as_of", "checklist_verdicts",
                   "determination", "determination_rule", "disclaimer",
                   "fa_digest", "fail_items", "layer_closure",
                   "provenance_notes", "runtime_window", "schema_version",
                   "seven_ac_reverification", "timing_baseline")


def compile_seal_determination(repo_root, state_path, seven_ac_selfcheck,
                               as_of, out_dir=None, archive_index=None):
    """总封版判定材料汇编(L208⑤;须在 started 之后,恰 1 次;如实不美化)。"""
    _validate_as_of(as_of)
    validate_seven_ac_selfcheck(seven_ac_selfcheck)
    records = read_journal(state_path)
    counts = _journal_counts(records)
    if (counts.get("baseline", 0) != 1 or counts.get("started", 0) != 1
            or counts.get("compiled", 0) != 0):
        raise ValueError("状态机须为 baseline=1+started=1+compiled=0(当前 %r)"
                         % (counts,))
    baseline_digest = records[0]["fa_digest"]
    started_digest = records[1]["fa_digest"]
    current_digest = fa_digest()
    if not (baseline_digest == started_digest == current_digest):
        raise ValueError("终验清单/计时 digest 链失配(疑似回改,拒汇编): "
                         "baseline=%s started=%s current=%s"
                         % (baseline_digest, started_digest, current_digest))

    timing = registered_timing()
    elapsed = days_between(DP10_OBSERVATION_START, as_of[:10])
    archive = verify_archive_index(repo_root, archive_index)

    checklist_by_id = {row["item_id"]: row for row in registered_checklist()}
    verdicts = []
    fail_items = []

    def _emit(item_id, verdict, detail):
        row = dict(checklist_by_id[item_id])
        row["verdict"] = verdict
        row["detail"] = detail
        verdicts.append(row)
        if verdict == "FAIL":
            fail_items.append(row)

    # S1 七 AC 复演(verdict=登记输入,非模块自算)
    seven_rows = []
    for ac_id in SEVEN_AC_IDS:
        row = seven_ac_selfcheck[ac_id]
        item_id = "FA-S1-" + ac_id
        _emit(item_id, row["verdict"],
              "evidence=%s; note=%s" % (row["evidence"], row["note"]))
        seven_rows.append({"ac_id": ac_id,
                           "title": checklist_by_id[item_id]["title"],
                           "verdict": row["verdict"],
                           "evidence": row["evidence"], "note": row["note"],
                           "provenance": _PROVENANCE_SELF_CHECK})

    # S2 层序关闭核对
    layer_rows = []
    for layer in LAYER_REGISTRY:
        layer_id = layer["layer_id"]
        item_id = "FA-S2-%02d" % (list.index([l["layer_id"] for l in LAYER_REGISTRY], layer_id) + 1)
        if layer["archive_layer"] is None:
            present = [p for p in SELF_EXCLUDED_PATHS
                       if os.path.isfile(_guarded_path(os.path.join(
                           _guarded_path(repo_root), p)))]
            missing = [p for p in SELF_EXCLUDED_PATHS if p not in present]
            layer_rows.append({"layer_id": layer_id, "title": layer["title"],
                               "files_total": len(SELF_EXCLUDED_PATHS),
                               "files_present": len(present),
                               "files_missing": missing,
                               "closure_provenance": layer["closure_provenance"],
                               "verdict": "NOT_VERIFIED",
                               "note": "执行席交付+自评在案(自身 4 件自豁免"
                                       "索引,在场核验=%d/4);独立审计 R043 待"
                                       % len(present)})
            _emit(item_id, "NOT_VERIFIED",
                  "层=%s; 独立审计 R043 待(NOT_VERIFIED@执行席); 自身交付件"
                  "在场 %d/4" % (layer_id, len(present)))
        else:
            info = archive["layers_by_id"][layer["archive_layer"]]
            ok = not info["files_missing"]
            verdict = "PASS" if ok else "FAIL"
            layer_rows.append({"layer_id": layer_id, "title": layer["title"],
                               "files_total": info["files_total"],
                               "files_present": info["files_present"],
                               "files_missing": info["files_missing"],
                               "closure_provenance": layer["closure_provenance"],
                               "verdict": verdict,
                               "note": ("交付件在场核验 %d/%d"
                                        % (info["files_present"],
                                           info["files_total"]))
                               + ("; 缺席如实登记: %s" % (info["files_missing"],)
                                  if info["files_missing"] else "")})
            _emit(item_id, verdict,
                  "层=%s; 关闭事实=%s; 在场核验=%d/%d%s"
                  % (layer_id, layer["closure_provenance"],
                     info["files_present"], info["files_total"],
                     ("; 缺席: %s" % (info["files_missing"],))
                     if info["files_missing"] else ""))

    # S3 归档索引
    _emit("FA-S3-01",
          "PASS" if archive["total_missing"] == 0 else "FAIL",
          "索引 %d 件; 在场 %d; 缺席 %d%s; overall_digest=%s"
          % (archive["total_files"], archive["total_present"],
             archive["total_missing"],
             ("; 缺席清单: %s" % (archive["missing_paths"],))
             if archive["missing_paths"] else "",
             archive["overall_digest"]))

    # S4 横切运行时验收登记(不预执行)
    _emit("FA-S4-01", "NOT_VERIFIED",
          "登记面 only(零预执行); 阈值=%d 执行日+%d 周报回归; 证据汇编属 "
          "R018 载体/补证轮面(2026-12-05 后)"
          % (RT_MIN_SCHEDULED_EXECUTION_DAYS, RT_MIN_WEEKLY_REGRESSIONS))
    _emit("FA-S4-02", "NOT_VERIFIED",
          "登记面 only(零预执行); 观察窗 elapsed=%d/%d 天(起算 %s→终点 %s); "
          "阈值=成功率≥%d%%+正式周报≥%d; 证据汇编属 R018 载体/补证轮面"
          % (elapsed, DP10_OBSERVATION_WINDOW_DAYS, DP10_OBSERVATION_START,
             DP10_OBSERVATION_END, RT_MIN_TASK_SUCCESS_RATE_PCT,
             RT_MIN_FORMAL_WEEKLY_REPORTS))
    _emit("FA-S4-03", "PASS",
          "载体=%s(%s); 本模块零运行时执行面(登记纪律成立)"
          % (DP10_CARRIER, DP10_CARRIER_INTERFACE_LEVEL))

    # S5 清单纪律(digest 链在本汇编内已逐级复核)
    _emit("FA-S5-01", "PASS",
          "digest 链 baseline=started=current=%s(逐级等值复核通过; "
          "amendment 恒拒面在案)" % (current_digest,))

    determination = determine(row["verdict"] for row in verdicts)

    # S6 总封版判定
    _emit("FA-S6-01", "PASS",
          "判定材料按登记规则汇编完成(规则=%s); 判定=%s"
          % (DETERMINATION_RULE_TEXT, determination))

    doc = {
        "schema_version": SEAL_DOC_SCHEMA_VERSION,
        "as_of": as_of,
        "fa_digest": current_digest,
        "timing_baseline": timing,
        "runtime_window": {
            "start": DP10_OBSERVATION_START,
            "end": DP10_OBSERVATION_END,
            "window_days": DP10_OBSERVATION_WINDOW_DAYS,
            "elapsed_days_at_as_of": elapsed,
            "supplementary_round_after": SUPPLEMENTARY_ROUND_AFTER,
            "carrier": DP10_CARRIER,
            "carrier_interface_level": DP10_CARRIER_INTERFACE_LEVEL,
            "zero_preexecution": DP10_ZERO_PREEXECUTION,
            "thresholds": timing["thresholds"],
            "execution_face": "零执行面(登记面 only;证据汇编属 R018 载体+"
                              "2026-12-05 后补证轮)",
        },
        "seven_ac_reverification": seven_rows,
        "checklist_verdicts": verdicts,
        "layer_closure": layer_rows,
        "archive_index": {
            "layers": archive["layers"],
            "overall_digest": archive["overall_digest"],
            "total_files": archive["total_files"],
            "total_present": archive["total_present"],
            "total_missing": archive["total_missing"],
            "missing_paths": archive["missing_paths"],
            "self_excluded": list(SELF_EXCLUDED_PATHS),
            "construction_rule": _PROVENANCE_ARCHIVE_RULE,
        },
        "fail_items": fail_items,
        "determination": determination,
        "determination_rule": DETERMINATION_RULE_TEXT,
        "disclaimer": DISCLAIMER,
        "provenance_notes": {
            "closure_facts": _PROVENANCE_FREEZE_CHAPTER,
            "seven_ac": _PROVENANCE_SELF_CHECK,
            "archive_index": _PROVENANCE_ARCHIVE_RULE,
            "determination_rule": "REPORT §零.5 P-F-13 登记值",
        },
    }
    if tuple(sorted(doc.keys())) != SEAL_DOC_FIELDS:
        raise AssertionError("判定材料键集与封闭集不符(内部一致性)")

    json_sha = None
    md_sha = None
    if out_dir is not None:
        out_root = _guarded_path(out_dir)
        json_text = json.dumps(doc, sort_keys=True, ensure_ascii=False,
                               indent=1)
        md_text = render_seal_determination(doc)
        json_path = os.path.join(out_root, "seal_determination.json")
        md_path = os.path.join(out_root, "seal_determination.md")
        _write_text_once(json_path, json_text + "\n")
        _write_text_once(md_path, md_text)
        json_sha = _sha256_bytes(json_text.encode("utf-8"))
        md_sha = _sha256_bytes(md_text.encode("utf-8"))
    record = {"record_type": "compiled",
              "journal_schema_version": JOURNAL_SCHEMA_VERSION,
              "as_of": as_of, "fa_digest": current_digest,
              "determination": determination,
              "materials_json_sha256": json_sha,
              "materials_md_sha256": md_sha}
    _append_journal_line(state_path,
                         json.dumps(record, sort_keys=True,
                                    ensure_ascii=False) + "\n")
    doc["journal_compiled_record"] = dict(record)
    return doc


def render_seal_determination(doc):
    """判定材料人读渲染(如实,不美化;含免责尾行)。"""
    lines = []
    lines.append("== 项目总封版判定材料(P3 终验·如实汇编) ==")
    lines.append("汇编时点(as_of): %s" % (doc["as_of"],))
    lines.append("终验指纹(fa_digest): %s" % (doc["fa_digest"],))
    rw = doc["runtime_window"]
    lines.append("-- 计时基线(DP-10 定值 (a)+(i)) --")
    lines.append("起算(LIVE 部署日): %s; 观察窗: %d 天; 终点: %s; "
                 "补证轮: %s 后收口" % (rw["start"], rw["window_days"],
                                        rw["end"],
                                        rw["supplementary_round_after"]))
    lines.append("载体: %s(%s,零预执行)" % (rw["carrier"],
                                            rw["carrier_interface_level"]))
    lines.append("观察钟 elapsed: %d/%d 天(as_of 时点)"
                 % (rw["elapsed_days_at_as_of"], rw["window_days"]))
    lines.append("-- 判定结论 --")
    lines.append("%s: %s" % (doc["determination"],
                             DETERMINATION_LABELS[doc["determination"]]))
    lines.append("判定规则: %s" % (doc["determination_rule"],))
    lines.append("-- S1 七 AC 复演式终验(%s) --" % (_PROVENANCE_SELF_CHECK,))
    for row in doc["seven_ac_reverification"]:
        lines.append("%s | %s | %s | note=%s"
                     % (row["ac_id"], row["verdict"], row["evidence"],
                        row["note"]))
    lines.append("-- S2 层序关闭核对 --")
    for row in doc["layer_closure"]:
        lines.append("%s | %s | 在场 %d/%d | %s%s"
                     % (row["layer_id"], row["verdict"], row["files_present"],
                        row["files_total"], row["closure_provenance"],
                        ("; 缺席: %s" % (row["files_missing"],))
                        if row["files_missing"] else ""))
    lines.append("-- S3 各层交付件归档索引 --")
    index = doc["archive_index"]
    for layer in index["layers"]:
        lines.append("%s: %d/%d 在场, digest=%s" % (layer["layer_id"],
                                                    layer["files_present"],
                                                    layer["files_total"],
                                                    layer["digest"]))
    lines.append("合计: %d/%d 在场; overall_digest=%s; F 自豁免 %d 件(%s)"
                 % (index["total_present"], index["total_files"],
                    index["overall_digest"], len(index["self_excluded"]),
                    "/".join(index["self_excluded"])))
    lines.append("-- S4 横切运行时验收登记(不预执行) --")
    for row in doc["checklist_verdicts"]:
        if row["section"] == "S4":
            lines.append("%s | %s | %s" % (row["item_id"], row["verdict"],
                                           row["detail"]))
    lines.append("-- S5/S6 清单纪律与判定汇编 --")
    for row in doc["checklist_verdicts"]:
        if row["section"] in ("S5", "S6"):
            lines.append("%s | %s | %s" % (row["item_id"], row["verdict"],
                                           row["detail"]))
    lines.append("-- FAIL 项如实区 --")
    if doc["fail_items"]:
        for row in doc["fail_items"]:
            lines.append("[FAIL] %s | %s | %s" % (row["item_id"],
                                                  row["title"],
                                                  row["detail"]))
    else:
        lines.append("无 FAIL 项")
    lines.append("-- 免责 --")
    lines.append(doc["disclaimer"])
    return "\n".join(lines) + "\n"


# ══ P-F-19 哨兵与入口 ═════════════════════════════════════════

def registered_dp_values():
    return {
        "DP-10": {
            "classification": DP10_CLASSIFICATION,
            "user_approval": DP10_USER_APPROVAL,
            "observation_start": DP10_OBSERVATION_START,
            "observation_window_days": DP10_OBSERVATION_WINDOW_DAYS,
            "observation_end": DP10_OBSERVATION_END,
            "carrier": DP10_CARRIER,
            "carrier_interface_level": DP10_CARRIER_INTERFACE_LEVEL,
            "zero_preexecution": DP10_ZERO_PREEXECUTION,
        },
        "DP-1/DP-2/DP-3": "上游 WP-P3-A 已登记定值;本包零消费零改写",
        "DP-5/DP-6": "上游 WP-P3-C 已登记定值;本包零消费零改写",
        "DP-7": "上游 WP-P3-D 已登记定值;本包零消费零改写",
        "DP-4/DP-8/DP-9": "零触及(WP-P3-B/D/E 面)",
    }


def registered_param_values():
    return {
        "fa_schema_version": FA_SCHEMA_VERSION,
        "seal_doc_schema_version": SEAL_DOC_SCHEMA_VERSION,
        "journal_schema_version": JOURNAL_SCHEMA_VERSION,
        "checklist_item_count": len(registered_checklist()),
        "section_counts": dict(SECTION_COUNTS),
        "layer_registry_count": len(LAYER_REGISTRY),
        "archive_layer_count": len(ARCHIVE_INDEX),
        "archive_total_files": sum(len(v) for v in ARCHIVE_INDEX.values()),
        "self_excluded_count": len(SELF_EXCLUDED_PATHS),
        "thresholds": registered_timing()["thresholds"],
        "supplementary_round_after": SUPPLEMENTARY_ROUND_AFTER,
        "journal_record_types": list(JOURNAL_RECORD_TYPES),
        "determination_rule": DETERMINATION_RULE_TEXT,
    }


def dp_selfcheck():
    """活性常量 vs 模块内登记镜像逐值对照+结构断言(回改任一定值→AssertionError)。"""
    mirror = {
        "dp10_user_approval": "user_approved_2026-11-08_now_dispatch_F",
        "observation_start": "2026-11-05",
        "observation_window_days": 30,
        "observation_end": "2026-12-05",
        "carrier": "R018_parked_artifact",
        "supplementary_round_after": "2026-12-05",
        "rt_min_scheduled_execution_days": 7,
        "rt_min_weekly_regressions": 1,
        "rt_min_observation_days": 30,
        "rt_min_task_success_rate_pct": 95,
        "rt_min_formal_weekly_reports": 4,
        "checklist_item_count": 24,
        "layer_registry_count": 11,
        "archive_layer_count": 10,
        "archive_total_files": 154,
        "self_excluded_count": 4,
    }
    actual = {
        "dp10_user_approval": DP10_USER_APPROVAL,
        "observation_start": DP10_OBSERVATION_START,
        "observation_window_days": DP10_OBSERVATION_WINDOW_DAYS,
        "observation_end": DP10_OBSERVATION_END,
        "carrier": DP10_CARRIER,
        "supplementary_round_after": SUPPLEMENTARY_ROUND_AFTER,
        "rt_min_scheduled_execution_days": RT_MIN_SCHEDULED_EXECUTION_DAYS,
        "rt_min_weekly_regressions": RT_MIN_WEEKLY_REGRESSIONS,
        "rt_min_observation_days": RT_MIN_OBSERVATION_DAYS,
        "rt_min_task_success_rate_pct": RT_MIN_TASK_SUCCESS_RATE_PCT,
        "rt_min_formal_weekly_reports": RT_MIN_FORMAL_WEEKLY_REPORTS,
        "checklist_item_count": len(registered_checklist()),
        "layer_registry_count": len(LAYER_REGISTRY),
        "archive_layer_count": len(ARCHIVE_INDEX),
        "archive_total_files": sum(len(v) for v in ARCHIVE_INDEX.values()),
        "self_excluded_count": len(SELF_EXCLUDED_PATHS),
    }
    assert actual == mirror, "登记定值与镜像失配(疑似回改): %r vs %r" % (
        actual, mirror)
    # 结构断言
    checklist = registered_checklist()
    ids = [row["item_id"] for row in checklist]
    assert len(ids) == len(set(ids)) == 24, "item_id 唯一性/计数失配"
    counts = {}
    for row in checklist:
        assert tuple(sorted(row.keys())) == ITEM_FIELDS, "项字段封闭集失配"
        assert row["kind"] in KIND_VALUES, "kind 枚举失配: %r" % (row["kind"],)
        counts[row["section"]] = counts.get(row["section"], 0) + 1
    assert counts == SECTION_COUNTS, "六段计数失配: %r" % (counts,)
    registry_ids = [l["layer_id"] for l in LAYER_REGISTRY]
    assert len(registry_ids) == len(set(registry_ids)) == 11, "层注册表失配"
    mapped_layers = {l["archive_layer"] for l in LAYER_REGISTRY
                     if l["archive_layer"] is not None}
    archive_ids = set(ARCHIVE_INDEX)
    assert archive_ids == mapped_layers, "层集与索引层集失配"
    all_paths = [p for files in ARCHIVE_INDEX.values() for p in files]
    assert len(all_paths) == len(set(all_paths)) == 154, "索引路径唯一性/计数失配"
    for p in all_paths + list(SELF_EXCLUDED_PATHS):
        _guarded_path(p)  # 零 data/daily 与 LIVE 路径(守卫即断言)
    assert set(SELF_EXCLUDED_PATHS) == {
        "scripts/project_final_seal.py", "tests/test_p3_wp_f.py",
        "docs/P3_WP_F_REPORT.md", "docs/P3_WP_F_DELIVERY.md"}, "自豁免集失配"
    # 日历算术断言(P-F-04)
    assert add_days(DP10_OBSERVATION_START,
                    DP10_OBSERVATION_WINDOW_DAYS) == DP10_OBSERVATION_END, \
        "观察窗终点算术失配"
    for probe in ("2026-11-05", "2026-12-05", "2024-02-29", "2000-01-01"):
        assert ordinal_to_ymd(ymd_to_ordinal(probe)) == probe, "日历往返失配"
    assert days_between("2026-11-05", "2026-11-08") == 3, "elapsed 基准失配"
    assert determine(["PASS"] * 24) == "SEALED", "判定规则 SEALED 失配"
    assert determine(["PASS", "NOT_VERIFIED"]) == "PENDING_SUPPLEMENTARY_EVIDENCE"
    assert determine(["PASS", "NOT_VERIFIED", "FAIL"]) == "NOT_SEALED", \
        "判定规则 FAIL 优先失配"
    return "dp_selfcheck OK(登记定值与镜像逐值一致+结构断言通过)"


def _usage():
    return ("用法: python3 scripts/project_final_seal.py [selfcheck] |\n"
            "      python3 scripts/project_final_seal.py run "
            "--repo-root ROOT --as-of YYYY-MM-DDTHH:MM:SSZ "
            "--seven-ac-file PATH [--state-path PATH] [--out-dir DIR]")


def _parse_run_args(argv):
    need = {"--repo-root": None, "--as-of": None, "--seven-ac-file": None,
            "--state-path": None, "--out-dir": None}
    i = 0
    while i < len(argv):
        flag = argv[i]
        if flag not in need or i + 1 >= len(argv):
            return None
        need[flag] = argv[i + 1]
        i += 2
    if not (need["--repo-root"] and need["--as-of"] and need["--seven-ac-file"]):
        return None
    return need


def _main(argv):
    if not argv or argv[0] == "selfcheck":
        print(dp_selfcheck())
        print(json.dumps(registered_dp_values(), ensure_ascii=False, indent=1))
        print(json.dumps(registered_param_values(), ensure_ascii=False,
                         indent=1))
        return 0
    if argv[0] != "run":
        sys.stderr.write(_usage() + "\n")
        return 2
    args = _parse_run_args(argv[1:])
    if args is None:
        sys.stderr.write(_usage() + "\n")
        return 2
    try:
        repo_root = _guarded_path(args["--repo-root"])
        default_dir = os.path.join(repo_root, "data", "research",
                                   "p3_final_seal")
        state_path = args["--state-path"] or os.path.join(
            default_dir, "acceptance_journal.jsonl")
        out_dir = args["--out-dir"] or default_dir
        table = json.loads(
            _read_bytes(args["--seven-ac-file"]).decode("utf-8"))
        validate_seven_ac_selfcheck(table)
        write_baseline(state_path, args["--as-of"])
        start_final_acceptance(state_path, args["--as-of"])
        doc = compile_seal_determination(repo_root, state_path, table,
                                         args["--as-of"], out_dir=out_dir)
    except ValueError as exc:
        sys.stderr.write("run 拒绝(纪律违例 fail-loud): %s\n" % (exc,))
        return 1
    nv = sum(1 for row in doc["checklist_verdicts"]
             if row["verdict"] == "NOT_VERIFIED")
    print("终验清单执行完成: 判定=%s(%s)" % (
        doc["determination"], DETERMINATION_LABELS[doc["determination"]]))
    print("观察钟 elapsed=%d/%d 天; FAIL 项=%d; NOT_VERIFIED 项=%d; 清单项=24" % (
        doc["runtime_window"]["elapsed_days_at_as_of"],
        doc["runtime_window"]["window_days"], len(doc["fail_items"]), nv))
    print("产物: %s{acceptance_journal.jsonl, seal_determination.json, "
          "seal_determination.md}" % (out_dir + os.sep,))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
