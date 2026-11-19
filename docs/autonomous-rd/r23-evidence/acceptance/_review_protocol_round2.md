# 独立语义审查席规程(Audit-R23 一问验收,Round-2 修订复核,零上下文)

本文件只含程序与工单原文,不含任何判断内容。

- 工单原文(run.question 逐字,Round-1 规程所载文本系操作席转录错误,以本版为准——
  可用 `python3 -c "import json,glob;print(json.load(open(glob.glob('/tmp/r23/output/r23map/20261119T173248Z_*')[0]+'/report.json'))['run']['question'])"` 自核):
  给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 受审运行目录: /tmp/r23/output/r23map/20261119T173248Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最
- 隔离树: /tmp/r23(CODE_VERSION.json 印章 git_head=b316e88…,report.run 同值)
- Round-1 裁决: RD/verdicts/VERDICT-round1.json(REVISE,1 MAJOR/3 MINOR/4 NIT,307 点)
  — 先完整读它,再开始。

## 边界(与 Round-1 相同)

只读复算(可运行树内脚本/引擎公开接口做独立计算,但不得修改 run 目录任何受审文件、
不得改引擎代码、不得联网、不得读 research_archive/ 旧档、不得读 /tmp/r23v、
不得调用 record_semantic_verdict)。你的产出只写 RD/verdicts/ 下两件:
VERDICT-round2.json 与 PROSE-round2.md。

## Round-2 复核范围

### A. 修订项核验(逐项,以 Round-1 裁决为准)

1. MAJOR-1(SCN-A 阈值日期-数值错配): 受审件应为『2026-11-17 的 2.21』或
   『2026-11-18 的 2.19』二者之一且全源一致(MAP 情景表/report.md/
   agent_judgment 三处)。独立从快照 BEI_10Y 序列复算两日之值再对。
2. MINOR-1(近30日窗起点披露): 新披露的起点日与起点值须与快照一致
   (TIPS_10Y/BEI_10Y 各自回溯30日首个观测日)。
3. MINOR-2(年内→研究窗内口径): 表述与序列事实一致(研究窗 2025-11 起;
   序列全域 2025-10→2026-02 的 -1.72pp 不得被『研究窗内』表述覆盖错)。
4. NIT-1(双前缀): 渲染后不得再出现『因果假设: 因果假设: 』『竞争解释: 竞争解释: 』。
5. NIT-3(ECB 括号两跳): 若补数值,2.0→2.25(2026-06-11)→2.5(2026-09-10)
   须与引擎政策面逐值一致;若去数值留文字,文字不得与政策面矛盾。
6. 已知留档项(不得作为新发现重提,但须确认修订未使其恶化):
   NIT-2(区分指标观测 pct 分支缺右括号)与 NIT-4(对照表指标名双括号叠套)
   系渲染器模板缺陷,操作席将在验收后收口提交修复,受审 MAP 保留原样属预期。
   MINOR-3 系操作席规程转录错误,与受审件无关。

### B. 回归抽样(最低 60 点,独立复算,不得转述 report.json)

从快照 series_store 与引擎接口直算,覆盖:
- 锚格抽样: 四地区×三维度×三锚各抽至少一格(值/日期/缺席理由);
- 三利率分解双窗恒等(97/104/-7 与 1/15/-14)重算一遍;
- 政策面一年窗净变动(Fed 先降后升净0;ECB 两跳;日本月均口径);
- 资产月窗抽 2 项(SPX、GOLD_F 或 VIX)两端值;
- 历史类比抽 1 段的逐窗并列 3 格;
- 总判断/情景阈值抽 3 个数字。

### C. 判据

- 零 MAJOR → UPHELD;仍有 MAJOR → REVISE(列明)。
- MINOR/NIT 新发现照列,不阻断 UPHELD,但须给序列级证据。

## 产出格式

VERDICT-round2.json 字段与 Round-1 相同(seat/reviewer/verdict/items/
recompute_points/audited_at),reviewer='independent-zero-context-seat-round2'。
PROSE-round2.md 为人读版。结束时报: 裁决词、复算点数、计数(MAJOR/MINOR/NIT)、
逐项修订核验结论(A1-A6)、回归抽样清单。
