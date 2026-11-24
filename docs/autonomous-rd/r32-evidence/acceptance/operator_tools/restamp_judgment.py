#!/usr/bin/env python3
"""restamp_judgment.py <in judgment.json> <out judgment.json> <old run id> <new run id>

Audit-R32: re-bind a research-seat judgment to the work order of the same
question re-planned at the final code stamp. The judgment content is evidence
driven (engine faces); when the faces of the new work order are identical to
the previous stamp's, the only difference is the work-order round id written
by the builders into agent_declaration.produced_by (a label argument).
This script replaces exactly that label and nothing else:
  - asserts the old id occurs exactly once in the whole JSON text and only
    inside agent_declaration.produced_by;
  - asserts the new id occurs nowhere in the input;
  - writes the output with the engine's own JSON formatting;
  - exits 3 if the content differs anywhere else (compared after undoing the
    label swap).
optional: --written-at <iso8601>  — two judgments carry
agent_declaration.written_at (when the seat wrote them). A judgment cannot
carry a writing time earlier than the work order round it cites, so the
re-stamp sets written_at to the real time of the re-stamp (one label field,
asserted to be the only other change).
"""
import json
import sys

args = sys.argv[1:]
written_at = None
if '--written-at' in args:
    i = args.index('--written-at')
    written_at = args[i + 1]
    del args[i:i + 2]
src, dst, old, new = args[:4]
text = open(src, encoding='utf-8').read()
if text.count(old) != 1:
    raise SystemExit('old id occurrences = %d (expected 1)' % text.count(old))
if new in text:
    raise SystemExit('new id already present in input')
d = json.loads(text)
pb = d['agent_declaration']['produced_by']
if pb.count(old) != 1:
    raise SystemExit('old id is not in produced_by')
d['agent_declaration']['produced_by'] = pb.replace(old, new)
back = json.loads(json.dumps(d, ensure_ascii=False))
back['agent_declaration']['produced_by'] = pb
if written_at is not None:
    if 'written_at' not in d['agent_declaration']:
        raise SystemExit('no written_at field to re-stamp')
    d['agent_declaration']['written_at'] = written_at
    back['agent_declaration']['written_at'] = json.loads(text)['agent_declaration']['written_at']
if back != json.loads(text):
    raise SystemExit(3)
with open(dst, 'w', encoding='utf-8') as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2)
    fh.write('\n')
print('restamped %s -> %s | written_at: %s | produced_by: %s'
      % (src, dst, d['agent_declaration'].get('written_at'), d['agent_declaration']['produced_by']))
