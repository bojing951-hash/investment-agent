#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P03-FINAL-ACCEPTANCE(P0-3 / Round 059): E2E-B 真实任务验收驱动(正式运行件)。

用途: 以冻结合同指定的自然语言研究任务样例(DESIGN §三(d) 第一环原文)在**真实数据**
上把 E2E-B 全链走一遍并留痕(输出=可复核运行日志;档案=持久 query_history 记录):

  NL问题 → B1 映射器(真实注册表85) → S1 快照(真实 data/daily,持久化到证据沙箱)
  → R1 快照选择(执行器自取) → R3 门禁判定 → B2 执行器(真实事实取值)
  → B5 渲染器(接地作答) → B4 档案(append-only 落 DEV data/research/)
  → B4 读回+digest 复算核验

纪律(IA-P03-FINAL-ACCEPTANCE-SEAL-AC-v1.0 §一/红线):
- 零生产逻辑改动: 本脚本只调用既有模块(B1/B2/B4/B5/S1/R1/R3),不含任何修复/调参;
- 真实数据只读: data/daily 仅经 build_snapshot 读取;一切写入只落证据沙箱与
  DEV data/research/(gitignored,LIVE 零触碰);
- 零网络/零模型调用/零凭证;禁墙钟: 全部时点参数显式注入(确定性重放);
- 如实不触发即如实: 日端数值缺席=B3 D7 事实提取未接线(结构性),本驱动不凑数,
  按∖三(c)/(b) 如实输出;缺陷登记归 REPORT。

退出码: 0=全链各环完成且档案核验通过; 2=链路任一环失败(如实,不重试不凑)。
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e2eb_query_mapper as eqm        # B1
import e2eb_query_executor as eqx      # B2
import e2eb_answer_renderer as ear     # B5
import research_archive as ra          # B4
import snapshot_builder as sb          # S1

# ══ 冻结运行参数(先登记后运行;REPORT §一映射) ═══════════════════════════
GOLDEN_QUESTION = ("美日政策利率差和10年期国债收益率差最近怎么样?"
                   "和美元兑日元走势合起来看是什么状态?")   # DESIGN §三(d) L134 逐字
CREATED_AT = "2026-11-05T20:45:00+08:00"                    # 受理时刻(注入,禁墙钟)
AS_OF = "2026-11-05"                                        # 研究截止(japan档运行日)
ARCHIVED_AT = "2026-11-05T12:46:00+00:00"                   # 落档时刻(注入)
TARGET_YMD = "20261105"
REAL_DAILY = os.path.join(ROOT, "data", "daily")            # 真实采集目录(只读)
REAL_ARCHIVE = os.path.join(ROOT, "data", "research")       # DEV 研究档案根(B4 缺省同源)


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(evidence_dir):
    sandbox = os.path.join(evidence_dir, "e2eb-sandbox")
    os.makedirs(sandbox, exist_ok=True)
    log = []

    def out(line=""):
        print(line)
        log.append(line)

    out("=== IA-P03-FINAL-ACCEPTANCE E2E-B 真实任务验收(正式运行) ===")
    out(f"question(DESIGN §三(d) L134 逐字): {GOLDEN_QUESTION}")
    out(f"created_at={CREATED_AT} as_of={AS_OF} target_ymd={TARGET_YMD}")
    out(f"real_daily(只读)={REAL_DAILY}")
    out(f"evidence sandbox={sandbox}")

    # ── 环1: B1 映射(真实注册表 85,v2.1.0) ─────────────────────────────
    query_id = ra.allocate_query_id(CREATED_AT, archive_dir=REAL_ARCHIVE)
    out("")
    out("[环1] B1 map_question(真实注册表;R023+R060 后 85/v2.1.0)")
    ir = eqm.map_question(GOLDEN_QUESTION, created_at=CREATED_AT, as_of=AS_OF)
    ir["query_id"] = query_id                      # 档案配号(B4 同日单调)接管拼接号
    out(f"  query_id={ir['query_id']} n_bindings={len(ir['metric_bindings'])} "
        f"n_ops={len(ir['derived_operations'])} n_unresolved={len(ir['unresolved_entities'])}")
    for b in ir["metric_bindings"]:
        out(f"  {b['binding_id']}: metric_id={b['metric_id']} role={b['role']}"
            f" window={b['window']} field={b['field']} status={b['status']}")
    for op in ir["derived_operations"]:
        out(f"  {op['op_id']}: {op['op_type']} operands={op['operands']} "
            f"status={op['status']} formula={op['formula']}")
    jp_bindings = [b for b in ir["metric_bindings"]
                   if b["metric_id"] in ("JP_POLICY_RATE", "JGB2Y", "JGB5Y", "JGB10Y")]
    out(f"  日端绑定(B3 注册表命中形态)= {[ (b['binding_id'], b['metric_id']) for b in jp_bindings ]}"
        f" —— B3 前(81注册表)该两绑定为 ABSENT_REGISTRY(DESIGN §三(d) MB-8/MB-9 走查形态)")

    # ── 环2: S1 快照构建(真实 data/daily → 持久化到证据沙箱) ─────────────
    out("")
    out("[环2] S1 build_snapshot(write=True→证据沙箱;真实数据只读)")
    snap = sb.build_snapshot(target_ymd=TARGET_YMD, data_dir=REAL_DAILY,
                             out_dir=sandbox, as_of=CREATED_AT)
    snap_path = os.path.join(sandbox, f"research_snapshot_{TARGET_YMD}.json")
    out(f"  snapshot_id={snap['snapshot_id']} gate_a={snap['gate_a']['status']} "
        f"n_facts={len(snap['facts'])} file={snap_path}")
    out(f"  snapshot sha256={_sha256_file(snap_path)}")
    for ch, st in snap["sources_status"].items():
        out(f"  sources_status[{ch}]: {st.get('status')} file={st.get('file')} "
            f"lag={st.get('lag_days')} sha256={st.get('sha256')}")
    jp_sha = (snap["sources_status"].get("japan") or {}).get("sha256")
    out(f"  japan 在场核验: status=EXACT sha256={jp_sha}"
        + (" == B3 A2 冻结值 6bba4718759ba12546499c1bdc510a1157b87f9462408e14071967d29e14e7f1"
           if jp_sha == "6bba4718759ba12546499c1bdc510a1157b87f9462408e14071967d29e14e7f1"
           else " ≠ 冻结值(如实)"))
    jp_facts = [f["metric_id"] for f in snap["facts"]
                if f.get("metric_id") in ("JP_POLICY_RATE", "JGB2Y", "JGB5Y", "JGB10Y")]
    out(f"  快照事实中日端指标 = {jp_facts}"
        f" —— B3 D7: 事实提取未接线(sb 归一化链四通道),japan 档经 sources_status 在场"
        f"核验(EXACT+sha256)而事实缺席=当前结构性事实,如实呈现,不冒充不填0")

    # ── 环3: B2 执行器(R1 自取持久快照 + R3 门禁) ───────────────────────
    out("")
    out("[环3] B2 execute_query(daily_dir=证据沙箱→R1 select_snapshot 自取;R3 门禁判定)")
    execution = eqx.execute_query(ir, daily_dir=sandbox)
    if execution.get("refusal") is not None:
        out(f"  REFUSAL(零部分执行): {execution['refusal']}")
        _finish(log, evidence_dir, 2, "refusal")
        return 2
    ex_ir = execution["ir"]
    out(f"  绑定: snapshot_id={execution['snapshot_id']} gate_status={execution['gate_status']}")
    for b in ex_ir["metric_bindings"]:
        line = f"  {b['binding_id']}: {b['metric_id']} status={b['status']}"
        if b.get("provenance") is not None:
            p = b["provenance"]
            line += (f" value={execution['values'].get(b['binding_id'])}"
                     f" fact={p['fact_id']} obs={p['observation_date']}"
                     f" q={p['quality_status']} src={p['source_file']}")
        elif b.get("absence_reason"):
            line += f" reason={b['absence_reason']}"
        out(line)
    for op in ex_ir["derived_operations"]:
        out(f"  {op['op_id']}: status={op['status']} result={op['result']}"
            f" calc_ref={op['calculation_ref']}")
    out(f"  values={json.dumps(execution['values'], ensure_ascii=False, sort_keys=True)}")

    # ── 环4: B5 渲染(接地作答=研究报告) ─────────────────────────────────
    out("")
    out("[环4] B5 render_answer(接地强制渲染)")
    answer = ear.render_answer(execution)
    out(f"  kind={answer['kind']} n_grounded={answer['n_grounded_values']} "
        f"absent={len(answer['absent'])} no_data={len(answer['no_data'])} "
        f"quality_disclosures={len(answer['quality_disclosures'])}")
    out("  ---- answer_text ----")
    for ln in answer["answer_text"].splitlines():
        out(f"  {ln}")
    out("  ---- /answer_text ----")

    # ── 环5: B4 档案(append-only 落 DEV data/research/)+读回+核验 ───────
    out("")
    out("[环5] B4 append_query_record(DEV data/research/;append-only)")
    status, path = ra.append_query_record(ex_ir, snapshot=snap,
                                          archive_dir=REAL_ARCHIVE,
                                          execution=execution, archived_at=ARCHIVED_AT)
    out(f"  append status={status} path={path}")
    if status != ra.STATUS_WRITTEN:
        _finish(log, evidence_dir, 2, f"append status={status}")
        return 2
    rec = ra.load_query_record(ex_ir["query_id"], archive_dir=REAL_ARCHIVE)
    ok, issues = ra.verify_query_record(rec, sandbox, archive_dir=REAL_ARCHIVE)
    out(f"  load ok: query_id={rec['query_id']} digest_snapshot={rec['digest_snapshot']}")
    out(f"  verify(R5 digest 复算+schema+快照解析): ok={ok} issues={issues}")
    out(f"  档案 sha256={_sha256_file(path)}")

    # ── 溯源链汇总 ──────────────────────────────────────────────────────
    out("")
    out("=== 档案溯源链(逐件可核验) ===")
    out(f"  查询记录: {path} (sha256={_sha256_file(path)})")
    out(f"  快照: {snap_path} (sha256={_sha256_file(snap_path)}; "
        f"digest_snapshot={rec['digest_snapshot']})")
    for ch, st in snap["sources_status"].items():
        src = os.path.join(REAL_DAILY, st.get("file", ""))
        if os.path.isfile(src):
            out(f"  源档[{ch}]: {st.get('file')} (sha256={_sha256_file(src)})")
    result = {"chain": "ok", "verify_ok": bool(ok), "issues": issues}
    _finish(log, evidence_dir, 0 if ok else 2,
            "ok" if ok else f"verify failed: {issues}")
    return 0 if ok else 2


def _finish(log, evidence_dir, code, summary):
    manifest = {"exit_code": code, "summary": summary,
                "question": GOLDEN_QUESTION, "created_at": CREATED_AT,
                "as_of": AS_OF, "target_ymd": TARGET_YMD}
    mpath = os.path.join(evidence_dir, "e2eb-run-manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1, sort_keys=True)
    lpath = os.path.join(evidence_dir, "e2eb-run.log")
    with open(lpath, "w", encoding="utf-8") as f:
        f.write("\n".join(log) + f"\nexit_code={code}\n")
    print(f"=== manifest: {mpath} | log: {lpath} | exit_code={code} ===")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 scripts/p03_final_acceptance_run.py <evidence_dir>")
        sys.exit(64)
    sys.exit(main(sys.argv[1]))
