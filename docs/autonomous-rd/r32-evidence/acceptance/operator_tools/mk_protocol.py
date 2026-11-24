#!/usr/bin/env python3
"""mk_protocol.py <tag> <out_dir> <min_points> [<extra_check_file>] [<round>]

Write the zero-context review-seat protocol for one R32 acceptance run at the
final code stamp (0f3936d, clean-install tree /tmp/r32-accept/final4; the C4
work order lives on the degraded-install tree).

The protocol carries procedure + artefact paths + output schema + procedural
disclosures only. It must not carry any judgement content or any operator
expectation (seat charter docs/autonomous-rd/SEMANTIC-AUDIT-SEAT.md §1)."""
import datetime
import os
import sys

STAMP = '0f3936dd7eb74c557a2350e400d58e10a09c5139'
TREES = {'C4': '/tmp/r32-accept/final4-degraded'}

tag, out_dir, min_points = sys.argv[1], sys.argv[2], int(sys.argv[3])
extra = open(sys.argv[4], encoding='utf-8').read() if len(sys.argv) > 4 else ''
round_no = sys.argv[5] if len(sys.argv) > 5 else '1'
STAMP = sys.argv[6] if len(sys.argv) > 6 else STAMP
MODE = sys.argv[7] if len(sys.argv) > 7 else 'final'
assert MODE in ('final', 'pre')
FINALITY = ('为本轮验收的最终提交' if MODE == 'final' else
            '为受审运行目录的代码印章(本轮=该印章上的审查;其后如有引擎修复提交,'
            '受审稿将在新印章另行复审)')

env = {}
for line in open('/tmp/r32-accept/env4.sh', encoding='utf-8'):
    line = line.strip()
    if line.startswith('export RD_'):
        k, v = line[len('export '):].split('=', 1)
        env[k] = v.strip('"')
import json
import re

run_dir = env['RD_' + tag]
tree = TREES.get(tag, '/tmp/r32-accept/final4')
today = datetime.date.today().isoformat()


def review196(tag_):
    """Outcome line of the independent review this work order received at the
    superseded stamp 19638e1 (procedural fact only; read from the seat's own
    verdict file). Empty when that work order had no review at 19638e1."""
    p = '/tmp/r32-accept/review3/%s_round1/VERDICT-round1.json' % tag_
    if not os.path.exists(p):
        return ''
    v = json.load(open(p, encoding='utf-8'))
    sev = [i.get('severity') for i in (v.get('items') or [])]
    line = '结论 %s,抽核 %s 点/偏离 %s,MAJOR %d 条' % (
        v.get('verdict'), v.get('recompute_points'), v.get('recompute_mismatches'),
        sev.count('MAJOR'))
    if v.get('verdict') == 'REVISE' and v.get('must_fix'):
        line += ',必修项由研判席修订后才进入本轮(修订脚本与前后对照入验收证据档)'
    return line


def prev_round(tag_, rnd):
    """Outcome line of the previous round of this final-stamp review (round >= 2
    only; procedural fact read from the seat's own verdict file)."""
    if int(rnd) <= 1:
        return ''
    k = int(rnd) - 1
    p = '/tmp/r32-accept/review4/%s_round%d/VERDICT-round%d.json' % (tag_, k, k)
    if not os.path.exists(p):
        raise SystemExit('no verdict file of round %d for %s: %s' % (k, tag_, p))
    v = json.load(open(p, encoding='utf-8'))
    sev = [i.get('severity') for i in (v.get('items') or [])]
    line = '上一轮(Round-%d,同一印章)独立审查结论 %s,抽核 %s 点/偏离 %s,MAJOR %d 条' % (
        k, v.get('verdict'), v.get('recompute_points'), v.get('recompute_mismatches'), sev.count('MAJOR'))
    if v.get('verdict') == 'REVISE':
        line += ',必修项由研判席修订后才进入本轮(修订脚本与前后对照入验收证据档)'
    return line


_r196 = review196(tag)
if tag in ('A', 'B'):
    # was the judgment text changed after the 19638e1 review? (fold output present)
    FOLDED = os.path.exists('/tmp/r32-accept/out/judgment4b_%s.json' % tag)
else:
    FOLDED = False
if int(round_no) > 1 and tag in ('A', 'B'):
    raise SystemExit('round label for A/B is fixed at 1 (their first review is the 19638e1 one)')
PRE = {
    'A': 'A 稿在更早的印章 f722e3c 经一次独立预审(结论 REVISE),必修项由研判席修订;'
         + ('在印章 19638e1 再经一次独立审查(%s)。' % _r196 if _r196 else
            '在印章 19638e1 的独立审查未形成结论档。'),
    'B': 'B 稿另经操作者文本复核(无独立预审);B 稿的早期审查尝试因接口错误中止、未形成裁决;'
         + ('在印章 19638e1 经一次独立审查(%s)。' % _r196 if _r196 else
            '在印章 19638e1 的独立审查未形成结论档。'),
    'T3': 'T3 稿在更早的印章 f722e3c 经一次独立预审(结论 REVISE),必修项由研判席修订后才进入本轮。',
    'N30': 'N30 稿的早期审查尝试因接口错误中止、未形成裁决;此前无预审。',
    'C4': 'C4 稿此前无预审。',
}
if tag in ('A', 'B') and not _r196:
    raise SystemExit('no 19638e1 verdict file for %s: fold that review before the final round' % tag)

_prev = prev_round(tag, round_no)
if _prev:
    PRE[tag] = PRE[tag] + ' ' + _prev + '。'
CARRY = ('研判稿在 19638e1 轮审查中的必修项及研判席采纳的次要项已由研判席修订后进入本轮'
         '(修订脚本与前后对照入验收证据档)，未涉及的判断文字沿用 19638e1 轮。' if FOLDED else
         '研判稿判断文字沿用此前轮次(仅工单轮次标识不同)。')

TEMPLATE = """# 独立语义审查席规程(Audit-R32 正式使用验收,{tag},Round-{round},零上下文)

本文件只含程序、工件路径与程序性披露,不含任何判断内容,也不含开发者期望。
席位性质(章程 docs/autonomous-rd/SEMANTIC-AUDIT-SEAT.md §1): 真独立、无开发树
上下文;席可拒开发者声明(UPHELD 不欠,REVISE 不留情)。数值对错由确定性层负责,
但本席仍须独立复算抽核——报告里的数字若与证据面不符即为 MAJOR。

## 0. 程序性披露(事实陈述,不构成对受审稿的任何评价)

- 受审判断档(agent_judgment.json)由研判席产出(操作者会话经正式入口
  `ia_cli research-one` 代持席位,Agent Native,零付费调用);引擎只供确定性证据。
- 代码印章 {stamp} {finality}。本工单研判稿此前的审查史(程序事实): {pre}
  其他工单研判稿各自的审查史见验收证据档,与本受审稿无关。席位不得索取、推测或依赖任何
  预审内容——本裁决须独立成立;受审稿经过修订不代表它已无问题。
- 印章由 19638e1 变为 {stamp} 的原因(程序事实): 正式入口验收中发现引擎缺陷——官方记录面
  读取格级 `policy_dates`,而规划器把该键写在锚级,导致问及官方政策目标的问句被误判为
  「缺官方记录」草稿;修复只改该读取与对应门测试(提交说明与复现记录入验收证据档)。
  两印章间本工单引擎确定性面(点值格/证据索引/日历)已程序比对逐键一致;本工单在
  {stamp} 上重新规划并重新 attach,{carry}
- 运行目录内 MAP_REPORT.md / FULL_REPORT.md 是裁决缺席状态下的渲染,
  「语义审查(席位待唤起)」是该状态下的预期文字。受审对象=agent_judgment.json 全文
  (l3 / l4 / reader_map / quality_gate_notes / agent_declaration)与读者报告中的判断文字。
- 引擎交付门(blocked_class,如草稿判定)是引擎确定性面,不在本席裁决范围;但判断档
  对相关缺口(缺数/缺官方记录/过期/降级)的披露是否属实,属本席核验范围(见 ⑭)。
- 席位与研判席、操作者之间不得通信;席位只产出下述文件。

## 1. 工单与受审对象(只读)

- 工单原文(逐字): `{run_dir}/question_verbatim.txt`
- 受审运行目录(只读,不得写入任何文件): `{run_dir}`
  - 读者报告: `MAP_REPORT.md`(地图问句读者面)、`FULL_REPORT.md`(完整报告)、`report.md`
  - 判断档(研判席产出,已 attach): `agent_judgment.json`
  - 引擎运行档: `report.json`(较大,用 python 抽取,勿整读)、`evidence_index.json`、
    `views_digest.json`、`AGENT_SEAT_ENVELOPE.json`
  - 冻结输入副本: `root_overlay/config/release_calendar.json`(发布/政策日历)、
    `root_overlay/config/metric_registry.json`、
    `root_overlay/data/daily/research_snapshot_20261123.json`(冻结快照)
- 隔离安装树(只读;git archive 净安装,`CODE_VERSION.json` 印章 {stamp}): `{tree}`
  - 快照同一份: `{tree}/data/daily/research_snapshot_20261123.json`
    (顶层含 research_as_of / facts / series_store / gate_a / quality 等)
- report.json 抽取指针: `run`(question / evidence_gate / frozen_inputs / git_head / ts_utc /
  data_requirements)、`research_plan`(point_values / point_anchors / regions / turning_candidates /
  us_rates_trio / asset_moves / policy_event_clusters / policy_doc_facts / dimension_gaps /
  ex_post_offsets / cutoff / map_question)、`layers.L1_事实层.rows`、
  `agent_judgment.contract_verification`(确定性验证结果,含逐项 verdicts 与 STALE 项)、
  `steps[*].envelope`(S3/S4/S5/S6/S8 等各子命令信封=引擎确定性面)。

## 2. 边界

- 只读复算。可自写脚本做独立计算;**不得**修改运行目录与安装树内任何文件
  (席位自己的脚本与产出只写到 `{out_dir}`)。
- 不得联网;不得运行 `ia_cli.py` 的 plan/attach/report/archive/replay/update 等任何写操作;
  不得调用 `agent_judgment.record_semantic_verdict`(登记由操作席执行)。
- 不得读取: `research_archive/`、树内 `docs/`(含各轮证据与报告)、`/tmp/r32-accept/out/`、
  `/tmp/r32-accept/scripts/`、`/tmp/r32-accept/replay/`、`/tmp/r32-accept/install*`、
  `/tmp/r32-accept/final*`(上列只读安装树本身除外)、其他运行目录、
  `/tmp/r32-accept/review*/` 下除本席产出目录 `{out_dir}` 以外的任何目录、
  `~/investment-agent-product`——这些含操作席/研判席的中间产物,读了即失独立。
- 不得委派子代理;本席亲自完成全部复算。
- 自写脚本放 `{out_dir}/`,用 `/usr/bin/python3 -I <脚本> <路径参数…>` 运行
  (路径作参数传入,不在数据目录内起解释器;需要只读调用树内引擎模块时可用
  `{tree}/.venv/bin/python -I`,同样只读)。

## 3. 复算覆盖要求(最低 {min_points} 点;逐点独立于报告转述——从冻结快照 series_store、
冻结日历、report.json 引擎面直算后,再与报告/判断档文字比对)

① 研究截止日: 报告自称的截止日与快照 research_as_of/target_date 是否一致;报告引用的每个
   观测日/发布日/决议日/生效日与截止日的关系(晚于截止日的观测、发布、决议、生效均不得作为
   可引用证据;历史类比的事后段只能以「事后结果」身份出现并明确标注)。
② 点值锚格: 每个被引用的地区×维度×时点(12个月前/3个月前/最新一期,或工单指定的窗口端点)
   的值/观测日/同比/缺席理由,从 series_store 直算。
③ 同比: 凡称「同比」的数,基期是否为去年同月/同季;基期观测缺席处是否如实标「缺基期/
   不可得」而非用相邻月份替代;「最近有效同比」的月份与数值直算。
④ 政策面: 决议日/生效日/目标值/距离上次调整天数,逐项与冻结日历条目和序列变更日核对;
   「官方目标」「市场报价」「月均值」各口径是否分列且不互相冒充;待生效决定(若有)是否
   与现行有效目标分记。
⑤ 三利率分解与资产月窗(若在场): 名义=实际+盈亏平衡恒等、窗口端点日期与值、变化幅。
⑥ 转折判断与候选面: 前值→后值/窗口/谁先变/跟进或背离的叙述是否与候选面一致,
   「先后」主张是否有相应时间分辨率支撑。
⑦ 传导链各环: 证据级(E1/E2/E3)标注与该环实际证据是否相称,E2/E3 环不得以事实位措辞出现;
   环内数字可回贴引擎面。
⑧ 历史类比(若报告含该节): 候选段/距离/分位/同步性叙述所引数字;当时可知面与事后段的
   划分是否正确;随后 3/6/12 个月结果是否以「事后实际」措辞呈现、是否被表述成预测。
⑨ 情景: 触发条件/证伪阈值/期限是否可观测、是否与截止日读数相容(已触发的触发条件、
   已被证伪的前提不得作为「待验证」情景);两情景是否方向互补而非孤证。
⑩ 总判断/走位/对质表文字与数值的一致性(方向词/单位/精度/「最高」「最低」「回到」类关系词);
   对质表「尚不能区分/支持竞争解释」的判断是否与该行观测一致。
⑪ 诚实缺席项: 报告声明的每个缺口(序列缺席/缺基期/过期/降级)是否属实(序列级证实),
   有无以相邻口径冒充;Gate A 状态是否如实披露。
⑫ 截止日当日标注的日频观测(如有): 是否带时点/口径说明,该说明与快照 research_as_of
   时间戳是否相容。
⑬ 契约验证结果中的非 VERIFIED 项(如 STALE): 判断档是否对相应指标作了披露,披露内容
   (指标/观测期/原因)与引擎面是否一致。
⑭ 交付门相关缺口(如运行存在草稿判定): 判断档与读者报告对缺席格/缺官方记录项/过期项的
   披露是否与序列面、冻结日历一致;有无把缺席写成「无变化」,或把序列值写成官方宣布目标。
{extra}
## 4. 六查+证伪(章程 §4,须主动找反例)

对每条 L3 矛盾陈述与每条机制链: 证据相关性 / 支持度(定性措辞 vs 证据强度)/ 竞争解释
(是否在列且真正竞争,同证据可容纳,非稻草人)/ 反对证据(有无未披露的反向事实)/
结论是否超出证据 / 证伪条件可观测性(被点名的区分指标须在证据面在场,且两解释在其上的
预言方向确实不同)。每条至少做一次「反方攻击」并记录攻击与结果。
历史段同步性(若在场): 同步/分化主张须与引擎地区×维度同步面一致;叙述称同步而面=缺证,
或叙述与面冲突,均为 REVISE 必修。

## 5. 裁决标准

- MAJOR = 数字/日期/方向错或与证据相左;缺基期却给出同比;以相邻口径冒充;事后信息冒充
  当时可知;结论超出证据且无标注;证伪条件不可观测。
- MINOR = 口径/披露可改进但不改变结论;NIT = 行文。
- 零 MAJOR 且无 REVISE 级问题 → **UPHELD**(MINOR/NIT 如实列出,不构成阻断)。
- 存在 MAJOR 或 REVISE 级问题 → **REVISE**,并逐条给出「原句 → 改句」(只改必修句,
  改句须可用证据面数字成立;拿不出成立的改句=证据不足,如实写明)。
- 禁止凭记忆或常识补数: 席位引用的每个数字必须来自上述只读面并写明出处(文件+键)。

## 6. 产出(写到 `{out_dir}/`)

1) `PROSE-round{round}.md`: 复算清单(逐点: 出处键/直算值/报告值/一致与否)+ 六查逐项结论 +
   反方攻击记录 + 问题清单(按 MAJOR/MINOR/NIT)。
2) `VERDICT-round{round}.json`(UTF-8,合法 JSON):
```json
{{
  "seat": "semantic-audit-seat",
  "reviewer": "independent-zero-context-seat-r32-{tag_l}-round{round}",
  "verdict": "UPHELD|REVISE",
  "overall": "UPHELD|REVISE",
  "notes": "裁决依据摘要(中文,含抽核命中/偏离计数与要点;此段将逐字进入裁决档)",
  "items": [{{"severity": "MAJOR|MINOR|NIT", "where": "文件+段落/条目", "note": "问题",
             "original": "原句(MAJOR 必填)", "fix": "改句(MAJOR 必填)"}}],
  "must_fix": ["必修条目(MAJOR)逐条,无则空数组"],
  "counterexamples_sought": ["反方攻击 1: 攻击内容→结果", "…(每条 L3/机制链至少一条)"],
  "recompute_points": 0,
  "recompute_mismatches": 0,
  "mismatch_details": [],
  "audited_at": "{today}"
}}
```
3) 席位自写的复算脚本与中间表(同目录),供操作席复核。
最终回复只需给出: 裁决词、recompute_points / mismatches、MAJOR 条数、两件产出路径。
"""

text = TEMPLATE.format(tag=tag, tag_l=tag.lower(), run_dir=run_dir, tree=tree,
                       out_dir=out_dir, min_points=min_points, extra=extra,
                       round=round_no, stamp=STAMP, today=today, pre=PRE[tag], carry=CARRY,
                       finality=FINALITY)
assert not re.search('g' + 'lm', text, re.I), 'vendor literal in protocol'
assert '19638e1487e1e572' not in text
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, '_protocol.md')
with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('wrote', path, len(text.encode('utf-8')), 'bytes')
