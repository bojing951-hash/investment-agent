# P0-2 W3-FIX5 交付报告（新闻信任边界 · 围栏开闭语法CommonMark修正）

任务编号: IA-P0-2-W3-FIX5 ｜ 指令: IA-P0-2-W3-FIX5-DEV-v1.0 ｜ 验收契约: IA-P0-2-W3-FIX5-AC-v1.0
开发分支: dev/p0-2-w3（不合并 main，不部署 Mac LIVE）

---

## 1. 基线与固定Commit

| 项 | 值 |
|---|---|
| W3-FIX4失败验收Commit（增量基线，CI 41168062441/44套绿但IA-P02-W3-FIX4-DEF-001未关闭→验收失败） | `e8b9e354c85f1078591545cb04ab4c56327fe198` |
| FIX5实现Commit | `8bc7261bf4a88b05c8ddab759b57b03b0b173043` |
| FIX5最终固定Commit | 本交付文档所在Commit（docs回填；完整SHA与两轮CI编号见Git外隔离证据与对话交付报告——防预写纪律，W2/W3/FIX1~4同法） |
| FIX5增量Diff | `git diff e8b9e35..HEAD` — scripts/news_provenance.py +19/−14（仅`_fence_open`/`_fence_close`及必要docstring）+ 新增tests/test_p02_w3_fix5.py（33检查项,566行） |
| W3累积Diff | `git diff 14fe6e5..HEAD` — 15文件（W3/…/FIX5全部,含本文档） |
| 封版链 | P0-1 `50b5d13` → W1 `69d7fc7` → W2 `14fe6e5` → W3首轮 `778050c` → FIX1 `522ca13` → FIX2 `e3d6b67` → FIX3 `ea93618` → FIX4 `e8b9e35`（Agent 4判验收失败）→ **W3-FIX5（本Commit）** |

## 2. 两项围栏语法错误（IA-P02-W3-FIX4-DEF-001，§十二.4）

Agent 4判定FIX4失败的两项确定性缺陷（本轮唯一核心任务，不重新设计Markdown系统）：
1. `_fence_open()`错误禁止合法波浪号围栏info中含`~`——`~~~ python ~edition`被误判为非围栏开栏，围栏内`- [art_B]`逃出围栏上下文被当普通新闻条目；
2. `_fence_close()`以`body = s.strip(' ')`处理关栏行——不能移除尾随`\t`，合法的```` ``` ````+TAB关闭标记无法关闭围栏，围栏吞掉其后全部正常新闻（A被错误丢失）。

## 3. CommonMark规则依据（§十二.5）

CommonMark规范（Fenced code blocks）：info串限制**仅适用于反引号围栏**——"Info strings for backtick code blocks may not contain backticks"（防与行内代码歧义）；规范示例`~~~ aa ``` ~~`（info=`aa ``` ~~`，含波浪号与反引号）是合法波浪号围栏。关闭围栏为"可缩进至多3个空格、其后可跟尾随空白（空格与制表符）的同字符≥开栏长度标记"。FIX4把反引号info限制错误对称应用到波浪围栏（缺陷①），且尾随空白处理只覆盖空格漏掉TAB（缺陷②）。

## 4. FIX5-01｜`_fence_open()`修复（§十二.6）

移除`if ch == '~' and '~' in info: return None`错误禁令（其余零改动）：
- 反引号围栏info不能包含反引号（CommonMark限制，保持）；
- 波浪号围栏info**可以**包含波浪号、**可以**包含反引号；
- ≥3个相同围栏字符、最多3个前导空格既有规则原样保留（`~~python`/`    ````仍非围栏）。
docstring同步修正并注明规则依据与FIX4错误来源。

## 5. FIX5-02｜`_fence_close()`修复（§十二.7）

行首缩进与行尾空白独立处理：
```python
lead = len(s) - len(s.lstrip(' '))
if lead > 3:
    return False
body = s[lead:].rstrip(' \t')
return bool(body) and set(body) == {ch} and len(body) >= length
```
- 尾随普通空格、制表符及混合均合法（```` ```\t ````/```` ```  \t \t ````合法关栏）；
- **未**改成`body = s.strip(' \t')`——那会移除行首制表符，错误接受前导TAB缩进的关栏（`\t``` `仍拒，`   \t``` `仍拒）；
- 关栏后含非空白文字/长度短于开栏/字符不匹配仍全部拒绝；0-3前导空格继续合法。

## 6. 共享围栏语义验证（§六FIX5-03，零额外修改）

`markdown_fence_map()`/`strip_code_fences()`/`parse_news_item_references()`/`validate_summary_citations()`/`load_news_summary()`**全部零改动**——本轮只修两个底层函数，按§六验证顺序逐层实证全部调用端自动获得正确语义： ①开栏正确（反例A第一行`('~,3)`）②关栏正确（反例B第三行关闭）③fence_map逐行标识正确（两种形态均[True,True,True,False]）④strip仅剔除真实围栏3行 ⑤解析器只识别围栏外合法ID（legal=[A]，B进excluded_context）⑥校验不认证围栏内B（仅围栏B→'合法引用槽位为空'失败）⑦周报不洗白B（B行/B URL零出现）⑧原始档案完整性验证继续生效（C0前提+E9）。**report_generator.py与news_collector.py本轮零修改。**

## 7. 固定反例A：合法波浪号信息字符串（§十二.8）

真实文章A/B（项目规范化流程核发真实16位hex ID，真实save_batch→verify_archive→load_trusted_articles_since双档案在可信集合）。摘要含`~~~ python ~edition`围栏内`- [art_B] 代码示例`+围栏外`- [art_A] 合法新闻`：
- 解析: `legal_ids==[Aid]`，B在excluded_context(kind='fenced')，不进illegal_ids；
- 周报（真实load_news_summary）: B整行与B URL不出现在输出任何位置；A保留并正常进入可信来源附录（A行+A URL正确）；**没有因围栏误判删除A**。

## 8. 固定反例B：尾随TAB关闭围栏（§十二.9）

摘要含```` ```python ````围栏（内`- [art_B] 代码示例`）+```` ``` ````+实际TAB关闭+围栏外`- [art_A] 合法新闻`：
- 解析: 关闭标记合法→`legal_ids==[Aid]`，B排除——**不能错误丢失A**；
- 周报: B行/B URL不出现；A保留+附录认证（A行+A URL）。

## 9. 非法前导TAB反向测试（§十二.11）

B5/B6: `\t``` `与`   \t``` `（前导TAB缩进的关栏）均拒绝；F3负向敏感性证明: 若错误使用整行`strip(' \t')`，`\t``` `被当关栏（fence_map在TAB行提前关闭、其后内容逃出围栏、逃逸行被当普通条目入legal）——正确实现中围栏持续到EOF。B4/B6同时保持: 关栏后非法文字拒/长度不足拒/字符不匹配拒/0-3前导空格与尾随普通空格继续允许。

## 10. A/B原始档案正向认证与周报结果（§十二.10）

C0: A/B双档案真实归档（代码核发ID与stable_article_id预计算一致）、逐批次verify_archive通过、均在load_trusted_articles_since可信集合、无failed_batches——B档案真实存在不构成放行理由。CA2/CB2: 周报侧A行+A URL入附录、'未通过来源认证'不在、B零认证。E9: 档案SHA-256损坏→'未通过来源认证'+完整性告警（完整性链继续生效）。

## 11. 模型与周报共享围栏语义（§十二.12）

D组（真实validate_summary_citations）: 仅围栏B（波浪info形态与尾随TAB关栏形态）→'合法引用槽位为空'失败；围栏B后正常A（两形态）→通过且B不取得来源资格；普通合法新闻（无围栏）→不回归通过。生成端与消费端继续共用`markdown_fence_map`单一实现（FIX4架构零改动，本轮仅修正其底层开闭规则）。

## 12. 专项测试（§七，tests/test_p02_w3_fix5.py，33检查）

A组开栏6（真实`_fence_open`）｜B组关栏6（真实`_fence_close`）｜C组真实固定反例5（C0前提+CA1/CA2/CB1/CB2全链路）｜D组模型校验3｜E组历史回归10（E1 FIX3正文夹带/E2普通反引号围栏/E3普通波浪围栏/E4未关闭围栏/E5跨日独立/E6七天窗口+跨天去重/E6b超长裁剪保新弃旧/E7 GLM安全回退/E8全败非关键降级/E9档案完整性）｜F组负向敏感性3。全部走真实模块（围栏函数/解析器/校验器/真实周报/真实档案链），未复制围栏实现到测试自证。

## 13. 负向敏感性（§七F）

F1恢复错误`if ch=='~' and '~' in info`禁令→围栏不再开栏，B进legal_ids且真实周报将B洗白认证（B URL入附录）→CA1/CA2必败；F2恢复旧`strip(' ')`→```` ``` ````+TAB不再关栏，围栏吞掉其后内容，legal为空且真实周报丢失A（无A行无A URL）→CB1/CB2必败；F3错误整行`strip(' \t')`→非法前导TAB被当关栏（fence_map提前关闭/逃逸行入legal）→B5断言必败。第4项（周报错误认证B或丢失A→测试失败）由F1/F2的真实load_news_summary断言直接覆盖。

## 14. 全量历史回归（§九）

本地**46套件全部exit=0**（45既有+新增test_p02_w3_fix5;test_glm_live按契约跳过且exit=0）: W3 38/38、FIX1 44/44、FIX2 26/26、FIX3 26/26、FIX4 35/35、**FIX5 33/33**、W2/FIX1~6、W1/W1-FIX1、P0-1 FIX1~11、原始14项E2E/四周/冻结14、Gate链、fact_engine、snapshot、P0/P1/P2/P4/P7、phase3/4、round3~6、datafix。**零旧测试删改、零预期弱化**（本轮无任何既有断言变更——FIX4测试不依赖被修正的两处错误行为，全部原样通过）。CI（workflow排除test_glm_live）45套件。

## 15. GitHub Actions CI（workflow_dispatch, offline-tests.yml, ref=dev/p0-2-w3）

| 轮 | Run ID | Job ID | head_sha | 结论 |
|---|---|---|---|---|
| run#1（实现Commit 8bc7261） | 41172514461 | 124453289848 | 8bc7261bf4a88b05c8ddab759b57b03b0b173043 | success, 45套件全部exit=0（含test_p02_w3 38/38、fix1 44/44、fix2 26/26、fix3 26/26、fix4 35/35、**fix5 33/33**;test_glm_live按workflow契约排除;逐套件清单见Git外附件） |
| run#2（最终固定Commit） | 防预写: 编号/Job ID/head_sha/逐套件退出码在最终Commit推送后运行，实证结果见Git外隔离证据附件与对话交付报告，不写入仓库 | — | 最终固定SHA（=run#2 head_sha） | 见Git外证据 |

FIX4的44套绿CI（41168062441）不作为本轮执行证据（其不含fix5专项，且FIX4验收失败原因是DEF-001两处围栏语法错误而非CI缺陷）；run#2在最终固定SHA上实际运行。

## 16. 工程边界遵守（§八）

只改动: scripts/news_provenance.py（**仅`_fence_open`/`_fence_close`两个函数及docstring，+19/−14**）、tests/test_p02_w3_fix5.py（新增）、docs/P0_2_W3_FIX5_DELIVERY.md（本文档）。零改动: scripts/report_generator.py、scripts/news_collector.py、markdown_fence_map/strip_code_fences/parse_news_item_references（本体）、原始档案Schema、批次排他写入、Finnhub状态机、GLM调用与回退、金融指标时效策略、Gate A/B、P0-1/W1/W2封版、既有FIX3/FIX4测试、W4/W5/P0-3、Mac LIVE、launchd、生产data/news、正式报告与长期状态、生产密钥、真实付费GLM、main分支、force push。

## 17. 最终DEV/LIVE隔离证据（Git仓库外审计材料）

`/Users/cast/audit/IA-P0-2-W3-FIX5-POSTCOMMIT-ISOLATION-<最终SHA前7位>.txt` — 最终Commit与CI run#2之后按§十一顺序执行；含核验时间/DEV Git根/HEAD/分支与工作区/远程main与dev真实SHA/DEV-LIVE realpath+inode/关键文件symlink与同inode交叉/launchd程序与工作目录/LIVE核心源码与P0-1封版50b5d13逐文件SHA-256对照/W3系全部新模块及开发测试（含fix5产物）在LIVE缺席/生产报告与长期状态只读元数据/核验限制如实标注。FIX4隔离证据（e8b9e35时点）只证明FIX4最终时点，本轮新最终Commit后重新取证。证据正文在对话中完整输出（脱敏），实际材料由用户直接交Agent 4；此后不再产生新Commit。

## 18. 未验证事项

- 真实GLM输出中自发使用波浪info含波浪号/尾随TAB关栏形态的实际频率（本轮全Mock；不要求真实付费调用）。
- 超出本轮两处修正范围的其他CommonMark围栏边角（如围栏内嵌围栏标记的info解析顺序）——本轮按指令不重新设计Markdown系统。
- FIX5交付后的Agent 4独立工程验收结论（本报告不自宣PASS）。

## 19. 结论声明

**READY FOR W3 INDEPENDENT ACCEPTANCE**——W3是否通过、P0-2是否完成由Agent 4独立工程验收决定；不自行宣布W3 PASS、不合并main、不部署Mac LIVE。

---
*回填说明: 实现Commit（代码+测试）先行推送并完成CI run#1实证后，本文档回填实现SHA与run#1实数形成最终固定Commit；run#2对本Commit运行，其编号按防预写纪律只入Git外审计附件与对话交付报告。此后零新提交，固定SHA不变。*
