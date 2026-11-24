#!/usr/bin/python3 -I
"""gen_docs9.py A|B — write the public documents of Audit-R32 into the dev tree from the out/ drafts.

A = evidence + report commit: replay / CI parts say "see the receipt commit".
B = receipt commit: replay / CI parts are read from out/docs_B/*.txt (written by the operator from the
    replay console logs and the CI job listings).
Source of truth: out/r32_report_final.md (placeholders {{CHAIN_TAIL}} {{CI_DOCS}} x2 {{R32_REPLAY_SUMMARY}}
{{REPLAYS}}) and out/r32_evidence_README_final.md. Nothing else is typed in here.
"""
import os
import sys

OUT = '/tmp/r32-accept/out'
REPO = '~/investment-agent-product'
mode = sys.argv[1]
assert mode in ('A', 'B')


def b(name):
    return open(os.path.join(OUT, 'docs_B', name), encoding='utf-8').read().strip()


if mode == 'A':
    rep = {
        '{{CHAIN_TAIL}}': '本提交(证据+报告,纯文档)→ 回执提交(从提交重新下载的重放回执,纯文档)',
        '{{CI_DOCS}}': '见随后的回执提交。',
        '{{R32_REPLAY_SUMMARY}}': ('四包从本证据提交重新下载的重放结果(严格重放/换本地日历/重复重放/缺件与篡改拒绝;'
                                   '最终提交引擎上的拒绝与显式越过)见随后的回执提交(`replays/`)。'),
        '{{REPLAYS}}': 'R32 四包与 R31 三包从本证据提交重新下载的重放结果见随后的回执提交(纯文档提交: `replays/`,并补入本段)。',
    }
else:
    rep = {
        '{{CHAIN_TAIL}}': b('chain_tail.txt'),
        '{{CI_DOCS}}': b('ci_docs.txt'),
        '{{R32_REPLAY_SUMMARY}}': b('replay_summary.txt'),
        '{{REPLAYS}}': b('replays.txt'),
    }
src = open(os.path.join(OUT, 'r32_report_final.md'), encoding='utf-8').read()
for k, v in rep.items():
    assert src.count(k) >= 1, k
    src = src.replace(k, v)
assert '{{' not in src and '}}' not in src, [l for l in src.split('\n') if '{{' in l or '}}' in l][:5]
rd = open(os.path.join(OUT, 'r32_evidence_README_final.md'), encoding='utf-8').read()

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
