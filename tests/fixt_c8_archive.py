"""Charter8 CI 自足 fixture: 合成研究归档(QB 链)构造器(根因A热修,2026-11-11)。

背景: 主CI 42850982644 干净检出——真实 data/research/ 不入库(入库纪律),
test_charter8_edges/test_charter8_workbench 原直读真实 QB 档 → CI 必挂。
本模块按 research_archive 公开写入 API(allocate_query_id/append_query_record/
write_research_full)在 tmpdir 合成最小归档,使"边必挂 QB 号"与页④档案行
核验逻辑在 fixture 上完整执行;真实档核验由调用方在档在场时条件执行,
缺席时显式 SKIP(不静默)——禁止为过 CI 往库里塞真实 data 档。

fixture 覆盖: config/transmission_edges.json 引用的 QB-20261110-022/-023
(同日单调配号推号);-022 带 research_full sidecar(answer_text 含真实
QB-022 抽核用的四行 r 表格原文,防抄录漂移核验在 CI 可跑);-023 sidecar
无 answer_text(follow_up_of→022,验'关联前档'链与'研究正文=—'如实)。
"""
import copy
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.join(os.path.dirname(_HERE), 'scripts')
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import research_archive as ra   # noqa: E402
import research_provenance as rp  # noqa: E402

# 合成快照(SNAP_A 形状同源 test_p03_e2eb_b4;数值虚构)
FIX_SNAP = {
    "snapshot_id": "research_snapshot_20261110",
    "target_date": "20261110",
    "gate_a": {"status": "PASS"},
    "facts": [{"metric_id": "VIX", "value": 15.0,
               "observation_date": "2026-11-09", "unit": "index_point",
               "quality_status": "PASS"}],
}

# IR 骨架(test_p03_e2eb_b4 IR_M 同款最小合法结构;stage=mapped)
FIX_IR_BASE = {
    "query_id": None,                      # 由 allocate_query_id 填
    "created_at": "2026-11-10T09:00:00+08:00",
    "mode": "B",
    "question_text": None,                 # 调用方填
    "as_of": None,
    "target_snapshot_id": None,
    "metric_bindings": [
        {"binding_id": "MB-1", "metric_id": "VIX", "role": "level",
         "window": None, "field": "value", "status": "PENDING_EXECUTION",
         "absence_reason": None, "provenance": None},
    ],
    "derived_operations": [],
    "unresolved_entities": [],
    "answer_constraints": {"grounding_required": True,
                           "no_data_policy": "report_absence"},
}

# QB-022 sidecar answer_text 抽核行(与真实归档 QB-20261110-022 answer_text
# 内四行逐字一致——字符串已在 test_charter8_edges 原文锁定,此处同源复用)
FIX_ANSWER_ROWS = (
    '| VIX×SPX | −0.7138',
    '| DXY×GOLD_F | **−0.3935',
    '| TIPS_10Y×UST_10Y | +0.8278',
    '| EURUSD×UST_10Y | −0.0307',
)

Q22 = 'QB-20261110-022'
Q23 = 'QB-20261110-023'


def build_archive(archive_dir):
    """在 archive_dir 内合成 QB-20261110-022/-023(+sidecar);返回 archive_dir。

    全部经公开写入 API 落档(schema 校验/同日单调校验/digest 由 append 内部
    真实执行,不绕过归档纪律)。编号取真实档同款 022/023(与边表引用一致);
    空档写入 seq=22/23 满足 append 同日单调(seq>现存max)——ir.query_id 由
    调用方注入是 b4 同款契约(_ir_with_qid 先例)。
    """
    created = FIX_IR_BASE["created_at"]

    def mk_ir(qid, question):
        ir = copy.deepcopy(FIX_IR_BASE)
        ir["query_id"] = qid
        ir["question_text"] = question
        return ir

    long_q23 = ('跨资产传导机制在近零渠道上的可移植性质询(长问题fixture): '
                + 'QE起点与加息起点的机制结论在当前周期是否仍然有效,'
                + '抑或属不可移植结论?(合成fixture长问题,验页④摘要截断纪律≤81字符)')
    status, _ = ra.append_query_record(
        mk_ir(Q22, '全球金融传导矩阵: 强渠道与近零渠道分别是哪些?'),
        snapshot=copy.deepcopy(FIX_SNAP), archive_dir=archive_dir,
        archived_at='2026-11-10T10:00:00+00:00')
    assert status == ra.STATUS_WRITTEN, status
    status, _ = ra.append_query_record(
        mk_ir(Q23, long_q23),
        snapshot=copy.deepcopy(FIX_SNAP), archive_dir=archive_dir,
        archived_at='2026-11-10T11:00:00+00:00')
    assert status == ra.STATUS_WRITTEN, status

    digest = rp.digest_snapshot(FIX_SNAP)
    base_full = {
        "record_type": "research_full_v1",
        "query_id": None,
        "question_text": None,
        "created_at": created,
        "research_as_of": "2026-11-10T18:00:00+08:00",
        "snapshot_id": FIX_SNAP["snapshot_id"],
        "digest_snapshot": digest,
        "status": "answered",
        "answer_text": None,
        "values": None,
        "unresolved": None,
        "model": None,
        "warnings": [],
        "violations": [],
        "user_note": None,
        "follow_up_of": None,
        "saved_at": "2026-11-10T19:00:00+00:00",
    }
    coll = ra._collection_dir(archive_dir)
    full022 = dict(base_full, query_id=Q22,
                   question_text='全球金融传导矩阵: 强渠道与近零渠道分别是哪些?',
                   answer_text='| 指标对 | r |\n' + '\n'.join(FIX_ANSWER_ROWS)
                   + '\n(合成fixture;四行r值与真实QB-022归档逐字同源)')
    st, _ = ra.write_research_full(coll, full022)
    assert st == ra.STATUS_WRITTEN, st
    full023 = dict(base_full, query_id=Q23, question_text=long_q23,
                   status='saved_without_answer', answer_text=None,
                   follow_up_of=Q22)
    st, _ = ra.write_research_full(coll, full023)
    assert st == ra.STATUS_WRITTEN, st
    return archive_dir
