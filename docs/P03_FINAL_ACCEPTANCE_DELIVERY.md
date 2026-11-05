# IA-P03-FINAL-ACCEPTANCE DELIVERY — P0-3 真实端到端验收交付说明(Round 059)

> 包: IA-P03-FINAL-ACCEPTANCE-SEAL(AC-v1.0;合同 sha256=
> `f7f58c9afc4ce1042cbcc823e8d836472f4d74642dd976a20e674451910a3cfb`)
> 基点: BASE-V13=`ecebb6d44da3f64fbbfc1350670973383534f2e0`(origin/main)
> 分支: `dev/p03-final-acceptance`(纯线性零 merge;merge-base(main,HEAD)=BASE-V13 实测)

---

## §一 白名单与改动清单(合同 §零 A 集;M=0/D=0)

| 行 | 文件 | 性质 | 提交 |
|---|---|---|---|
| A1 | `tests/test_p03_final_acceptance.py`(9 用例: T1 真实链锚 4+T2 双端闭合合成 4+T3 档案 round-trip 1) | 验收件 | C1 |
| A2 | `scripts/p03_final_acceptance_run.py`(E2E-B 正式驱动,五环+溯源链留痕) | 验收件 | C1 |
| A3 | `docs/P03_FINAL_ACCEPTANCE_REPORT.md`(§零 运行前登记 C1+§一-§五 如实回填 C2) | 验收件 | C1/C2 |
| A4 | `docs/P03_FINAL_ACCEPTANCE_DELIVERY.md`(本文件) | 交付说明 | C3 |

`git diff --stat ecebb6d..HEAD` = 上表 A 行文件,零生产逻辑改动(M=0);
B1-B5/G 族/基线锁/LIVE/launchd/CI 配置零触碰。

## §二 提交链与运行留痕

- C1 `3171f7a` §零登记+验收件三件(探针/保险核验/D-FA-01..09 先登记后运行)。
- C2 `19ee763` §一-§五 如实回填(E2E-B 正式运行 exit0/E2E-A 重跑零漂移/
  B5③回补/FD-NV-DV 登记/AC 执行席自检)。
- C3(本提交)DELIVERY+证据包 zip 哈希终笔。
- 运行留痕(真实数据只读): `data/daily` 前后 25 文件 sha256 零变化;
  净增 DEV 研究档案 2 件(gitignored,按合同不 commit):
  `data/research/research_archive/query_history/QB-20261105-001.json`
  (**档案登记哈希** sha256=`cbc71860b8e1e2d28af87ceb6f814babb7b20396f9f4bc41eb00e3d822695bd9`)
  与 `data/research/detection_series_2026-06-30_2026-09-30_003.json`
  (sha256=`8d3c631aea78…`;RT 任务档 `03b4fd7d…` 字节不变)。

## §三 CI 预期(AC-05;操作者 CHECKPOINT 面)

- 引擎侧 CI run 派发权在操作者,执行席结构性不可达(U 级,REPORT §0.1 同口径)。
- 本地全量: 69 文件设计形态全绿(67 unittest-form exit0[glm_live=本地
  跳过形态 exit0,对应 CI SKIPPED]+2 脚本形态 exit0[46/0、41/0];
  `05-tests/fullrun-summary.json`)。
- CI 预期: 基线 67(66 exit0+1 SKIPPED)零回归+新增
  `test_p03_final_acceptance`(9 用例)同绿;验收件仅依赖 git 在场件
  (真实注册表 85+`data/daily/japan_20261105.json`),CI 可移植(D-FA-05)。

## §四 证据包与 zip 哈希终笔(AC-06)

- 证据目录: `/tmp/p03-final-evidence/`(01-probe/02-ls-remote-and-design/
  03-e2eb-formal/04-e2ea-rerun/05-tests/06-injections/07-docs-final/
  08-git-forensics/09-result-selfreport;完整 manifest=zip 内 SHA256SUMS)。
- 证据包: `IA-P03-FINAL-ACCEPTANCE-EVIDENCE.zip`(装配时点 TIP=C2
  `19ee763`;成员逐件 sha256 见 zip 内 SHA256SUMS)。
- **zip 整体 sha256(终笔,装配后实测)**:
  `23980e0b935843d750a27b63edb47147f01c3509719791dd83845ccdda7b04f5`
  (107 条目=106 成员+SHA256SUMS/314075 字节;装配时点 TIP=C2 `19ee763`。
  自指豁免沿 B2/R057/R058/B3R 先例: zip 内 DELIVERY 副本=占位版无本终值;
  推送/CI 终态见证据目录 `08-sidecar/final-state.txt`。)
