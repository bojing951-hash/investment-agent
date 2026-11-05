# IA-P03-W2-GLM-WP-G4 DELIVERY(GLM 研究结论层第 4/末实现包·真实调用接线)

> 分支 `dev/p03-w2-glm-g4`(自基点 d667a4e5f3faf93fffbaa1ab1bfd67c386fee2e3 切出,纯线性)
> 合同 IA-P03-W2-GLM-WP-G4-AC-v1.0;详细逐要点证据映射与偏离登记见 REPORT §三/§五。

## §一 改动

| 项 | 值 |
|---|---|
| 白名单(恰 k=5,纯新增 A 行) | scripts/glm_conclusion_client.py / tests/test_p03_w2_glm_g4.py / docs/P03_W2_GLM_G4_REPORT.md / docs/P03_W2_GLM_G4_DELIVERY.md(本件) / docs/P03_W2_GLM_G4_CREDENTIAL_REGISTRY.md |
| 模块 sha256 | glm_conclusion_client.py=a846f727ac299e4e4a9432d91ca147dd657e89b918378439b19a800b32d0e718;test_p03_w2_glm_g4.py=404de82b60026208d3a5f16189e721344ce18cf5752fabe2bc3cfb8cafa93e48(负向敏感性注入→红→还原逐字节一致) |

**scripts/glm_conclusion_client.py**(真实调用接线模块;stdlib import 面,openai 惰性导入;零 data/daily 引用):
冻结常量 CB-1~CB-4(L51-54)+DP 初值(L57-64)+费用估算参数(L67-69,示意单价);`CircuitBreaker`(L164,CB-2 软停/CB-3 达限 TRIPPED/CB-4 >120s 计失败并入 CB-1/reset 仅人工不清计数);`build_prompt`(L302,DESIGN §四(1) 六槽位+反馈回注槽+JSON schema 块复用 G2 常量);`call_glm_once`(L468,client_factory DI,None=真实路径: 门控→惰性 OpenAI→流式 create(L497)→usage 捕获→CB-4 判定→异常分类);`run_live_conclusion`(L565,attempts 喂 G2 `run_conclusion_pipeline` 权威裁决+径1 反馈回注预算 gov.MAX_RETRIES=3+G3 结论记录 append-only+用量 JSONL);`run_smoke`(L673)与 CLI(L728,`--echo` 参数回显/`--live-smoke` 执行段冒烟需 RUN_GLM_LIVE=1+GLM_API_KEY/默认打印跳过 exit=0);`redact`(L116)/`estimate_cost_usd`(L126)/`classify_elapsed`(L139)/`render_registry_row`(L656)。

**tests/test_p03_w2_glm_g4.py**: 48 用例七类全合成桩零真实出站,预期值字面量硬编码——T0 fixture 自检 4/T1 熔断 11(AC-03.8 冻结值字面量)/T2 客户端桩 7/T3 六槽 9/T4 编排 8/T5 门控边界 8(CLI 子进程默认跳过+源码 grep 反证)/T6 真实路径守卫 1;本地 exit=0。

**三份文档**: REPORT(§零登记+§一前置实读+§二参数登记+§三要点映射+§四取证+§五偏离+§六自检)/DELIVERY(本件)/REGISTRY(合同 §七.7 冻结模板+G4-CRED-001 逐字段+执行段结果)。

**复现**: 参数回显 `python3 scripts/glm_conclusion_client.py --echo`;默认无门控=零出站零凭证读取 exit=0;执行段冒烟(仅实批后)=先快照(`scripts/snapshot_builder.py --date <YMD> --out-dir data/research`)→逐面登记 REGISTRY→`RUN_GLM_LIVE=1 python3 scripts/glm_conclusion_client.py --live-smoke --ymd <YMD> --snapshot-dir data/research --task data/research/RT-*.json --out-dir data/research --registry-seq <N>`;产物落 data/research/ 不 commit。

## §二 证据

- 证据包: `/tmp/p03-w2-glm-g4-evidence/IA-P03-W2-GLM-WP-G4-EVIDENCE.zip`(九类最低集: ①规格抄录+登记清单 ②交付文件双源副本交叉哈希 ③git 取证含设计在场核验 ④本地 CI 逐套件 ⑤逐要点映射表 ⑥真实调用脱敏日志+双面锚定 ⑦自述副本 ⑧SHA256SUMS[自身显式豁免不入 zip] ⑨REGISTRY 脱敏副本);zip sha256=装配后追加行(见本节末,自指豁免: zip 内副本为占位行版本,终值以本工作树行+zip 外 final-state.txt 为准)。
- 本地 CI(同构,零真实出站): 61 条目=59 exit=0(含新增套件)+test_glm_live skipped+test_p4_fixes exit=1(既有环境红,基线 git archive 复现取证,零导入关系,REPORT §五.3);CI 面=59 基线+1 新增=60。
- 真实调用(唯一面 F1): REGISTRY G4-CRED-001——3 次真实出站全传输层成功(26.9/26.1/19.7s,均<CB-4=120s),费用估算 $0.0667(<CB-3),熔断未触发(0 连败/3 of 60);G2 终裁 **ABSENT_REGISTERED**(情形(c)如实: 模型输出 3 次未过校验器,失败面收敛 schema 外字段→limitations 义务→仅剩数值接地);G3 落档 CR-20261105-001;产物=glm4_usage_log_20261104.jsonl(3 行)+glm4_live_smoke_20261105T015850Z.json+glm_conclusions_archive.json(均不 commit,脱敏副本入证据包⑥)。
- 锚定: 运行前后 data/daily(24)+data/research 既有(3)全 27 文件 sha256 不变,新增仅 7(快照 5+运行 3,去重后 7);清单入证据包⑥。
- git 取证: diff=5 纯 A 行/纯线性零 merge/HEAD^=基点/ls-remote 尖端=HEAD;冻结 36 支集(35 dev+main)逐一复核零漂移,唯一新增=本分支(合同 §0 合法);设计在场核验 merge-base exit 0+六件 blob 等值 6/6;输出原样入证据包③。
- LIVE 路径/launchd: 零写入零触碰(边界声明;证据包③ reflog+diff 可反证)。
- 凭证明文: 零落盘(REGISTRY 仅环境变量名;证据包全成员装配后凭证模式 grep 复核零命中)。

> zip sha256(装配后追加行): fe11a2bbfd5988cce3c0400f51d88e80781654afeef717d25a12181cd4d3bab7(100 成员/354032 字节;装配后全包凭证模式 grep 复核=零凭证明文命中,仅 3 处 'Authorization' 字面量=脱敏正则代码与既有 P2 测试类名,非凭证值)。自指豁免: zip 内 DELIVERY 副本(tip/工作树成员②)=026a479 版占位行,固定点不可内含自身哈希,实测值以装配后追加行落档;终态 SHA 与最终 ls-remote 见证据目录 08-sidecar/final-state.txt(zip 外)。

> zip sha256 v2(补证据轮重装配,装配后追加行): b9e8d4268c27b37ba378061bac20186081d6599651436576e95e23e358d7c8f7(104 成员/367496 字节;SHA256SUMS 重列 103 成员全验证 OK,清单自身显式豁免不入 zip 自身校验和;装配后全包凭证复核=凭证据值字节扫描零命中,'Authorization' 字面量 13 处=引用性文字/本模块脱敏正则代码/既有 P2 测试类名,零凭证值)。v2 变更=新增第 4 次尝试阻断工件 4 件[06-real-run/live_smoke_F1_attempt2_blocked.txt+anchors/pre-run-sha256-round2.txt+anchors/post-run-check-round2.txt+03-git/forensics-round2.txt]+双源副本/REGISTRY/映射/自检副本刷新至补证据轮提交 1(d40eeaa)版;终态 SHA 与最终 ls-remote 以 zip 外 08-sidecar/final-state.txt 为准,自指豁免沿 v1: zip 内 DELIVERY 副本=占位行版本(d40eeaa)。

## §三 逐 AC 自评(详见 REPORT 对应节)

| AC | 自评 | 一句证据指引 |
|---|---|---|
| AC-01 规格抄录与交付面登记 | PASS | REPORT §0.2 逐字抄录(DESIGN L234-238,偏差 0)+§0.3 k=5 清单结构约束全过 |
| AC-02 验收要点逐条映射 | **NOT VERIFIED(限要点①冒烟受纳子面)** | 映射表零漏检/落点真实/参数三方一致/锚定不变/零编造(REPORT §三);但要点①模型输出 3 次未过 G2 校验器=情形(c)如实,该子面按合同 §九(c) NV 处置,交审计裁量 |
| AC-03 测试与确定性验证 | PASS | 48 用例本地全绿零真实出站;冻结值字面量硬编码(T1);漂移维护策略专节在场(§五);fixture→预期值映射(§五.4) |
| AC-04 引用真实性与注入边界 | PASS | REPORT/DELIVERY file:line 逐条实取;注入摘要已标注;跨支引用 ls-remote 实取(design 0c8de3c3/g3 d667a4e/冻结 36 支集);否定性声明 grep/diff 可反证(证据包③⑤) |
| AC-05 范围/分支/生产隔离 | PASS | diff 恰 5 A 行零 M/D;纯线性零 merge;reflog 无 reset/amend;未 force push;main 未碰(36 支集零漂移);LIVE/launchd 零触碰 |
| AC-06 CI 与证据包 | PASS(本地交付面) | 证据包九类齐+SHA256SUMS 自指豁免;DELIVERY 五节+漂移专节;CI dispatch=操作者 CHECKPOINT(本包不自行派发,登记件将落 rounds/029/GLM-WP-G4-CI-dispatch-evidence.md,自述引用该路径)——CI 实跑值以登记件为准 |
| AC-07 研究纪律与使用边界 | PASS | 零直读 data/daily(T5/T6 源码 grep 反证);缺席如实登记不填 0;零投资建议文案;PENDING 门履行(实批后唯一面先登记后调用);熔断全程护航;REGISTRY 与日志计数一致;凭证明文零落盘 |

## §四 如实偏差(全文见 REPORT §五)

1. 要点①模型遵从性未达(情形(c),非 FAIL): glm-5.3 冻结初值(0.2/low)下 3 次尝试未过校验器,终裁 ABSENT_REGISTERED;禁重试凑结果,参数零事后回改;
2. DESIGN 冒烟机制由合同 AC-03.7 显式改道(tests 内→执行段),登记为机制承接非冲突;
3. test_p4_fixes 本地 exit=1: 既有环境红(基线 git archive+真实数据复现逐字相同/零导入关系/CI 无数据为绿),不越权修复;
4. env_config.py 既有本机回退路径: 白名单外发现登记不代改;
5. 原始响应正文不留档(仅 usage+trace 反馈链+终态报告),如实披露;
6. CI run ID 缺席: 合同步骤15 承接,操作者派发后落 rounds/029 登记件。
7. 补证据轮第 4 次尝试阻断(2026-11-05T02:45:52Z~02:48:27Z,如实非 FAIL): 4 次发起均被本会话工具权限层拒绝于执行前,**零真实出站**(佐证=锚定 34/34 不变+usage log 仍 3 行);REGISTRY G4-CRED-002=0/3 出站/$0.0000/$0.0667/未触发;按追加指令「恰 1 次不追加」停止;零代码/测试/参数改动;处置权操作者(择时重发/代执行);详见 REPORT §五.7+证据包⑥ 阻断记录。

## §五 参考

- 冻结合同 IA-P03-W2-GLM-WP-G4-AC-v1.0(§零登记制/§七.5 熔断冻结值/§七.7 登记模板);
- DESIGN(docs/P03_W2_GLM_DESIGN.md): WP-G4 行 L234-238/DP-1~4 L45-48/§三 L78-116/§四(1) 六槽 L122-131/§四(3) L143-148/§五 L163-175/§六 L193-209/模式 B 排除 L219/§八 红线 L244 起;
- 上游复用件: G1 scripts/glm_input_assembler.py(:293/:437/:550)/G2 scripts/glm_output_validator.py(:47-54/:111/:154/:186/:234/:582)/G3 scripts/glm_conclusion_integrator.py(:502/:567);E2E-A scripts/research_task_manager.py:36;机制族 scripts/allocation_engine.py:104;通道参照 scripts/report_generator.py:574-605;门控参照 tests/test_glm_live.py:31-33;标准化层 scripts/snapshot_builder.py:236;GLM 通道实值 env_config.py:28-29;
- INVENTORY docs/P03_W2_GLM_INVENTORY.md(GG-07→DP-1~4+WP-G4 承接)。

### 漂移维护策略专节(AC-03.6 三要素;AC-03 生效时必备)

1. **预期值唯一来源=仓库内版本化合成 fixture**: 一切测试预期值字面量定义于 tests/test_p03_w2_glm_g4.py 版本化常量区(L41-59)与 builder 函数,与真实采集档/真实 GLM 响应零关联;
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: fixture 值与其断言预期值同文件;后续演进=同一 tests 文件单 commit 内同步变更,禁分离漂移;
3. **真实数据档永不进入测试预期值来源**: data/daily、data/research 真实档与真实调用日志零 import/零读取/零路径引用进 tests(T5 源码 grep 反证+T0 值域互异锚点;CI 无数据环境全绿为结构性证明)。

#### fixture→预期值映射(逐断言组;定义处=tests/test_p03_w2_glm_g4.py)

| 断言组 | fixture 来源(定义处) | 预期值(硬编码处) |
|---|---|---|
| T0 fixture 自检(4) | build_synthetic_snapshot(L68)/build_synthetic_task(L116)/build_full_inp(L153)/build_absent_inp(L160)/build_valid_output(L170) | VAL_TIPS=1.87/VAL_GOLD=3912.5(L45-46)/OBS='2026-11-03'(L44)/YMDS='20261104'(L41)——与 G1 fixture(2.93/4186.7)互异,旁证独立发明 |
| T1 熔断(11) | CircuitBreaker 直驱 note_* 序列+编排注入 | FROZEN_CB1=5/FROZEN_CB2=60/FROZEN_CB3=5.00/FROZEN_CB4=120(L56-59);恰第 5 次 TRIPPED/第 61 次拒/累计>$5.00 TRIPPED/121.0s 计失败而 119.9 不计——零模块导入取值 |
| T2 客户端桩(7) | StubFactory(L263)/_ScriptedCompletions(L245)/_Usage(L226)/_Event(L232)/CanaryFactory(L278) | 费用字面量: 1000pt+2000ct→0.021(L449,注释载算式)/floor 0.02(用量缺席,L455);时延判级 121.0/119.9(L396/L401);脱敏 canary CRED_SENTINEL(L52)→<<REDACTED>>(L491/L725) |
| T3 prompt 六槽(9) | build_full_inp(L153)+legal_targets={VAL_TIPS,VAL_GOLD}(L499/L574) | 六槽位关键词逐字断言(现象/机制族 7 类/竞争性/反方/数值接地">=\|>\|<\|<="/缺席承接)+schema 块七字段名 |
| T4 编排(8) | build_full_inp+StubFactory 剧本(成功/schema 瞬态/网络/预置 TRIPPED) | outcome 字面量('ACCEPTED' 等)、attempts_used 计数、blocked_reason 前缀 'TRIPPED-CB-1'、档案 __v2 版本化、日志行数=出站数 |
| T5 门控边界(8) | 子进程真跑 CLI/环境变量清空场景 | 跳过文案含 'RUN_GLM_LIVE';--echo 键集=登记参数集;源码 grep 零 data/daily 引用/模块级零 openai import |
| T6 真实路径守卫(1) | 源码文本扫描 | 零 requests/urllib/httpx 直连(唯一出站点=流式 create,经 client_factory DI 可替换) |
