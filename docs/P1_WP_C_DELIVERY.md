# IA-P1-WP-C 交付说明(DELIVERY)

- 工作包: IA-P1-WP-C(P1 四经济体底图层·经济体评分·装配·报告)
- 契约: IA-P1-WP-C-AC-v1.1(FROZEN,2026-11-06 02:5x HKT;附录A随开工提示词注入)
- 分支: dev/p1-impl-c(自 BASE-P1C=fcd0537c9ac4b66dcd8a52c6186e814121feaf5f 切出,纯线性)
- 尖端 SHA: 以 git 取证为准(证据包③;本件不含自引用尖端值——避免"提交内嵌自身 SHA"自指失实,先例沿 WP-B 报告头形态)
- 姊妹件: docs/P1_WP_C_REPORT.md(§零 登记+§一-§六 实录,事实基线以 REPORT 为准)

## §一 交付件清单与 git 面

| 类 | 文件 | 状态 |
|---|---|---|
| A1 | docs/P1_WP_C_REPORT.md | 新增(§零 开工登记+§一-§六 实录) |
| A2 | docs/P1_WP_C_DELIVERY.md | 新增(本件) |
| A3 | tests/test_p1_wp_c.py | 新增(14 用例,全合成数据源) |
| M-a | scripts/macro_scorecard.py | 修改(DP-3 economy 参数化: L38-41/L99-118/L200-216/L414-437/L484-487/L517-545/L577-616) |
| M-b | scripts/data_assembler.py | 修改(经济体观察节: L82-105/L267-320) |
| M-c | scripts/correlation_calculator.py | 修改(PAIRS+2 跨域对: L46-53) |
| M-d | scripts/report_generator.py | **零改动**(条件类判定成立,t13 固化;DESIGN L128 自动传导) |

diff 判据自评: `git diff --name-status fcd0537c..HEAD` 应=恰 3 行 A(A1-A3)+3 行 M(M-a/b/c)+0 行 D;report_generator 零 diff=条件类零改动(非遗漏)。分支=BASE 切出纯线性零 merge,不碰 main,零 force。

## §二 运行与验证摘要

- 本包测试: tests/test_p1_wp_c.py 14/14 绿(Ran 14 tests, OK;全合成 fixture,零网络零 GLM——t13 对 `_call_glm` 本地打桩,桩注入点=tests/test_p1_wp_c.py L403)。
- 本地 CI 镜像(2026-11-06): 72 槽=71 rc=0+1 rc=1;红=tests/test_phase3.py 单断言(L182 计数 9/1→9/3),根因=DESIGN L171 授权的 PAIRS 新对对白名单外既有测试的涟漪(根因隔离实证=证据包⑥;涟漪面=AC-07.7 登记发现不实施,REPORT §零.9 发现1/§二 偏离1)。71 rc=0 含 test_glm_live.py 设计性跳过面(exit 0)。
- 真实运行面: **零运行产物**(要点均【测试/CI】限定;data/daily 19 既有 JSON sha256 运行前后一致;零 GLM/零网络/零凭证/零付费)。

## §三 合同 AC 逐条自评摘要(全文自检=stdout 自述段4;判据细节=REPORT)

- AC-01 规格抄录与登记: 自评**过**(L171 逐字抄录+四要素+清单推导;审计对照权在审计侧)。
- AC-02 逐要点证据映射: 自评**过**(REPORT §五 映射 9 行无漏检,落点直读可核)。
- AC-03 测试与确定性验证: 条 1-4/6-7 自评**过**;条 5"本地逐套件全绿"自评**不满足**(test_phase3.py rc=1,涟漪根因+AC-07.7 处置登记;其余 71 套件 rc=0)——整条 AC-03 判定权留操作者/审计。
- AC-04 引用真实性: 自评**过**(file:line 引用以提交时工作树为准;基线 CI run 42082218620 标注注入转录非实取)。
- AC-05 范围/分支/生产隔离: 自评**过**(diff 恰 3A+3M+0D;零分支外操作;LIVE/launchd/引擎零触碰;零网络)。
- AC-06 CI 与证据包: 本地镜像已录;**GitHub CI dispatch=操作者 CHECKPOINT 面**(登记件将落 rounds/046/P1-WP-C-CI-dispatch-evidence.md);证据包八类成员+SHA256SUMS(自指豁免)=§四。
- AC-07 研究纪律: 自评**过**(特有纪律登记=REPORT §零.4;数据不足不填 0 实现于非 US 路径;零投资建议文案;零真实调用;白名单外发现登记不实施=§零.9)。

## §四 证据包登记

- 路径: /tmp/p1-wp-c-evidence/IA-P1-WP-C-EVIDENCE.zip(八类成员: ①规格抄录件+登记清单副本 ②交付文件双源副本(git 尖端版+工作树版,交叉哈希) ③git 取证原样输出 ④本地 CI 逐套件记录 ⑤逐要点证据映射表 ⑥真实运行面=「零运行产物」声明+data/daily sha256 锚定+涟漪隔离实证 ⑦自述报告副本+六项自检清单件 ⑧SHA256SUMS——清单自身显式豁免不塞入 zip,R019-D3)。
- zip 整体 sha256: **装配于本件提交之后**(先例沿 WP-B 8edfb68 两笔形态)——终值以装配 stdout+SHA256SUMS 旁挂件为准,回填登记见本仓库后续"证据包终笔"提交(纯线性追加,零 amend)。

## §五 漂移维护策略声明(AC-03.6 三要素)+fixture→预期值映射

1. **预期值唯一来源=仓库内版本化合成 fixture**: 本包测试一切期望值来源于 tests/fixt.py 合成载荷与 tests/test_p1_wp_c.py 内显式发明值([示意]标注),不依赖 data/daily 真实档。
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: fixt.py 若演进(如 WP-A v1.3 先例),依赖其数值的断言(t05 UMCSENT=68.0→0 分;t09 JPY=X=152.4/EURUSD=1.163)须同 commit 勘正;fixture 路径锚定: fixt.py L40(collector_payloads)/L152(UMCSENT 68.0)/L80-82(EURUSD/JPY=X)。
3. **真实数据档永不进入测试预期值来源**: 测试零读取 data/daily(渲染面 t07/t14 走临时目录注入);真实档(jp_20261105.json 等)仅 REPORT 文字引用,不入断言。

fixture→预期值映射(逐断言组→定义处):

| 断言组 | fixture/发明值定义处 | 预期值断言处 |
|---|---|---|
| t01-t04 维度评分 | tests/test_p1_wp_c.py L60-101(_fact/_us_full_facts,发明值) | L93-138 |
| t05-t06 存档/标题 | fixt.py L291-297(write_collectors)+L152 | tests/test_p1_wp_c.py L167-227 |
| t07-t08 经济体节 | fixt.py L60-276(7通道)+config/metric_registry.json(计数实取) | L241-277 |
| t09-t10 Gate B | fixt.py L80/L82+registry source 字段 | L282-322 |
| t11-t12 相关性 | scripts/correlation_calculator.py L28-53(字面)+tests L344-388(发明序列) | L331-388 |
| t13 报告 prompt | da.build_markdown 输出+桩捕获(注入点 L403) | L393-420 |
| t14 既有链路 | fixt.py L329-390(build_full_day) | L426-440 |

## §六 如实偏差与 PENDING

1. **test_phase3.py 涟漪红**(§二): PENDING 操作者——授权单行勘正(L182 `== 1`→`== 3`)或改派;本包不越白名单。
2. REPORT §零 三处登记勘误(实现前,注记保留原文): PAIRS 字段名/sources_status 表述/legacy 键 19。
3. t02 期望值手算勘正(WTI 档位,实现零改动)。
4. 上游延后面(WP-B F1/F2): NIKKEI/DAX 序列与 jp/ea facts 未接线——本包以如实缺席呈现(设计内形态),接线属后续包。
5. AC-03.7 外部调用面合成桩: **条件适用判定=不适用**——登记清单无外部服务调用面实现(四 M 件+三 A 件均确定性本地模块);t13 的 _call_glm 桩=对既有调用面的测试打桩(测 t13 一处),非本包新增调用面实现,注入点(L403)已登记。
6. **取证表述失实一处族(步骤12 发现,取证更正笔处置)**: REPORT 对 049ec978 误记为 blob、抄录命令漏 `:docs/P1_DESIGN.md` 路径限定(7 处)——实测=commit(设计分支尖端,其内 DESIGN blob=13b263cf…);抄录内容与"设计在场"结论经正确命令复核均成立。全记录=REPORT §零.12,原文划线保留+更正指针;本笔=REPORT+本件两 docs 零代码面。

## §七 参考

- 契约: IA-P1-WP-C-AC-v1.1(开工提示词附录A注入;contracts/ 存档=引擎侧不可达,有效性以冻结章实物化为准)
- 设计: docs/P1_DESIGN.md(blob 049ec978;§六 L171 规格行、L30 DP-3、L68 §三a-5、L128 §四 L5)
- 上游: docs/P1_WP_A_REPORT.md、docs/P1_WP_B_REPORT.md(工作树在场)
- CI: .github/workflows/offline-tests.yml(零改动)
