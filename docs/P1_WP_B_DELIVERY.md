# IA-P1-WP-B DELIVERY(交付件 · 状态=终态交付)

- 契约: IA-P1-WP-B-AC-v1.1(FROZEN 2026-11-06 00:3x HKT); 分支 dev/p1-impl-b(自 BASE-P1B=f6d0beb7cdba8631c9df6a20a2e9a5e6140c1c20)
- 全文叙事/实录: docs/P1_WP_B_REPORT.md; 本件=交付面五节+漂移维护政策(AC-03)。

## §一 交付清单(逐项 1:1: 文件→授权项→DESIGN 依据→验证锚)

| 文件 | 状态 | 授权项 | DESIGN 依据 | 验证锚 |
|---|---|---|---|---|
| scripts/fact_engine.py | M(+127/−2) | M-a | L170 技术要点"normalize_jp/ea、build_all 扩展"+§三(a-3) L62-64 | tests/test_p1_wp_b.py t01-t12; test_fact_engine(CI 绿) |
| config/metric_registry.json | M(1 行) | M-e | 冻结章 (e) 条件单字段 | t19(单字段锁) |
| docs/P1_WP_B_REPORT.md | A | A1 | 合同§五.1 | 本文互证 |
| docs/P1_WP_B_DELIVERY.md | A | A2 | 合同§五.2 | 本件 |
| tests/test_p1_wp_b.py | A(20 测) | A3 | L170 ①②③ | 本地 CI 71 槽(§四) |
| scripts/snapshot_builder.py | **零 diff** | M-b(面已被 WP-A 吸收) | §四 L126"扩展仅 resolve_inputs/sources_status" | t16/t17/t18(真实 build_snapshot 证成) |
| scripts/trading_calendar.py | **零 diff** | M-c(面已被 B3/WP-A 交付) | L170"jp/ea 日历" | t03/t08(japan/ea 日历口径断言) |
| scripts/data_validator.py | **零 diff** | M-d(条件未触发) | 冻结章 (d) | Gate A/B 注册表驱动面无扩展需求(REPORT §零.4) |

## §二 验收要点逐条映射(L170 ①②③)

- **① 事实构造+口径+数据不足**: t01/t02(jp 权属拆分)/t07/t09(ea)/t03(NIKKEI +4.0×3 窗口, japan 日历 8 会话)/t08(DAX +5.0, ea 日历 6)/t04(七窗口 unavailable)/t05(未注册 FAIL 诊断)/t06(inflation=null 诚实缺席)/t10-t12(build_all 扩展+兼容+不伪造对账)。
- **② sources_status 含 jp/ea 键(含缺源 MISSING)**: t16(EXACT+file/file_date+13 缺席边界合法登记)/t17(MISSING)。
- **③ US 面零回归(W-3)**: t18(7 通道 vs 基线 4 通道快照 facts/quality/gate_a 全等)+本地 CI 71 槽(§四)。
- **技术要点 Gate A 对新指标裁决**: t13(在场计数+边界收敛 7→3)/t14(缺席 13 条边界记录, 精确字符串)/t15(坏值 noncore_fail, effective=DEGRADED)。

## §三 fixture→期望值映射(漂移维护之基; 全 [示意·合成·值发明], REPORT §零.8/§零.11)

| fixture(值) | 期望(硬编码) | 锚 |
|---|---|---|
| JP_SYN NIKKEI 系列 {2025-12-30:50000, 01-05:51000, 01-09:52000}, as_of 2026-01-09T08:00+08 | week/mtd/ytd pct=4.0; week expected_sessions=8(01-01 排除)/sessions_in_window=2; m1 unavailable | t03 |
| JP_SYN CPI 2.2@2025-12-01(月频无 release_date) | quality=WARN(RELEASE_UNKNOWN) | t01 |
| EA_SYN DAX {2026-01-02:20000, 01-09:21000} | week pct=5.0/expected_sessions=6 | t08 |
| EA_SYN 七值(2.00/2.65/2.82/2.31/2.2/21000/8100) | 7 facts(六 PASS+HICP WARN) | t07 |
| fixt jp/ea(WP-A v1.3 合成: NIKKEI=38000/ECB_MRO=3.15 等) | ids∩JP13={NIKKEI,ECB_DFR,ECB_MRO,BUND_10Y,BUND_2Y,EA_HICP_YOY}(DAX/CAC40/JP_CPI 诚实缺席) | t10/t13 |
| japan 手工 4 事实(0.100/0.500/0.900/1.200@2026-11-05) | boundary JP13 7→3 | t13 |
| [实取] jp_20261105/ea_20261105 | NIKKEI=61077.9 PASS+recon{1.043,2.855,1.891}; ECB_MRO=2.65 DEGRADED(滞后50天) | t20 |
| [实取] registry | NIKKEI range=[5000,150000]/版本 2.2.0/94 条目 | t19 |

## §四 复跑终态([实取·命令输出])

- 全套件: `python3 tests/test_p1_wp_b.py` → **Ran 20 tests, OK**(FAILFLAG=0)。
- 本地 CI 镜像(canon=offline-tests.yml 同构, 逐 test_*.py 脚本方式): **TOTAL_SLOTS=71 GREEN=70 FAILFLAG=0**(2026-11-06 00:59-01:01 HKT; test_glm_live SKIPPED 设计性; summary=/tmp/p1-wp-b-evidence/ci-summary-wpb.txt, 逐件 log=ci-logs-wpb/)。
- 关键从属锁全绿: test_p0_baseline_lock_equivalence/test_p1_wp_a(23 测)/test_p03_e2eb_b3(B3 冻结锚)/test_fact_engine/test_phase3/test_p03_final_acceptance/test_p01_fix6。
- 白名单: `git diff --name-status f6d0beb..HEAD` = A3+M2+D0(REPORT §零.13)。
- 证据包: IA-P1-WP-B-EVIDENCE.zip = **111 成员/397,969 字节/sha256=6e786095e05479990e46bdb723ef7c4030d49d74a97e9412b1d8f9ebd728b37e**(装配 2026-11-05T17:12:26Z, TIP=fa95213; REPORT §零.16.1; SHA256SUMS zip 外自指豁免沿 WP-A R023/R060)。

## §五 漂移维护政策(AC-03)

1. **fixture 漂移**: tests/fixt.py 或 test_p1_wp_b.py 合成值变更→§三映射表必须同步再登记并复跑 t01-t20; 真实首档值(t20)变更→须先更新 REPORT §零.11.7 预登记再改断言(先登记后实现纪律沿用)。
2. **上游再演进**: WP-A/B3 若调整 jp_/ea_/japan_ 档节形态(a-2 结构)→normalize_jp/ea 的节取值面(_channel_fact price_like 分支)为唯一适配点; registry 若调整 13 指标权属(source 字段)→normalize_jp 权属拆分与 _JP_RECON_MAP 语义以 registry 为唯一权威随之重审(t02/t13 断言同步)。
3. **锚点面**: NIKKEI range 上限再次触顶(真实收盘>150000)→按 §零.11.1 同侪余量算术重算并先登记(REPORT 先例沿用); B3 冻结锚(test_p03_e2eb_b3 t02)覆盖 JP_POLICY_RATE/JGB×3 完整字段, 本包未触碰; build_all 签名再演进→t11 兼容断言为准绳(位置参数面)。
4. **白名单外发现(F1-F6)**: build_snapshot facts 级接线/series_store 键/_SOURCE_TO_INPUT jp/ea 绑定/fixt L214 注释陈旧/EA 双源对账/jp 对账对手方——任何后续包承接时, 本包 t13/t14/t16 的 boundary==13 与 t18 全等断言即为**预期变更面**: F3 落地将使 boundary 断言转向 noncore_missing 断言, F1 落地将使 t18 需扩展为"US 面+新通道面"双对照——承接包须先在本节登记预期断言迁移, 禁静默改断言。

## §六 逐 AC 自评摘要(v1.2 整改轮增节; 仿 WP-A DELIVERY §五 形态; 逐条全文=REPORT §三+stdout 四段自述, 标注同源)

- **AC-01 规格抄录与登记正确性: 绿** — §零.2 逐字转写 L170 与 DESIGN 原文**逐字节一致**(v1.2 项1 勘正后; 全角逗号失实两处域已改半角+披露行在档), 四要素齐备; 清单 A3+M5 登记 §零.3(同源 REPORT §零.2/§零.3)。
- **AC-02 验收要点逐条映射: 绿** — L170 ①②③+技术要点四项+(e) 触面逐点映射表=REPORT §一(同源); DP=零载明判定(REPORT §零.7, 判定依据在档)。
- **AC-03 测试与确定性: 绿** — 20 测全绿零网络全合成 fixture, 期望值字面量硬编码(REPORT §零.8); 漂移维护政策=本件 §五, fixture→期望值映射=本件 §三; 桩纪律 7=不适用(登记清单无外部调用面文件, REPORT 判定依据在档)。
- **AC-04 引用真实性: 绿** — 引用 file:line 逐条可寻; normalize_ea 行号端点已按 v1.2 项2 勘正为 L566-587(实测函数域, REPORT §零.12); 注入摘要一律标注「注入摘要,非工作树实读」。
- **AC-05 范围/分支/生产隔离: 绿** — `git diff --name-status f6d0beb..HEAD` = A3+M2+D0 逐件在授权面内(REPORT §零.13); 纯线性零 merge 零 amend; BRANCH-SET 42 冻结零漂移+唯一新增 dev/p1-impl-b; LIVE grep 零命中+零写入; 零网络(唯一网络面=git 通道)。
- **AC-06 CI 与证据包: 绿** — 本地 CI 镜像 71 槽=70 exit0+1 SKIPPED(test_glm_live 设计性), FAILFLAG=0(本件 §四); 证据 zip 八类最低集齐+SHA256SUMS zip 外自指豁免(§四登记 sha256); 本件五节齐备+本节起 v1.2 增节; CI dispatch=操作者 CHECKPOINT 面(登记件 rounds/045/P1-WP-B-CI-dispatch-evidence.md, 本 Agent 不自行触发)。
- **AC-07 研究纪律与使用边界: 绿** — P1 特有纪律六条登记并遵守(REPORT §零.6); 缺席不填 0/陈旧 DEGRADED/不足 unavailable 如实(t06/t09/t20); 零真实 GLM/零网络出站/零凭证/零付费; F1-F6 白名单外发现登记不实现(REPORT §零.9); W4/W5 未入链。

## §七 如实偏差(v1.2 整改轮增节; 同源摘录自 REPORT §二, 编号一致)

1. **§零.1 禁锚措辞失实**(取证期发现): "非祖先"字面对任何合规分支不可满足=c9626633 实为 BASE-P1B 历史祖先; 正确判定三元组在档(分支基点 f6d0beb 正确/恰纯线性提交/main 未触碰); §零.16.2 完整登记+原句划线保留; v1.2 处置章认定该偏离处置已接受(同源 REPORT §二.1)。
2. **快照面交付形态偏离(收敛性)**: (b) 授权面被 WP-A SOURCE_FILE_RULES→SOURCES 推导吸收, 本包零 diff+测试证成(t16/t17/t18), 非缩水; facts 级接线/series_store/_SOURCE_TO_INPUT=白名单外 F1/F2/F3 登记不实现(同源 REPORT §二.2)。
3. **测试开发期 4 处预期失实**: 均测试侧对齐既有系统语义, 零实现侧回改, 逐处诊断登记(同源 REPORT §二.3/§零.12)。
4. **首轮 CI 镜像调用方式失当**: `-m unittest` 致 2 脚本式套件误红, canon 文件方式重跑 71 槽全绿, 失当过程不隐瞒(同源 REPORT §二.4/§零.15)。
5. **F4 注释陈旧**: fixt.py L214 旧区间注释陈旧(值仍合法), fixt 不在白名单不更新(同源 REPORT §二.5)。
6. **零运行产物**: 验收①②③全部为【测试】/【CI】面, 无真实运行验收面; 未运行采集器/生产快照路径, data/ 零变化(同源 REPORT §二.6; 证据 06-no-run)。
7. **ECB_MRO DEGRADED 如实降级**: 观测滞后 50 天>10 天窗, t20 断言 DEGRADED——诚实降级语义非缺陷(同源 REPORT §二.7)。
8. **v1.2 整改轮登记**: ①rounds/045 首审 FAIL 四阻断项全为文档/证据形式类(处置章认定), 本轮四项授权全部落地(零代码/零测试/零数据面); ②本轮新发现=REPORT §零.1 表更正指针指向「§零.16.3」而实际禁锚更正节为「§零.16.2」(v1.1 取证更正笔转写滑笔; 不在四项授权面内, 未整改, 判定权留操作者; 注: 本轮 zip 终笔新增节恰为 §零.16.3[zip 重装配登记], 与该指针本意[禁锚更正=§零.16.2]语义不同)。

## §八 参考(v1.2 整改轮增节)

- 合同: IA-P1-WP-B-AC-v1.2(v1.1 冻结章及全部 AC 语义不变+处置章四项整改授权; 注入摘要,非工作树实读——执行Agent 不可达引擎路径, 合同经提示词内嵌传递)。
- 设计: docs/P1_DESIGN.md §六 L170 WP-P1-B 行(blob 13b263cf, 基线工作树实读; 设计支 dev/p1-design@049ec978 终态留驻只读)。
- 上游对照同源: WP-P1-A(R044)工作树在场交付件(其 REPORT §零 登记清单为对照同源; 含 jp_/ea_ 采集器/registry 三字段/SOURCE_FILE_RULES jp/ea/fixt jp/ea 合成节); B3 冻结锚=tests/test_p03_e2eb_b3.py t02。
- 范本: docs/P1_WP_A_DELIVERY.md §五(本件 §六 仿其合规形态)。
- 证据: /tmp/p1-wp-b-evidence/IA-P1-WP-B-EVIDENCE.zip + SHA256SUMS(zip 外自指豁免, 沿 R019/R023/R060 先例); CI dispatch 登记件=引擎侧 rounds/045/P1-WP-B-CI-dispatch-evidence.md(操作者 CHECKPOINT 落字面值)。
