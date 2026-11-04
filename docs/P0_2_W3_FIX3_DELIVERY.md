# P0-2 W3-FIX3 交付报告（新闻信任边界 · 正式引用位置认证）

任务编号: IA-P0-2-W3-FIX3 ｜ 指令: IA-P0-2-W3-FIX3-DEV-v1.0 ｜ 冻结契约: IA-P0-2-W3-FIX3-AC-v1.0
开发分支: dev/p0-2-w3（不合并 main，不部署 Mac LIVE）

---

## 1. 基线与固定Commit

| 项 | 值 |
|---|---|
| W3-FIX2失败验收Commit（增量基线，CI 41066868478/42套绿但IA-P02-W3-FIX2-DEF-001未关闭→验收失败） | `e3d6b673f75f35caf9ca3ecae287e4edf87a0733` |
| FIX3实现Commit | `d1a4540c31b5fe1263900ec94fc7ebcb14559499` |
| FIX3最终固定Commit | 本交付文档所在Commit（docs回填；完整SHA与两轮CI编号见Git外隔离证据与对话交付报告——文档无法预知自身Commit SHA，防预写纪律，W2/W3/FIX1/FIX2同法） |
| FIX3增量Diff | `git diff e3d6b67..HEAD` — 4文件 +178/−26（news_provenance.py +93/−1, news_collector.py 校验重写, report_generator.py 消费端 +23/−2, test_p02_w3_fix2.py K3修订）+ 新增tests/test_p02_w3_fix3.py（26检查项） |
| W3累积Diff | `git diff 14fe6e5..HEAD` — 11文件 +3225/−124 |
| 封版链 | P0-1 `50b5d13` → W1 `69d7fc7` → W2 `14fe6e5` → W3首轮 `778050c` → W3-FIX1 `522ca13` → W3-FIX2 `e3d6b67` → **W3-FIX3（本Commit）** |

## 2. 唯一缺陷定位（IA-P02-W3-FIX2-DEF-001）

正式周报 `load_news_summary()` 以 `extract_citations(merged)` 对整个新闻Markdown做**全文任意位置**ID搜索——正文/标题/不合格条目行中的合法格式ID一律被当作可信引用。固定反例：`- [art_A] Fed holds rates [art_B]`（A行首合法、B正文夹带，A/B均有通过完整性验证的真实档案）→ 旧代码把A、B都认证。本轮只关闭此缺陷，不重开任何已通过能力。

## 3. FIX3-01｜正式引用位置解析器（§四）

`news_provenance.parse_news_item_references(text)`（严格逐行解析，与档案Schema/数据库无关）：
- 合法条目=单行顶格 `NEWS_ITEM_RE = ^-\s+\[(art_[0-9a-f]{16})\](?=\s|$)`——行首引用槽位，ID后必须紧跟空白或行尾；
- 结构化输出：`items`（逐条目 line_no/article_id/body/extra_body_ids/status）、`legal_ids`（合法槽位ID去重保序）、`illegal_ids`（非法位置ID）、`anomalies`（body_extra_ids与illegal_position两类，各含reason/action）、`ok`；
- §4.3固定反例：A=合法槽位、B=body_extra_ids（不进入legal_ids）；§4.5边界：`### 美联储/利率 [art_B]`标题、`The article [art_B] …`正文、`- Fed holds rates [art_B]`不合格条目行——全部illegal_position，不取得引用资格；
- 旧 `extract_citations()` **保留但明确降级**为诊断级宽松文本搜索（docstring声明不得作为可信引用判定入口/模型摘要校验），签名与行为不变（FIX1/W3既有测试零改动依赖它做诊断断言）。

## 4. 宽松全文提取 vs 正式解析的接口区别（§十四.5）

| | `extract_citations`（诊断级） | `parse_news_item_references`（正式） |
|---|---|---|
| 匹配范围 | 全文任意位置`[art_xxx]` | 仅新闻条目行首引用槽位 |
| 位置区分 | 无 | legal/illegal结构化分流+异常原因 |
| 正式认证入口 | **禁止**（FIX3-03） | 唯一判定基础（生成端+消费端共用） |
| 允许集合核验 | 无（仅提取） | 由消费端叠加（validator/档案核验） |

## 5. FIX3-02｜模型摘要引用校验统一（§五）

`validate_summary_citations()` 重写为以解析器为共同基础（不再全文搜索）：
1. 至少一个合法行首槽位ID（整篇无有效引用→失败）；2. 输出中**全部**[art_]ID（含夹带/非槽位）∈允许集合（虚构/超范围→失败）；3. 每条'-'条目行必须符合正式语法（`- Fed … [art_A]`位置错误→'不在行首槽位'失败；无引用条目行→失败）；4. **正文夹带额外[art_]→失败——即使夹带ID在允许集合内**（B真实存在也不得成为A的第二来源）。
失败路径不变：一次受控重试（【重要修正】+具体problems）→二次失败→FIX1/FIX2已通过的确定性标题回退（回退行`- [art_xxx] 标题`天然符合槽位语法）。不依赖提示词保证（提示词未改动语义，仅校验器收紧）。

## 6. FIX3-03｜周报正式来源消费（§六）

`load_news_summary()` 停止 `extract_citations(merged)` 全文认证，改为：
1-3. 既有读取/脱敏/去重/裁剪（9000上限与保新弃旧逻辑零改动）；4. 对**最终保留文本**严格位置解析（引用集合与实际进入周报新闻输入严格对应——被裁掉一天的引用不进附录，测试K1以"被裁引用有真实档案却不被认证"实证）；5-8. legal_ids → `load_trusted_articles_since`（FIX1可信原始档案根不变）→ 逐ID档案再核验 → 仅双重通过者进附录；9. 非法位置ID不认证，附录追加无方括号诊断行（`⚠️ 诊断: …不构成可信引用,未列入来源索引`，不可被再提取为引用）+ 控制台逐ID诊断。
§6.3反例实测：A独立认证（附录A行+A URL）、B零认证（无附录行/无B URL/合法槽位集合=[A]）；§6.4：B独立条目`- [art_B] Treasury yields rise`正常认证，不因曾夹带被永久禁止；§6.5：旧摘要无ID→可读取零附录；档案不存在→'未通过来源认证'，不从news_refs自认证（FIX1根不变）。

## 7. 来源档案可信链继承（§十四.10）

批次排他创建+清单事务/逐档案verify_archive/`load_trusted_articles_since`实时重建（档案→清单→文件SHA-256→逐记录摘要→ID映射）/`verify_citation_trusted`——全部零改动继承；本轮解析器只决定**哪些ID有资格进入认证流程**，认证本身仍以原始档案为唯一可信根。

## 8. 旧K3测试修订（§七/FIX3-04）

`tests/test_p02_w3_fix2.py` K3原断言"真实load_news_summary把B误认证入附录"验证的是FIX2缺陷本身——不得在新正确版本中继续要求错误行为为True。修订为**K3a**（FIX3代码下：B不进可信附录/A行首独立认证/夹带记为body_extra_ids异常）+ **K3b**（人为恢复FIX2宽松全文解析→B再次被错误认证→证K3a对该退化敏感）。场景保留、未删除、断言收紧。W3(38)/FIX1(44)零改动；FIX2其余24项零改动。

## 9. 专项测试（§八，tests/test_p02_w3_fix3.py，26检查）

A 两篇真实文章（归档+verify_archive+可信集合）；B 固定反例（真实load_news_summary只认证A+诊断）；C 独立合法条目双向对照；D 校验拒正文夹带（B在允许集合内）+真实generate路径重试→回退；E 位置错误拒绝；F 无引用重试+回退；G 虚构ID拒绝；H 档案不存在不认证；I 档案SHA损坏→未通过认证+完整性告警；J 旧摘要无ID零附录；K 七天聚合/跨天去重/超长裁剪对应（被裁引用有档案仍不认证，保留引用仍认证）；L 恶意标题回退安全（解析零异常/伪ID不成为引用）；**M 负向敏感性**：M1消费端恢复`extract_citations(merged)`宽松解析→B被错误认证（B2必失败）；M2校验恢复"行内任意允许ID即过"→位置错误输出被直接保存（D/E必失败）。全部走真实模块（解析器/validate/generate/load_news_summary），零正则复制品自证。

## 10. 正式联合E2E（§九12项）

E2E-A（成功链，真实研究链）： 合法采集→原始档案保存→完整性认证→GLM成功恰1次输出合法行首引用→摘要保存→正式周报从真实摘要加载来源→合法来源进入周报输入（提示词含来源索引+A认证URL）→篡改摘要注入B正文夹带后B虽有真实档案仍不被认证（附录无B行/无B URL/A独立认证+诊断）→Gate A PASS+Gate B PASS+published+主状态digest==正式文件摘要→thesis/views零污染。
E2E-B（降级链）： 新闻全败→正式研究链exit0+GLM恰1次+published+Gate A/B PASS+无[art_]认证——金融事实门禁不因新闻改变。外部Finnhub/RSS/GLM全Mock。

## 11. 不得重新开发清单核对（§三）

新闻原始字段保存/RSS UTC/批次排他创建及清单保护/可信原始来源实时重建/Finnhub四态/跨通道关联/原始与脱敏输入隔离/多行标题单行化/GLM异常安全回退/无引用受控重试/旧摘要兼容/非关键降级/P0-1·W1·W2全部回归——全部保留（43套件exit=0实证）；批次不可覆盖机制、Finnhub状态机、sanitize_model_text/_fallback_headlines已通过语义零触碰。

## 12. 全量历史回归（本地）

**43套件全部exit=0**（42原有+新增test_p02_w3_fix3；test_glm_live按契约跳过）: W3 38/38、W3-FIX1 44/44、W3-FIX2 26/26（K3修订为K3a/K3b，25→26检查）、W3-FIX3 26/26、W2/FIX1~6、W1/W1-FIX1、P0-1 FIX1~11、原始14项E2E/四周/冻结14、Gate链、fact_engine、snapshot、P0/P1/P2/P4/P7、phase3/4、round3~6、datafix。旧预期调整仅FIX2-K3一处，已附理由（§8）。

## 13. GitHub Actions CI（workflow_dispatch, offline-tests.yml, ref=dev/p0-2-w3）

| 轮 | Run ID | Job ID | head_sha | 结论 |
|---|---|---|---|---|
| run#1（实现Commit d1a4540） | 41094138222 | 124195383646 | d1a4540c31b5fe1263900ec94fc7ebcb14559499 | success, 43套件全部exit=0（含test_p02_w3 38/38、fix1 44/44、fix2 26/26、fix3 26/26;glm_live按契约跳过;逐套件清单见Git外附件） |
| run#2（最终固定Commit） | 防预写： 编号/Job ID/head_sha/逐套件退出码在最终Commit推送后运行，实证结果见Git外隔离证据附件与对话交付报告，不写入仓库 | — | 最终固定SHA（=run#2 head_sha） | 见Git外证据 |

FIX2的42套绿色CI（41066868478）不作为本轮执行证据；run#2在最终固定SHA上实际运行。

## 14. 工程边界遵守（§十）

只改动: scripts/news_provenance.py（引用解析部分+extract_citations文档降级）、scripts/news_collector.py（validate_summary_citations）、scripts/report_generator.py（load_news_summary消费段）、tests/test_p02_w3_fix2.py（K3修订）、tests/test_p02_w3_fix3.py（新增）、docs/P0_2_W3_FIX3_DELIVERY.md。未触碰: 档案Schema、批次不可覆盖及清单事务、Finnhub状态机、RSS UTC、sanitize_model_text、原始摘要与安全回退、81项指标政策、Gate A/B、P0-1/W1/W2封版、W4/W5/P0-3、Mac LIVE、launchd、生产data/news、正式周报、长期状态、生产密钥、真实付费GLM、main分支、force push。

## 15. 最终DEV/LIVE隔离证据（Git仓库外审计材料）

`/Users/cast/audit/IA-P0-2-W3-FIX3-POSTCOMMIT-ISOLATION-<最终SHA前7位>.txt` — 最终Commit与CI run#2之后执行；含核验时间/DEV HEAD/realpath+inode/origin/main/launchd路径与工作目录/LIVE关键源码与P0-1封版50b5d13 SHA-256逐文件对照/W3全部新模块及开发测试（含fix3产物）未部署LIVE/生产长期状态只读元数据/无法证明事项如实标注。证据正文在对话中完整输出（脱敏，无生产密钥/私人状态正文），实际送达供Agent 4读取。

## 16. 未验证事项

- 真实GLM对行首槽位约定的遵守率（本轮全Mock；不要求真实付费调用）。
- 恶意混合内容在真实多源RSS/多语言标题下的解析器覆盖面（测试锚定八类位置形态+多行边界继承FIX2）。
- FIX3交付后的Agent 4独立工程验收结论（本报告不自宣PASS）。

## 17. 结论声明

**READY FOR W3 INDEPENDENT ACCEPTANCE**——W3是否通过、P0-2是否完成由Agent 4独立工程验收决定；不自行宣布W3 PASS、不合并main、不部署Mac LIVE。

---
*回填说明: 实现Commit（代码+测试）先行推送并完成CI run#1实证后，本文档回填run#1实数形成最终固定Commit；run#2对本Commit运行，其编号按防预写纪律只入Git外审计附件与对话交付报告。此后零新提交，固定SHA不变。*
