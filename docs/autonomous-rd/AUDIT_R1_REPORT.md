# Audit-R1 第一轮审计修复与重新验收 — 终交付报告

- 分支: `dev/audit-fix-r1`(基于审计基线 `c9d5715`)
- 候选冻结 SHA: `1656294`(完整: `git rev-parse HEAD` 亲验;修复提交链见 §二)
- 引擎数据树(只读注入): `~/investment-agent-dev/data/daily`(快照 research_snapshot_20261112_v2 + macro_20261112 + views 库 17 份)
- 使用命令: `python3 ia_cli.py research-one --stage {plan|attach|report|auto} --question <NL> --out-dir <dir> --engine-root ~/investment-agent-dev`
- 本轮授权边界遵守: 未合并 main、未公开推送、未部署、未改远端权限、未购买 API/数据、未执行真实交易、未泄露密钥。

## 一、F01—F10 关闭表

| # | 发现 | 根因 | 修复位置 | 复验依据 | 状态 |
|---|---|---|---|---|---|
| F01 | 黄金 SCN-A 证伪逻辑倒置(跌幅不足5%=弱化被证伪,实与假说相容);各档「前提缺席」vs「前提发生但结果相反」不分档;美元竞争变量未条件化 | 判断写作面语义方向错 | BLIND SCN-B 重写(1月峰回撤主张作废→9月紧缩窗事实+双腿分解)+DXY 条件化(偏相关或\|ΔDXY\|<0.3%子样本两口径同向);C MECH-1 证伪区与确认区构造性互斥;C/B SCN-C 前提两态条款;A SCN-B 前提变体三分档 | 独立终审席逐项裁定 UPHELD(BLIND 12项/C 7项/B 6项/A 8项,全量复算逐位吻合);契约门 VERIFIED | ✅关闭 |
| F02 | report 阶段 L3/L4 produced=true+REVISE 仍 ok=true warnings 空——独立审查不约束交付 | report 段未接审查态 | `ia_cli.py` report 段四态门(generated/machine_verified/review/deliverable)+`agent_judgment.record_semantic_verdict`(append-only,content_sha256 绑定,fresh 判定)+`_semantic_review_state` | 新守卫 test_audit_r1_f02(15/0)+四档真跑: B 档底座 run_ok=False→**deliverable=False 如实拒发**(门有牙实证);A/C/BLIND deliverable=True 仅在独立席 UPHELD+fresh 后 | ✅关闭 |
| F03 | product_acceptance_runner.py question 经 json.dumps 拼 shell=True——命令注入 | shell 拼接 | argv 列表+shell=False,clone/checkout 分开调用,question/baseline/workdir 独立参数,基线解析确切 commit;无害负例($/反引号/引号/换行/空格路径) | 守卫 test_audit_r1_f03(12/0)无害负例全过 | ✅关闭 |
| F04 | CI 三套红(arch_reform_phase6/rd_r20_state_checkpoint/rd_r20_state_consistency)+pytest SystemExit≠成功+FAILED 列表不传播+py3.11/3.12 环境 | 见 F04 修复链 | 已在 36c1e7e 修三套 CI;pytest 适配器 rc 契约(目录面 fail-closed);py3.11 CI 钉版+py3.12 AST ast.Constant 迁移(F04b 4b1e4ca);test_p3_wp_d 3.12 差异单独解释未放宽阈值 | CI #297(36c1e7e)=success;候选 1656294 本地全量 185 件 **867 PASS/0 FAIL**;py3.12 浮点末位差异=环境差异如实分离 | ✅关闭 |
| F05 | 四任务证据包原件缺(report.json/views_digest/evidence_index 指 /tmp);脚本绝对路径 | 归档不完整 | A 档 evidence_pack/ 原件入库+sha 验证;BLIND 冻结脚本去绝对路径(IA_ENGINE_DAILY 环境变量,默认 ~/ 展开);blind_calc2 pp/bp 阈值 bug 修(旧 n=27/+0.07% 不可复现根因);无倒填——修订以 Audit-R1 标记显式留痕 | BIGFILES.sha256 重算四档;A evidence_pack sha 亲验;预注册只锁问题文本(不锁脚本),脚本修订链 inline 标记+MANIFEST 记录 | ✅关闭(注:B/C/BLIND 大件仍在 /tmp 运行档+sha 在档;tmp 清理后以 judgment+FULL_REPORT+复算脚本可重放) |
| F06 | PPI≠投入成本口径;黄金 -0.30%/+0.48%、n=27/+0.07%、n=427/-0.361 不可复现仍挂已验证;CCC 走阔最大≠贡献占比;相关≠因果 | 金融解释与统计复算 | CON-3(B)PPI 条件推断降级+四点一个百分点中文数字;BLIND 桶值全量复算更正(美元桶 -0.428%/+0.671%,旧值作废注);A CON-3 走阔幅度排序(不称贡献份额);C +0.536 引文作废→事件事实 | 三席终审独立复算(B 25项/C 30+项/BLIND 全样本 n=2492)逐位吻合;n=427/-0.361 定性=冻结脚本 i=0 环绕伪值(正确 -0.382),列 NEW-2 下轮清偿,不再挂已验证 | ✅关闭 |
| F07 | main 保护未落地却可能被当已执行;须准确报告外部阻塞 | 治理面 | AUDIT_R1_F07_GOVERNANCE.md: 已验证(公开仓/默认main/CI#297绿/基线#296红→修复绿链)与未验证(分支保护: token 401+凭证探索被分类器拦)分离;配置已备(TARGET_PROTECTION_PREP.md);用户最小动作 2 件 | 未声称 ENGINEERING_GOVERNANCE_ENFORCED;§四 落地登记仍空=如实 | ✅关闭(配置就绪,落地待用户 3 分钟动作) |
| F08 | gate_b 并行 harness 循环外一次性提取旧锚点——两侧输入不同源 | 输入面不对齐 | `--anchors-data` 每报告一 vintage(extract_anchors_from_data(data_dir) 注入);缺省单一 vintage 如实注记 single_live_vintage(输入错代披露);行内 anchors_used 溯源 | 守卫 test_pc_phase2_gate_b_parallel §C(套件 17/0);迁移判据 MC1-MC4 冻结未动 | ✅关闭 |
| F09 | FULL_REPORT 只有事实表+路径,真分析在 report.md;缺一键全自动 | 装配不完整 | `_r1_report_core` 完整装配(L1 表+L2 摘编+L3/L4 **全文内联**+证据索引表+四态质量节);`--stage auto` 单命令链(plan→judgment 缺席=Agent Native 暂停点如实 rc=1→attach→report) | 新守卫 test_audit_r1_f09_fullreport(20/0)+四档真实面 FULL_REPORT 全节在场;auto 链暂停点/截链诚实 | ✅关闭 |
| F10 | 旧 BLIND 出题后被操作者注入方法提示——半优化不能写成 G4 已过 | 独立性 | 本轮重做: 独立验收席(未参与修复)自选题→原样投递→受测席自选方法→独立验收 | 【进行中: 出题席已派,题落 question_prereg.json;受测席+验收段见 §四】 | ⏳进行中 |

## 二、候选版本与变更摘要

- 基线 `c9d5715` → 修复链(本分支): `4b1e4ca`(F04b AST 迁移)→ `1656294`(F01-F09 全链收口+四档修订闭环终审)→ 【F10 完成后追一提交】
- 复核命令:
  ```bash
  git checkout dev/audit-fix-r1 && git rev-parse HEAD
  python3 tests/test_audit_r1_f09_fullreport.py   # F09 守卫 20/0
  python3 tests/test_pc_phase2_gate_b_parallel.py # F08 守卫 17/0
  # 全量: for f in tests/test_*.py; do python3 $f || echo RED $f; done  (185 件)
  ```

## 三、四档研究收口状态(修订闭环终审毕)

| 档 | 问题域 | judgment 终版 sha(前16) | 契约门 | 独立终审 | 四态终态 |
|---|---|---|---|---|---|
| A | UST_10Y→HY_OAS/SPX | `0d929aeed32873b4` | VERIFIED 11 检 | UPHELD(8项,残留1 NIT 列档) | **deliverable=True** |
| B | CN 信用/景气→创业板/FXI | `538c92f8845132bd` | VERIFIED 12 检 | UPHELD(6项) | **deliverable=False(如实)**: 底座 run_ok=False 诚实拒答降级(--allow-failed-run 显式),四态门拒发——门有牙实证非缺陷 |
| C | 美日政策分化→USDJPY | `82b26a72af0be0a0` | VERIFIED | UPHELD(7项,3既有 NIT 列档) | **deliverable=True** |
| BLIND | 黄金×实际利率×美元(盲测) | `afd04c693d1f561a` | VERIFIED 11/11 unbound=0 | UPHELD(12项,含 FIX-6/NEW-1 两项裁决后按席位复算值清偿;NEW-2/NEW-3 列档下轮) | **deliverable=True** |

- 裁决档: `audit/semantic_review/20261116/VERDICT-{045959Z,053224Z,053259Z,053623Z}-01.json`(R32 章程 schema: seat=semantic-audit-seat/UPHELD/counterexamples_sought/audited_at,B3-B5 机核 10/0)
- 修订链: 各档 MANIFEST.md「Audit-R1 修订记录」(旧→新 sha+逐项理由+标记形制映射);失败证据不覆盖(BLIND 旧 n=27/+0.07% 等以作废注留档)
- 标记形制(契约门 token 化发现): 扫描字段内用无数字「复审*」标记,数字形 Audit-R1 F0x 只进未扫描字段——映射表在各 MANIFEST

## 四、F10 真正未优化独立任务

**独立性协议(本轮重做,纠正旧 BLIND 半优化)**: 独立验收席(f10-acceptor-seat,**未参与任何修复**,独立性声明在档)自选新题并预注册期望(5 条,只存档不外泄)→问题逐字投递受测席(方法/窗口/分档全部受测席自选留痕)→同一独立席做 B 段验收。

- 出题: `docs/autonomous-rd/phase4/F10/question_prereg.json`(set_at 2026-11-16T11:46:43Z,候选 SHA 亲验一致;操作者废弃尝试的 run 目录已清理,无泄题面)
- 问题域: 布伦特原油(BRENT_F)大幅波动对美国长期通胀预期(BEI_10Y)的传导——减弱/锚定/时有时无(四旧题均未触及的序列组合)
- 受测席产物: 【进行中,完成后回填: 链路各段/自选方法/结论/证伪条件/judgment sha】
- B 段验收: 【待回填】

## 五、测试与 CI

- 本地全量(候选 1656294): **185 件套件,867 PASS / 0 FAIL,零 rc 失败**(含 F02 15/0、F03 12/0、F08 17/0、F09 20/0、席位章程 10/0、arch_reform_phase6 29/0)
- CI: main #297(36c1e7e)=success(py3.11);审计基线 #296=failure→修复绿链在 GitHub Actions 可复核;**候选分支 CI 未跑**——候选在 dev 分支,推送需授权(未推);外审可本地按 §二命令复核
- py3.12 面: AST ast.Constant 迁移已落(4b1e4ca);浮点末位/哈希差异=环境差异,金融阈值未放宽

## 六、G0—G4 判定(独立验收席裁定)

【待 F10 完成后由独立验收席裁定回填。操作者预核面: G0 标准=867/0+CI 链+目标契约未擅改+状态 Git 一致;G1=四档契约门+终审复算;G2=--stage auto 链+四档真实面;G3=三席终审全量复算逐位吻合;G4=四档+独立新题】

## 七、治理实际状态与外部清单

见 `AUDIT_R1_F07_GOVERNANCE.md`。已验证: 公开仓/默认 main/CI 链;未验证: 分支保护规则集(token 401+凭证探索被权限分类器拦截,如实不声称)。用户最小动作 2 件(规则集落地 3 分钟+落地后核验回填)。

## 八、恢复状态与 DEFERRED

- 恢复入口: 本报告+`RESUME.md` Audit-R1 检查点块(待 F10 后 finalize)
- DEFERRED(代码瘦身继续暂缓,未获授权不动):
  1. NEW-2: BLIND MECH-3 收窄日 -0.361→-0.382 + blind_calc2.py HY 段 i=0 环绕索引修(冻结脚本,定性稳健)
  2. NEW-3 四项精度 NIT(-0.535→-0.541 等)
  3. A 档 RES-01: MECH-2 环3 单月窗措辞与 SCN-A 固定基准口径统一
  4. B 档引擎观察: S4 no_series 补标 honest_refusal(R46 候选)
  5. C 档三项既有 NIT(约0.09/约5.1 叙事压缩、4600『其』绑定)
  6. F05 尾巴: B/C/BLIND 大件原件从 /tmp 迁入受控存储(--archive 正式归档重产)
  7. Gate B 迁移 MC1-MC4 判据面(裁定档/连续期,独立于本轮)
- 旧研发队列(R45+ 引擎轨道)保持暂停,未恢复。

## 九、最终七答(收口时回填)

【待 F10+验收席毕】
