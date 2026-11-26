#!/usr/bin/python3 -I
"""gen_docs9.py A|B|C — write the public documents of Audit-R32 into the dev tree from the out/ drafts.

A = evidence + report commit (f46fdcb): replay / CI parts say "see the receipt commit".
B = receipt commit: replay / CI parts are read from out/docs_B/*.txt (written by the operator from the
    replay console logs and the CI job listings).
C = Task-3 correction commit: same placeholders, fragments from out/docs_C/*.txt (the replays redone
    from this commit and its CI / battery are reported by the receipt commit that follows).
Source of truth: out/r32_report_final.md (placeholders {{CHAIN_TAIL}} {{CI_DOCS}} {{R32_REPLAY_SUMMARY}}
{{REPLAYS}} {{C_BATTERY}} {{C_REF}}) and out/r32_evidence_README_final.md. Nothing else is typed in here.
"""
import os
import sys

OUT = '/tmp/r32-accept/out'
REPO = '~/investment-agent-product'
mode = sys.argv[1]
assert mode in ('A', 'B', 'C')

NAMES = ('chain_tail', 'ci_docs', 'replay_summary', 'replays', 'c_battery')
PLACEHOLDER = {'chain_tail': 'CHAIN_TAIL', 'ci_docs': 'CI_DOCS', 'replay_summary': 'R32_REPLAY_SUMMARY',
               'replays': 'REPLAYS', 'c_battery': 'C_BATTERY'}


def b(name, sub):
    return open(os.path.join(OUT, sub, name + '.txt'), encoding='utf-8').read().strip()


if mode == 'A':
    rep = {
        '{{CHAIN_TAIL}}': '本提交(证据+报告,纯文档)→ 回执提交(从提交重新下载的重放回执,纯文档)',
        '{{CI_DOCS}}': '见随后的回执提交。',
        '{{R32_REPLAY_SUMMARY}}': ('四包从本证据提交重新下载的重放结果(严格重放/换本地日历/重复重放/缺件与篡改拒绝;'
                                   '最终提交引擎上的拒绝与显式越过)见随后的回执提交(`replays/`)。'),
        '{{REPLAYS}}': 'R32 四包与 R31 三包从本证据提交重新下载的重放结果见随后的回执提交(纯文档提交: `replays/`,并补入本段)。',
    }
else:
    sub = 'docs_C' if mode == 'C' else 'docs_B'
    rep = {'{{%s}}' % PLACEHOLDER[n]: b(n, sub) for n in NAMES}
    rep['{{C_REF}}'] = b('c_ref', sub)


def fill(text, strict):
    for k, v in rep.items():
        # the report carries every placeholder; the README only the correction-commit reference
        assert k in text or not strict, k
        text = text.replace(k, v)
    return text


src = fill(open(os.path.join(OUT, 'r32_report_final.md'), encoding='utf-8').read(), True)
assert '{{' not in src and '}}' not in src, [l for l in src.split('\n') if '{{' in l or '}}' in l][:5]
rd = fill(open(os.path.join(OUT, 'r32_evidence_README_final.md'), encoding='utf-8').read(), False)
assert '{{' not in rd and '}}' not in rd

# public-document scan: no home root, no model-vendor word (word list stays outside the repository)
words = []
for line in open('/tmp/r32-accept/vendor_cn.txt', encoding='utf-8'):
    line = line.strip()
    if line and not line.startswith('#'):
        words.append(line.split('=>')[0].strip())
for name, text in (('report', src), ('readme', rd)):
    hits = {w: text.count(w) for w in words if text.count(w)}
    print(name, 'chars', len(text), 'lines', text.count('\n'), 'home_root', text.count('~'), 'vendor_word_hits', hits)
    assert not hits and '~' not in text, name

open(os.path.join(REPO, 'docs/autonomous-rd/AUDIT_R32_REPORT.md'), 'w', encoding='utf-8').write(src)
open(os.path.join(REPO, 'docs/autonomous-rd/r32-evidence/README.md'), 'w', encoding='utf-8').write(rd)
print('written mode', mode)
