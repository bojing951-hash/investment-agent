# IA-P0-BASELINE-RESTRUCT-WP-BR DELIVERY — 注册表演进测试基线重构包(B3-案A先行件)交付说明

> 包: IA-P0-BASELINE-RESTRUCT-WP-BR-AC-v1.0 · 分支 `dev/p0-baseline-restruct` · 基线 BASE-BR=5e9fc88650b9d4a483e83b6638cbc984f8e7b514(冻结时 origin/main 尖端)
> 详细 REPORT: `docs/P0_BASELINE_RESTRUCT_REPORT.md`(§零 58 锁清点表/§一三联锁设计登记/§二逐文件摘要/§三电池映射/§四预演双向/§五 p4 双态/§六全量表/§七谱系)
> 证据包: `/tmp/p0-baseline-restruct-evidence/IA-P0-BASELINE-RESTRUCT-EVIDENCE.zip`

## §一 交付清单(What)

- **新增(A 集 k=5,全数)**: `tests/helpers/baseline_locks.py`(三联锁共享助手:T1 冻结下限 81/80/32/82+81 项 vintage 锚机器生成零手抄+基线四采集/五数据通道冻结;T2 实载派生 registry_doc/双射唯一/工件恰覆盖/gate_vintage_ok/sources_status_baseline_ok(复用生产校验器);T3 evolution_legal 四枚举+通道映射核;reset_registry_caches 注入配套)+ `tests/helpers/__init__.py`(包标识)+ `tests/test_p0_baseline_lock_equivalence.py`(等价套件:Z0 对照+N1-N7+ 电池 27 项+R 三态预演,31/31)+ `docs/P0_BASELINE_RESTRUCT_REPORT.md`+ 本 DELIVERY;
- **修改(M 集 28,全数⊆合同白名单,均在 tests/ 树)**: w4 族 5+p01_fix 族 11+w2_fix 族 2+w3 族 5+w5 族 1+清点实证扩充族 3(w1/w1_fix1/w2)+p4 环境敏感 1(逐文件摘要=REPORT §二);
- **删除(D=0)**: 无删除;test 函数数/check 调用数 28/28 只增不减(REPORT §二.1,唯 fix9 43→44 净增);
- **零改动**: 生产代码/配置/数据/.github/workflows 零触碰(注册表 config/metric_registry.json 零改动——演进兼容性以 worktree 副本预演证明,不落地真实演进);LIVE 树零写入;main 零接触。

## §二 实现摘要(How)

三联锁形态(合同 §零规则冻结,REPORT §一登记后实现): **T1 冻结下限**(≥81/≥80/≥32/≥82+`baseline_removals==∅` 集合面)防缩水;**T2 实载派生**(期望值一律自 config/metric_registry.json 实读/生产校验器实调派生,弃字面 81/80/32——M 集 grep 零残留)防腐化;**T3 自洽演进**(新条目 source/日历/单位/通道/status 全登记核)防静默未登记演进。全 active 契约→**vintage 域**(PASS 恒合法;DEGRADED 仅当 core 四桶净且 noncore_missing⊆时点后新增;基线四采集通道任何 vintage 硬 active);sources_status 盲迭代→⊇基线四通道+生产校验器结构域;p4 数据面 fixture 全 tmp 化(环境无关化)。邻接 8 处演进敏感锁经合法 85 预演实证发现后同域化(commit 94c6e84,语义不弱化)。

## §三 测试面(Evidence)

- **等价套件**: `python3 tests/test_p0_baseline_lock_equivalence.py` → **31/31,exit=0**(电池红面全数咬合+恒红防线四处绿面+注入零残留+工作树零污染);
- **演进预演双向**(AC-04): 合法 85→M 集 28 套件零改动全绿(0 红);缩水 84→4 套件红(w1/w1_fix1/w2 artifact 锁+w4);裸 85→w1 加载即 AssertionError——演进不撞墙∧非法必红;
- **p4 双态**(AC-05): ambient 43/0+isolated(detached worktree)43/0,无 @skip;
- **本地全量**(AC-07 前半): 66 文件→65 运行(glm_live 按 CI 同构跳过)→**65 绿/0 红/exit=0**,323s(REPORT §六;基线 63 绿+p4 红→65 全绿,p4 漂移面消除,余零新红);
- **CI dispatch**: 操作者面(执行 Agent 不自行派发;分支已推 origin,待操作者 dispatch+登记)。

## §四 证据包(Assessment 材料)

`IA-P0-BASELINE-RESTRUCT-EVIDENCE.zip` 成员: ①result.md 副本;②REPORT/DELIVERY 终版副本;③等价套件源码副本;④清点表 CSV(58 锁行)+发现程序三源(wpbr_discovery.py/raw.tsv/count.txt+vintage_ids.txt 生成指令);⑤p4 双态脚本+记录;⑥预演三变体 JSON+构造/驱动脚本;⑦全量跑 summary.csv+逐套日志;⑧计数脚本;⑨SHA256SUMS(最后写入)。zip 整体 sha256(装配后实测,自指豁免沿 B1/B2/B4 先例):

```
IA-P0-BASELINE-RESTRUCT-EVIDENCE.zip sha256 = 332b32d0088d99e7b015476d66a3ef59d58024819cdccfb600e88138ec064a61 (86成员/245666字节, 装配后实测,assemble TIP=4a89f22)
```

> 自指豁免: zip 内 DELIVERY 副本(成员③)=终版提交版无上行实测值,固定点不可内含自身哈希;推送终态(最终尖端/最终 ls-remote)见证据目录 final-state.txt(zip 外),B1/B2/B4 同款先例。

## §五 复算指令+漂移维护三要素+映射表(References)

**复算指令**(任一审计者可独立复算):

```
git fetch origin && git checkout dev/p0-baseline-restruct
python3 tests/test_p0_baseline_lock_equivalence.py   # 31/31 exit=0(含三态预演,约150s)
for t in tests/test_*.py; do python3 "$t" >/dev/null 2>&1 || echo "RED: $t"; done  # 除 glm_live 外 0 红
python3 - <<'PY'  # AC-06 面
import subprocess
print(subprocess.run(['git','diff','--name-status',
  '5e9fc88650b9d4a483e83b6638cbc984f8e7b514..HEAD'],
  capture_output=True,text=True).stdout)   # 期望: M28(⊆白名单)+A5+D0
PY
```

**漂移维护三要素**(合同 AC-03⑥):

1. **预期值唯一来源=仓库内版本化锚**: T1 冻结值与 81 项 vintage 锚版本化于 `tests/helpers/baseline_locks.py`(机器生成自 BASE-BR 基线态注册表,生成指令入证据包 discovery/vintage_ids.txt);T2 期望值运行时自 `config/metric_registry.json` 实读派生(单一事实源),零手抄常量;
2. **注册表演进时锁与基线锚同 commit 变更**: 合法演进(B3 81→85)无需改任何 M 文件(预演实证 28/28 绿);仅当**冻结值本身**变更(vintage 锚/下限重冻结,即 B3 重冻动作)时,baseline_locks.py 锚与演进同 commit 更新——单一文件单一事实源,物理集中;
3. **真实数据档永不进入锁域**: 锁域=注册表枚举面+快照结构面,不涉 `data/daily`/`data/research` 内容;p4 套件数据面亦只读提交内 fixture(tests/fixtures/e2e/w4_data 的 tmp 副本),ambient 数据档零依赖。

**电池↔清点回归类映射**: REPORT §三.1(1:1,27 电池项↔58 锁行回归类全覆盖: 缩水×3 面/漏输出/桶和/回显/表行/重复/私货/漏项/映射漂移/基线指标死亡/基线通道死亡/未登记演进×3/通道缺席/枚举缩水/T1 必要性)。

**如实现偏差**: ①电池首跑 N3c/N7b 两处电池自身构造缺陷(live 未接注入/artifact 未传注入 reg)——修正后 31/31,属电池语义自证组成部分(REPORT §三.2);②预演发现 8 处清点表外邻接演进敏感锁,同域化处理并全数登记(REPORT §二,commit 94c6e84)——非弱化,拒绝事实/一致性绑定全保持;③BASE-BR 本地基线态 test_p4_fixes 为 ambient 红(4 红),本包隔离化后全绿——环境面修复非断言弱化(45 check==基线);④无其他偏离,未触发情形(b)/(c)。
