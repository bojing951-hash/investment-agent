# 中国任务 B 可独立重放证据包(Audit-R6 条目5·正式生成器数据全链)

运行: `20261117T083954Z_中国宏观信用与制造业景气_CN_NEW_LOANS_新增贷款与_CN_PMI_M`
(B_run3,引擎 `/tmp/audit_r6/engine`,run_ok=True,四项数据要求 satisfied)。

与 R5 包(`docs/autonomous-rd/cn-task-b-20261117T035814Z/`)的关系: 研究内容
同源(同一冻结市场快照+同一统计口径),**CN 两指标 226 月全史改由 Audit-R6
条目2 正式生成器** `china_market_collector.fetch_macro_history()` 产出(经
`macro_collector.merge_cn_history` 随档 `macro_20261117.json`),R5 临时
addendum 废止;数值与 R5 已独立复核序列**逐位一致**,研究席脚本重放输出与
R5 冻结输出**逐字节一致**(`seat_calc_output.txt`)。

## 输入哈希(全部 sha256)

| 件 | sha256 |
| --- | --- |
| `seat_data/CN_PMI_MFG.json` | `416986c755143a667a59347727c3b68e46e693cb863467117f5e7a08e7f01cbc` |
| `seat_data/CN_NEW_LOANS.json` | `b29707507f5a6ace861d5e6cdfdccd615d17bfc3008384e691772e0634ad992f` |
| `seat_data/FXI.json` | `b4c6ce7ee548e1c5730de5d6d6d9cdca535594b8d31567d3f7823630b49f8eb8` |
| `seat_data/CHINEXT.json` | `f2bab31ea11652762f01c43b9c955f6f5b1a60602d26c33e4786771c2472a1c5` |
| 正式生成器随档 `macro_20261117.json`(Audit-R7 起随包交付: `macro_input/macro_20261117.json`,provenance 完整含 fetched_at/coverage/revision_policy/observation_anchor) | `be1f7680ce7a650e03631b10c6fc4065ed09cf69969cfbcc246a8168ee22c09e` |
| 冻结市场快照 `research_snapshot_20261112_v2.json` | `e2e9152557bd7bb86ca53485069ee1874acf91504c255c541dbd7aec12191769`(与 R5/BLIND 同版) |

## 口径台账

承 R5 包 README 全部口径(月频对齐/重叠窗 2016-12..2026-10 n=119/严格 <50
vs >50 分组,PMI=50.0 持平月 3 个剔除/信用脉冲 CI=12 月滚动和/Welch t+
Mann-Whitney U 双检/防前视公布滞后【假设】),原文见
`docs/autonomous-rd/cn-task-b-20261117T035814Z/README.md`;CN_NEW_LOANS 口径
红线不变=**对实体经济发放的人民币贷款**(社融口径,非全口径)。

## 一条命令重放(空目录)

```sh
mkdir /tmp/cnb_r6 && cd /tmp/cnb_r6 && \
cp <repo>/docs/autonomous-rd/cn-task-b-20261117T083954Z/research_seat_calc.py . && \
cp -R <repo>/docs/autonomous-rd/cn-task-b-20261117T083954Z/seat_data . && \
python3 research_seat_calc.py > replay_out.txt && \
diff replay_out.txt <repo>/docs/autonomous-rd/cn-task-b-20261117T083954Z/seat_calc_output.txt && echo REPLAY OK
```

(脚本以 `__file__` 相对定位 `seat_data/`,不依赖 home//tmp 绝对路径。)

## 独立席复算重放(Audit-R7 R7-03 参数化后,净检出直接可跑)

```sh
cd <repo> && python3 docs/autonomous-rd/cn-task-b-20261117T083954Z/review_seat/recompute_r6b.py && echo "rc=$? OK"
```

rc=0 且 105/105 OK;产物 `review_seat/recompute_replay_out.txt` 与冻结档
`recompute_out.txt` 核心段(汇总行前 162 行)逐行一致——冻结档尾另有席位
当日追加的「反例面扫描补充」段(append-only,不参与机器比对)。
`--seat DIR / --out FILE` 可覆写;任一校验失败脚本以非零退出码结束。

## 判定档 v3 与措辞规约修订

`judgment_mvp_v3.json` = R5 冻结终档同源+一处措辞规约修订(数字零改动):
CON-1 陈述句两处相位边界『PMI<50/>50 信号相位』→『低于/高于荣枯线』,
『两个-23.0%最大跌幅月』→『两个并列样本最大跌幅月』(-23.0% 在 CON-2/CL-3/
L4 原文保留;50 在 basis 与 caliber_notes 保留)。动因=审计基线判定档合同将
相位边界裸 token 与跨资产极值月 token 误绑 CN_PMI_MFG 当期水平(B 族误报类,
引擎侧 RDG-20261116-014 ③ 已修未合入审计基线);措辞避让不改合同。

生产 attach 通过(契约门 VERIFIED 6 检查/0 矛盾/0 未绑/六检 20/20)。

## 独立审查席

- 裁决 **UPHELD**(rev1,零必修): `audit/semantic_review/20261117/
  VERDICT-20261117T083954Z-01.json`(recorded_at=20261117T091337Z,
  content_sha256=06624da711a7fc1332c0015b5720662fa57fb846116becc8c77f6017bbf6437a)。
- 席位自写复算脚本(纯 stdlib,零引用研究席代码):
  `review_seat/recompute_r6b.py`(+`recompute_out.txt`)——105 项数字判定
  全吻合 0 失配: 修订面核验(v3 vs R5 终档 263 叶仅 3 处差异与声明一致,
  数字零变化)/相位统计/40 相关格/极值月归属/数据溯源(seat_data 与
  macro_20261117.json 逐位全等)/合同门复跑一致。
- 归档: `research_archive/20261117T083954Z_…/`(三处一致已核)。
