# IA-P03-W2-GLM-WP-G4 DELIVERY(GLM 研究结论层第 4/末实现包·真实调用接线)

> 分支 `dev/p03-w2-glm-g4`(自基点 d667a4e5f3faf93fffbaa1ab1bfd67c386fee2e3 切出,纯线性)
> 合同 IA-P03-W2-GLM-WP-G4-AC-v1.0;详细证据映射见 REPORT,本件=交付说明与漂移维护策略。

## §一 交付概览

| 项 | 值 |
|---|---|
| 白名单(k=5) | scripts/glm_conclusion_client.py / tests/test_p03_w2_glm_g4.py / docs/P03_W2_GLM_G4_REPORT.md / docs/P03_W2_GLM_G4_DELIVERY.md / docs/P03_W2_GLM_G4_CREDENTIAL_REGISTRY.md |
| 模块 sha256 | glm_conclusion_client.py=a846f727ac299e4e4a9432d91ca147dd657e89b918378439b19a800b32d0e718;test_p03_w2_glm_g4.py=404de82b60026208d3a5f16189e721344ce18cf5752fabe2bc3cfb8cafa93e48 |
| 测试 | 48 用例七类(T0 fixture 自检 4/T1 熔断 11/T2 客户端桩 7/T3 prompt 六槽 9/T4 编排 8/T5 门控边界 8/T6 真实路径守卫 1),本地 exit=0;全合成桩零真实出站 |
| 真实调用 | 唯一面 F1(模式 A 冒烟)已执行: 3 次出站/$0.0667/未触发熔断/G2 终裁 ABSENT_REGISTERED(情形(c)如实,详见 REPORT §三要点①与 REGISTRY §四) |
| 运行产物 | data/research/: research_snapshot_20261104.json(+.md+anchors)+glm4_usage_log_20261104.jsonl+glm4_live_smoke_20261105T015850Z.json+glm_conclusions_archive.json(不 commit) |
| 证据包 | /tmp/p03-w2-glm-g4-evidence/IA-P03-W2-GLM-WP-G4-EVIDENCE.zip(九类最低集;zip sha256=装配后追加行,见 §五末) |

## §二 逐文件交付说明

1. **scripts/glm_conclusion_client.py**(真实调用接线模块;stdlib import 面,openai 惰性导入):
   - 冻结常量 CB-1~CB-4(L51-54)+DP 初值(L57-64)+费用估算参数(L67-69,示意单价);
   - `CircuitBreaker`(L164): note_outbound/note_success/note_failure/state/reset(人工复位,不清出站/日费用计数);CB-2 软停/CB-3 达限 TRIPPED/CB-4 >120s 计失败并入 CB-1;
   - `build_prompt`(L302): DESIGN §四(1) 六槽位+反馈回注槽+JSON schema 块(复用 G2 常量);
   - `call_glm_once`(L468): client_factory DI(None=真实路径: 门控→惰性 `from openai import OpenAI`→流式 create(L497)→usage 捕获→CB-4 判定→异常分类(timeout/5xx→network,1301→risk_control,401/403→auth_error));
   - `run_live_conclusion`(L565): 门控→G1 回验→真实调用循环(预算=gov.MAX_RETRIES)→attempts 喂 G2 `run_conclusion_pipeline`(权威 outcome/trace/反馈)→G3 结论记录+append-only→用量 JSONL;
   - `run_smoke`(L673)/CLI(L728): `--echo` 参数回显/`--live-smoke` 执行段冒烟(需 RUN_GLM_LIVE=1+GLM_API_KEY)/默认打印跳过信息 exit=0;
   - `redact`(L116)/`estimate_cost_usd`(L126)/`classify_elapsed`(L139)/`render_registry_row`(L656)。
2. **tests/test_p03_w2_glm_g4.py**(48 用例;预期值全部字面量硬编码): 见 §四映射表。
3. **docs/P03_W2_GLM_G4_REPORT.md**: 规格抄录/白名单登记/参数登记/逐要点证据映射/git 取证/偏离登记/六项自检。
4. **docs/P03_W2_GLM_G4_DELIVERY.md**(本件)。
5. **docs/P03_W2_GLM_G4_CREDENTIAL_REGISTRY.md**: 合同 §七.7 冻结模板头部+G4-CRED-001 逐字段登记+执行段结果如实记录。

## §三 使用与运行说明

- 参数回显: `python3 scripts/glm_conclusion_client.py --echo`(登记=常量=echo 三方一致);
- 默认(无门控): 打印跳过说明 exit=0,**零出站零凭证读取**;
- 执行段冒烟复现(仅实批后;凭证经环境变量注入): `RUN_GLM_LIVE=1 python3 scripts/glm_conclusion_client.py --live-smoke --ymd <YYYYMMDD> --snapshot-dir data/research --task data/research/RT-*.json --out-dir data/research --registry-seq <N>`,前置=该日快照已在 `data/research/`(经 `scripts/snapshot_builder.py --date <YYYYMMDD> --out-dir data/research`);熔断器全程激活;产物落 data/research/(不 commit);逐面先登记 REGISTRY 再调用;
- 边界: 本模块零 `open()` 于 data/daily(源码 grep 反证);tests/CI 零真实出站(合成桩经 client_factory/breaker/legal_targets DI 注入,REPORT §二.4);禁交易/仓位/收益承诺文案(输出=G2 校验器受纳的研究假设集,非投资建议)。

## §四 fixture→预期值映射(逐断言组;fixture 定义处 file:line=tests/test_p03_w2_glm_g4.py)

| 断言组 | fixture 来源(定义处) | 预期值(字面量硬编码处) |
|---|---|---|
| T0 fixture 自检(4) | build_synthetic_snapshot(L68)/build_synthetic_task(L116)/build_full_inp(L153)/build_absent_inp(L160)/build_valid_output(L170) | VAL_TIPS=1.87/VAL_GOLD=3912.5(L45-46)/OBS='2026-11-03'(L44)/YMDS='20261104'(L41)——G1/G2 fixture 值域互异锚点(2.93/4186.7)旁证独立发明 |
| T1 熔断(11) | CircuitBreaker 直驱(note_* 序列)+编排注入 | FROZEN_CB1=5/FROZEN_CB2=60/FROZEN_CB3=5.00/FROZEN_CB4=120(L56-59);恰第 5 次 TRIPPED/第 61 次拒/累计>$5.00 TRIPPED/121.0s 计失败而 120.0 不计——全部硬编码字面量,零模块导入取值 |
| T2 客户端桩(7) | StubFactory(L263)/_ScriptedCompletions(L245)/_Usage(L226)/_Event(L232)/CanaryFactory(L278) | 费用字面量: 1000pt+2000ct→0.021(L449,注释载算式)、floor 0.02(用量缺席,L455)、时延判级 121.0/119.9(L396/L401);脱敏 canary: CRED_SENTINEL(L52)替换为 <<REDACTED>>(L491/L725) |
| T3 prompt 六槽(9) | build_full_inp(L153)+legal_targets={VAL_TIPS,VAL_GOLD}(L499/L574) | 六槽位关键词逐字断言(现象/机制族7类/竞争性/反方/数值接地">=\|>\|<\|<="/缺席承接)+schema 块含七字段名(复用 G2 常量渲染,断言取字面量串) |
| T4 编排(8) | build_full_inp+StubFactory 剧本(成功/schema 瞬态/网络/预置 TRIPPED) | outcome 枚举(G2 常量复用,断言取字面量 'ACCEPTED' 等)、attempts_used 计数、blocked_reason 前缀 'TRIPPED-CB-1'、档案 __v2 版本化、日志行数=出站数 |
| T5 门控边界(8) | 子进程真跑 CLI(默认跳过 exit=0)/环境变量清空场景 | 跳过文案含 'RUN_GLM_LIVE';--echo 键集=登记参数集;源码 grep 零 data/daily 引用/模块级零 openai import |
| T6 真实路径守卫(1) | 源码文本扫描 | 零 requests/urllib/httpx 直连(唯一出站点=流式 create,经 client_factory DI 可替换) |

**真实数据隔离声明**: 上表全部预期值来源=仓库内版本化合成 fixture(本 tests 文件 L41-59 常量区+builder 函数);执行段真实运行数值(3 次出站/$0.0667 等)仅入 REPORT §三/REGISTRY/证据包⑥,**永不进入测试预期值**。

## §五 漂移维护策略(AC-03.6 三要素专节)+证据包指引

1. **预期值唯一来源=仓库内版本化合成 fixture**: 一切测试预期值字面量定义于 tests/test_p03_w2_glm_g4.py 版本化常量区与 builder 函数(§四表),与真实采集档/真实 GLM 响应零关联;
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: VAL_* /FROZEN_CB* /剧本字符串等 fixture 值与其断言预期值同文件同 commit 演进(本包初版即同文件落档;后续任何演进=同一 tests 文件单 commit 内同步变更,禁分离漂移);
3. **真实数据档永不进入测试预期值来源**: `data/daily/`/`data/research/` 真实档与真实调用日志(usage log/冒烟报告)零 import/零读取/零路径引用进 tests(T5 源码 grep 反证+T0 值域互异锚点);CI 无数据环境全绿为结构性证明。

**证据包指引**: /tmp/p03-w2-glm-g4-evidence/IA-P03-W2-GLM-WP-G4-EVIDENCE.zip 九类成员
①规格抄录+登记清单 ②交付文件双源副本(git show 尖端版+工作树版交叉哈希) ③git 取证
(含设计在场核验) ④本地 CI 逐套件 ⑤逐要点映射表 ⑥真实调用脱敏日志+锚定清单
⑦自述报告副本 ⑧SHA256SUMS(自身显式豁免不入 zip) ⑨REGISTRY 脱敏副本。

> zip sha256(装配后追加行): 【待装配后实值追加——自指豁免: zip 内 DELIVERY 副本不含本行终值,终值以本工作树行与证据包⑧清单为准】
