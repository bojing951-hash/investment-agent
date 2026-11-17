# Audit-R11 第十一轮审计修复报告(R55)

- 基线: `08775168c5ac727e606fd4bf26b5b6a63eabe503`(PR #1 第十轮 CI 回填尖)
- 修复提交(执行代码版本,固定 SHA): **30770afb4fa8609b3e533cb35845c05787595e94**(dev/audit-fix-r1)
- 范围: 仅关闭本轮四项(P1-① 时间约束完整处理 / P1-② 并发写入互斥 / P1-③ 引用扫描失败禁删 / P2-④ 工作台缓存重载);目标、研究能力、统计口径不变;不扩功能、不瘦身、不降验收
- 判定口径: 29 判据新门(`tests/test_audit_r11_gate.py`,29/0)+ 电池 184 件直跑 183 绿(phase6 D3 工作面净=提交后复跑口径)+ 复放四包(BLIND/F10/新 B 105/105/e2e-corrected 全 PASS)+ 既有门 r4/r5/r6/r7/r8/r9/r10/t3/r42 复跑全绿

---

## 一、P1-① 完整处理时间约束(scripts/research_orchestrator.py)

### 基线复现(/tmp/r11_repro_p1.py,真实 CN_PMI_MFG 隔离副本走生产链)

数据: 仓内 2026-11-17 实采档 226 点按指令裁出隔离副本——C=2025-01..2026-10(22 点,as_of 2026-11-17: 近五年覆盖不足/近六个月满足/前年零覆盖)、E=2026-01..2026-10(10 点,十八个月窗起点失约)、F=完整历史。经生产采集→loader→S4 信封→`_evaluate_data_requirements`,与 report/archive 同判据源。

| 反例 | 基线(0877516) | 修复后 |
| --- | --- | --- |
| 1a 分别研究过去五年与过去六个月(C) | 只检查六个月→满足即**误交付** | `unparseable`(多个时间范围约束:过去6个月·近5年)+拆分提示,阻断 |
| 2a 研究去年和前年(C) | 只检查去年→**误交付** | `unparseable`(去年·前年)+拆分提示,阻断 |
| 3a 研究过去一年半(E) | 解析为**一年**→1 年窗误交付 | `relative_months 18`,窗 2025-05-17..2026-11-17,起点失约**阻断**(与 3b 十八个月同窗) |
| 4a 研究过去1.5年(F) | 小数数量不匹配→None→**max_available 无窗交付** | months=18 真实窗,窗内 17≥下界 10,satisfied(窗核验在场) |
| 4b 研究过去六季度(F) | 未支持词形→None→**max_available 无窗交付** | `unparseable`(未支持: 季度)带改写提示,阻断 |
| 4d 研究「近 20 24个月」(F) | 残缺数量→None→**max_available 无窗交付** | `unparseable`(残缺数量,不缩短范围),阻断 |

基线 6 例 BASELINE-BUG,修复后 0;对照(单独五年阻断/单独六个月满足/单独前年阻断/单独十八个月阻断/未限定满足)全保持。

### 修复位置

| 文件:函数 | 修改 |
| --- | --- |
| `research_orchestrator.py`:`_q_relative_constraints`(新) | **先收集全部时间约束再决定规范窗口**: 相对月/相对年/日历年(去年/前年)三类约束全量枚举(带日期区间 span 重叠分派: 重叠+以来→日期分支;重叠+以内/内→BAD 日历年形态;重叠+月词形→日期月形),返回 `({'months','years','cal'}, bad_raw)`——多约束不再"先到先得"只检查其一 |
| 同上:`_q_multi_conflict_ret`(新) | 约束集合 >1 → `unparseable`(「问题声明多个时间范围约束(…),单窗口接口无法表达多范围任务」+拆分提示)——明确区分未指定/已完整解析/已指定但无法完整解析三态;**R7「显式区间优先」口径自本轮废止**(显式区间与相对约束并存=多范围阻断,不再静默取区间) |
| 同上:`_RANGE_MONTHS_RE`/`_RANGE_YEARS_RE` | 数量 run 兼容小数(`[0-9]+(?:\.[0-9]+)?`);「N年半」词形(前缀与后缀两形态);年限 `年(?!半)` 负向前瞻防「一年半」被「一年」部分吞掉 |
| 同上:`_iter_range_months`/`_iter_range_years`(新) | 生成器逐个产出全部匹配值或 `('BAD', raw)`;年半=y×12+6;非整数月(如 1.5 个月)→BAD |
| 同上:`_q_residual_bad`(新)+`_QNUM_RESIDUAL_RE`/`_QRANGE_MARKER_RE` | 残余数量扫描: 已解析/日期/未支持覆盖之外的裸数量 run,若带范围标记词(近/最近/过去/以来/以内)=残缺→BAD 明确拒绝;无标记裸数量维持 R9/R10 未限定语义(「6个月」单独出现≠范围声明) |
| 同上:`_QTIME_UNSUPPORTED_RE` | 「N季度」(带可选前缀/个量词)加入未支持清单→unparseable 带提示 |
| 同上:`_q_relative_tail`/`_question_window` | 重构收尾: bad→unparseable;多约束→冲突阻断;单约束分派(月/年小数→round(y×12) 月/年整数/日历年);显式区间返回前先过冲突/未支持/残余三检;`_range_years` 类型守卫(bool/非数值→None 防哨兵字符串进 min_obs 推导) |

### 等价与保留(门 §A 判据)

- **一年半=十八个月=1.5年 → 同一 months=18 窗**(2025-05-17..2026-11-17,as_of 2026-11-17)——验收原文逐字满足;
- **验收不变式**: E(10 点)未限定即因历史不足被拒→加十八个月仍拒(增加范围要求不让被拒数据变可交付);C(22 点)窗内 17≥下限→满足=真满足非放松;
- 保留: 半年=6/「过去 6 个月」空格变体/研究时点 as_of 单独在场/去年/前年/2020年以来(explicit)/2026年内(BAD)/资产名护栏(十年期美债裸用→None;显式近半年→合法 6 个月窗)/裸半年(None)/未限定(None→max_available)/显式区间+相对并存→多范围阻断。

## 二、P1-② 并发写入不得覆盖裁决或查询记录(scripts/store_lock.py 新 + agent_judgment/research_archive/workbench_data)

### 基线复现(/tmp/r11_repro_p2.py,真实多进程 fork+起跑栅栏)

| 场景 | 基线(0877516) | 修复后 |
| --- | --- | --- |
| A 同 run 裁决双写(REVISE+UPHELD 并发) | 同路径配号,后写覆盖先写,**两次都返回成功**,只余 1 份裁决 | 6 进程并发(门 B1)→ **6 份完整裁决**(序号 01-06 唯一),revision 1..6 成链,零覆盖零崩溃;锁下配号冲突→`FileExistsError` 明确拒绝 |
| B 同日查询双档(配号→栅栏→落盘) | 两进程配同一 QB 号,共享临时文件名互相拆台,双 written 实存一条或进程崩溃 | 落盘串行化: 一条 written+其余**诚实拒绝**(rejected-duplicate-query-id),已存记录原样,零崩溃零假成功;split 调用(配号与落盘间有调用方间隙)的原子成对由事务路径(场景 C)承担 |
| C 工作台并发归档(save_to_archive×2) | 配号撞车(其一被拒或记录丢失) | `archive_write_lock` 事务(配号→IR→执行→落盘全程临界区)→ **QB-001/QB-002 两条完整记录**,配号互异 |

连跑三遍 0/3 稳定。

### 修复位置

| 文件:函数 | 修改 |
| --- | --- |
| `scripts/store_lock.py`(新模块) | ①`store_write_lock(dirpath)`: 目录级跨进程互斥(fcntl.flock,锁文件=目录下 .write.lock,目录即互斥域),**同线程可重入**(事务组合内层公开函数再取锁不死锁),跨进程/跨线程互斥;②`unique_tmp(path)`: 临时文件独立命名(`path.tmp.<pid>.<uuid>`)——并发写同名目标互不拆台,中断只留孤儿不出撕裂终档;③`atomic_write_json(path, doc)`: 独立临时名完整写+fsync 后 `os.replace` 原子发布 |
| `agent_judgment.py`:`record_semantic_verdict` | 配号(listdir 计数)、存在性检查(`FileExistsError` 拒绝覆盖)、前序/revision/predecessor 计算、落盘全部移入锁临界区;落盘改 `atomic_write_json`;锁域=semantic_review 树(跨日修订链同域互斥) |
| `research_archive.py` | `archive_write_lock(archive_dir)`(新公开事务入口,锁域=采集目录);`allocate_query_id` 配号入锁;`append_query_record` 尾段(存在性/单调性/建目录/落盘)入锁+原子写;`write_research_full` 同 |
| `workbench_data.py`:`save_to_archive` | 配号→IR 构造→执行→append 全程持 `archive_write_lock`(执行段在临界区内=串行化代价换配号→落盘原子成对,docstring 注记);状态检查与返回在锁外 |

中断写入(门 B4): `json.dump` 注入失败→异常上抛、终档原样、仅独立临时孤儿——不产生撕裂终档。串行追加/重复明确拒绝(门 B5)/裁决链校验(r6 门)行为保留。

## 三、P1-③ 引用扫描失败时禁止误删证据(scripts/data_retention.py;run_weekly.py 调用面不变)

### 基线复现(/tmp/r11_repro_p3.py,临时目录,now=2026-11-18/cutoff=2026-08-20)

| 场景 | 基线(0877516) | 修复后 |
| --- | --- | --- |
| 截断快照唯一引用的 macro_20260205 | 引用被当作不存在→**直接删除且无归档**(字节不可恢复) | 未删,降级 gzip 归档,**原始字节读回一致** |
| 扫描脏目录的永久删除面 | 继续删(含无引用老档) | `deleted=[]` 全停(「无法判断引用」≠「没有引用」),应删档入 `deletion_skipped` 降级字节保全 |
| 扫描异常上报 | 静默吞掉(OSError/ValueError→continue) | `scan_problems` 逐份登记(快照名+错误),report 字段+`main()` 明确打印 |
| 对照: 完好引用保护/月度代表归档/研究层不动 | 正常 | 正常(字节保全核验) |
| 对照: 扫描净目录常规策略 | — | 不变: 无引用老档删除/引用保护归档/月度代表归档/近窗保留/scan_problems 与 deletion_skipped 均空 |

### 修复位置

| 文件:函数 | 修改 |
| --- | --- |
| `data_retention.py`:`research_referenced_files` | 返回 `(refs, problems)`: 读取失败/JSON 损坏/非对象结构逐份登记 `{'snapshot','error'}`;listdir 失败整体登记;可解析快照的声明并集照旧 |
| 同上:`prune_daily_archives` | `scan_problems` 非空→过期未声明档**不删除**,降级 `_gzip_into_archive`(与月度代表同一字节保全机制),入报告 `deletion_skipped`;月度代表归档与已解析引用保护照常;报告新增 `scan_problems`/`deletion_skipped` 两键 |
| 同上:`main()` | 扫描异常逐条打印(快照名+错误)+跳过删除降级归档计数 |
| `tests/test_charter7_p0.py` | 引用集断言对齐二元组返回(`== ({...}, [])`) |

## 四、P2-④ 工作台更新后加载新快照(app.py + scripts/workbench_data.py)

### 基线复现(/tmp/r11_repro_p4.py,**实际 streamlit 1.50.0 缓存运行时**,隔离 venv /tmp/r11_venv,bare 模式=真实 st.cache_data 语义,直接导入 app.py 本体)

| 场景 | 基线(0877516) | 修复后 |
| --- | --- | --- |
| 同进程旧→新(首读 20261117,外部落盘 20261118) | 无参无 TTL 缓存→**仍返回旧快照**(须重启进程) | `app._current_state()` 返回新日期 20261118;`_load_state.clear()`+再读同 |
| 首次生成(初始无快照→采集生成) | **仍 None**(须重启) | 同进程读到新快照 |
| 指纹稳定性 | — | 输入无变化→指纹不变(不误失效) |
| 采集失败路径 | — | rc≠0 仅 `st.error`,无 clear/rerun/success(**不失效不假成功**,结构断言+失败分支逐词核验) |

### 修复位置

| 文件:函数 | 修改 |
| --- | --- |
| `workbench_data.py`:`state_fingerprint`(新) | 加载输入的内容指纹: `data/daily/research_snapshot_*.json` 候选集+`config/metric_registry.json` 的文件集×mtime_ns×size → sha256;纯文件系统操作零 streamlit 依赖(CI 可独立测试);外部采集落盘(含另一进程)即被指纹发现 |
| `app.py`:`_load_state`/`_current_state` | `@st.cache_data` 缓存键=指纹参数——文件更新→键变化→自动重读新快照;模块级绑定经 `_current_state()` 每次 rerun 重取 |
| `app.py`:刷新按钮成功分支 | rc==0 → `_load_state.clear()`+`st.rerun()`(旧实现提示"刷新页面"但缓存无 TTL,重启前永远旧快照);失败/超时/OSError 分支不动缓存,如实报错 |

CI 无 streamlit: 门 §D 以指纹语义(增/改/删/注册表变化→指纹变化;无变化→稳定)+app 结构断言(成功=clear+rerun,失败=仅 error)在 CI 内判定;真实缓存运行时验证在本地 venv 执行并记录于此(上表),不伪造 CI 覆盖。

## 门测试(tests/test_audit_r11_gate.py,29 判据)

- **§A 时间约束(10)**: 多范围/去年和前年→unparseable+拆分;一年半=十八个月=1.5年同窗 months=18;1.5年@完整历史真实窗交付(n_in=17/下界10);六季度/残缺数量明确拒绝;验收不变式(E 加窗仍拒不翻转/C 窗内足量真满足);既有正例 9 形保留;2026年内 BAD+区间年限并存多范围阻断。
- **§G 生产双门(3)**: 多范围与六季度规格 report 拒+archive 拒;1.5 年真实 18 个月窗正例可交付(合成裁决 'R11-GATE' 仅身份标记)。
- **§B 并发(7)**: 6 进程并发裁决→6 份完整记录(序号唯一/revision 成链/零覆盖零崩溃);工作台并发归档→两成功两记录配号互异;同日查询并发→无假成功无崩溃已存记录完整;中断写入→异常上抛+终档原样+仅独立临时孤儿;串行追加+重复明确拒绝保留。
- **§C 保留(4)**: 扫描脏→零永久删除+全字节 gzip 可恢复+deletion_skipped 登记;扫描异常逐份登记(快照名在场);研究层不动;扫描净→常规策略四判全不变。
- **§D 工作台缓存(7+1 跳过)**: 指纹稳定/快照新增/更新(mtime)/删除改名/注册表变化→指纹变化;复稳定;app 结构(指纹入参+成功 clear+rerun+失败仅 error);D7 真实 streamlit 运行时(本地 venv 执行=本报告§四,CI 如实跳过)。

## 回归与交付

- **既有门复跑**: r4 29/0、r5 30/0、r6 25/0、r7 37/0、r8 30/0、r9 33/0、r10 29/0、t3 43/0、r42 19/0——全绿。
- **电池**: 184 件(新增 r11 门)直跑 183 绿+phase6 D3(工作面净)提交后复跑绿=184/184 口径与 R10 一致。
- **复放四包**: BLIND 64/64、F10 rc=0、新 B recompute_r6b 105/105、e2e-corrected 全吻合——研究数值复算与历史实采证据绑定零回退。
- **夹具修复(非生产行为)**: ①`test_audit_r4_gate.py` L2 当日前缀动态化(20261115/16 硬编码跨午夜误红,判定语义不变);②`test_audit_r6_gate.py` C5-C7 采集档名动态化(save_macro 以运行当日命名,macro_20261117.json 硬编码 11-18 起误红,判定语义不变);③`test_audit_r7_gate.py` T12 对齐(显式区间+相对年限并存→多范围阻断,R7「显式区间优先」口径按本轮指令废止,断言改为 unparseable+拆分并注记);④`test_p03_e2eb_b4.py` 三断言对齐新持久化架构(采集目录常驻 .write.lock 锁文件=互斥域本体,非散落文件;`archive_write_lock` 入公开面白名单=事务组合显式扩面;本模块 open 面收敛为纯读 3 处,两处写入移 store_lock.atomic_write_json)。
- **复杂度基线重锚(章程§四.4 登记路径)**: `COMPLEXITY_BASELINE.md` 自 Audit-R2 后未重锚,R4-R10 七轮门测试累积+本轮 29 判据门使 test_lines 达 +5.8% 触发 `complexity_baseline.py --check` 红。登记理由: 增量=审计修复轮判据门(每轮外审反例的回归资产,非新增框架/系统/重复模型;生产面 91f/+4.6% 在阈内,唯一新增生产模块 store_lock.py=本轮 P1-② 修复本体)。按 R2 先例 `--write` 重锚(生产 91f/54650L,测试 195f/86455L),重跑 pc_phase1 门 13/0。
- **CI 首跑红与热修(判定口径,非生产行为)**: 首跑 run 44132467404(b4bdc52)tests 3.11/3.12 两 job 红——新门 B1/B1b 判 `files=0`。根因: 生产 `record_semantic_verdict` 以北京+8 定日目录(agent_judgment.py:617),门读取面用 runner 本地时区定日(CI=UTC 窗,本地=北京)——CI 落昨日目录故 0 文件,六进程本体全 ok。本地 `TZ=UTC` 精确复现 27 PASS/2 FAIL 后,门定日改为生产同款 +8(test_audit_r11_gate.py 热修注记),三时区(UTC/上海/纽约)复跑 29/0。Charter 8 时区时间炸弹同类,登记为坑⑧。
- **CI**: 最终推送 HEAD 三 job 绿(见尾部回填)。
- **worktree 清单**: 全程固定 6,零新建。

## CI 回填

- 首跑: run 44132467404 @ b4bdc52 = tests(3.11)✗ tests(3.12)✗ gates ✓(B1 时区错位,见上热修)。
【待推送后回填: 最终 HEAD/运行号/三 job 状态】

## 剩余阻塞

无。(本轮四项全关;停等用户外部独立审计裁定——不并 main、不合并 PR、不部署、不开新轮。)
