# P0-2 W3-FIX4 交付报告（新闻信任边界 · Markdown代码围栏上下文）

任务编号: IA-P0-2-W3-FIX4 ｜ 指令: IA-P0-2-W3-FIX4-DEV-v1.0 ｜ 冻结契约: IA-P0-2-W3-FIX4-AC-v1.0
开发分支: dev/p0-2-w3（不合并 main，不部署 Mac LIVE）

---

## 1. 基线与固定Commit

| 项 | 值 |
|---|---|
| W3-FIX3失败验收Commit（增量基线，CI 41094628715/43套绿但IA-P02-W3-FIX3-DEF-001未关闭→验收失败） | `ea93618907b1a791fa66d67a890daca475649d32` |
| FIX4实现Commit | `c5ce8d4e45eb5d6a2138fe5817bdc6e326959378` |
| FIX4最终固定Commit | 本交付文档所在Commit（docs回填；完整SHA与两轮CI编号见Git外隔离证据与对话交付报告——文档无法预知自身Commit SHA，防预写纪律，W2/W3/FIX1~3同法） |
| FIX4增量Diff | `git diff ea93618..HEAD` — 3文件 +169/−28（news_provenance.py +118/−7 围栏识别器+解析器围栏上下文, news_collector.py +23/−9 校验围栏感知, report_generator.py +28/−12 周报先剔围栏）+ 新增tests/test_p02_w3_fix4.py（35检查项,797行） |
| W3累积Diff | `git diff 14fe6e5..HEAD` — 12文件（W3/…/FIX4全部） |
| 封版链 | P0-1 `50b5d13` → W1 `69d7fc7` → W2 `14fe6e5` → W3首轮 `778050c` → W3-FIX1 `522ca13` → W3-FIX2 `e3d6b67` → W3-FIX3 `ea93618`（Agent 4判验收失败）→ **W3-FIX4（本Commit）** |

## 2. 唯一缺陷定位（IA-P02-W3-FIX3-DEF-001，两环节）

Agent 4判定: Markdown代码块内的`- [art_ID]`被错误识别为合法新闻条目引用。两个独立环节共同造成：
- **环节①（解析器）**: `parse_news_item_references`逐行解析时不维护代码围栏上下文——围栏内的`- [art_B] 代码示例`行与普通新闻条目行在语法上不可区分，直接取得行首槽位引用资格；
- **环节②（周报过滤）**: `load_news_summary`以`sanitize_news(content)`直接过全文——板块过滤器丢弃围栏标记行（不属白名单板块）却保留围栏内`- [art_…]`样式行，围栏上下文在正式解析之前已被销毁，代码块内假新闻被"洗白"成普通新闻。
两环节必须同时修复；本轮只关闭此缺陷，不重开任何已通过能力。

## 3. FIX4-01｜共享围栏语义与解析器围栏上下文（§四）

`news_provenance.py`新增四个函数（CommonMark最小确定性子集，共享单一实现——解析器与周报过滤**共用同一围栏语义，不得两套不一致正则**）：
- `FENCE_OPEN_RE = ^ {0,3}(`{3,}|~{3,})`——**不止`line.startswith("```")`**；`_fence_open(line)`: 0-3空格前导（>3空格=缩进代码块，非围栏）+≥3连续反引号或波浪号+可选语言标签info串；反引号围栏info不得再含反引号、波浪围栏info不得再含波浪号；返回(围栏字符,长度)或None；
- `_fence_close(line,ch,length)`: 同字符且长度≥开栏长度、仅0-3空格前导与尾随空白、关栏行不得带info——字符不匹配（```` ``` ````↔`~~~`）或关栏更短都不是关栏（围栏继续）；
- `markdown_fence_map(text)`: 返回与`splitlines()`等长的`List[bool]`（True=开栏/内容/关栏行）；**未关闭围栏状态持续到文档结束**；**文档级状态**——每个news_summary_YYYYMMDD.md独立调用，未关闭状态绝不跨文件携带（§5.3）；
- `strip_code_fences(text)`: 剔除围栏区域行后的文本（供周报消费端在板块过滤/脱敏**之前**调用）。
`parse_news_item_references`重写为围栏感知： `raw_lines=splitlines()`+`fence=markdown_fence_map(text)`，围栏行→`fenced_lines`行号记录+围栏内含[art_]ID或条目样式的行进`excluded_context`（kind='fenced'，确定性诊断）后`continue`。**围栏内ID绝不进入legal_ids**（也不进illegal_ids/不产异常——围栏内容不是新闻上下文，属"排除上下文"而非"非法位置"，保证A+围栏B的合法输出整体通过）。返回结构**新增**`excluded_context`/`fenced_lines`两个字段，`items/legal_ids/illegal_ids/anomalies/ok`原有语义零改动（§四兼容要求）。

## 4. FIX4-02｜周报过滤顺序修正（§五）

`report_generator.load_news_summary`正确顺序落地: **原始→识别代码区域→排除非新闻代码内容→板块过滤/脱敏→去重→七天聚合→长度裁剪→正式合法引用解析→原始来源认证**。
实现: `safe_content = news_provenance.strip_code_fences(content)`先于`sanitize_news(safe_content)`——围栏标记行与围栏内容在板块过滤之前整段剔除，围栏内假新闻不存在"被过滤洗白"路径；每个日文件独立处理（未关闭围栏只吞本文件）；解析后`excluded_context`非空时控制台打印确定性诊断行（含围栏内[art_]ID计数，不入附录）。**保持不变**: 7天加载/板块白名单/敏感过滤/跨天去重/9000上限/保留新日期/引用ID/确定性附录/旧摘要兼容（无ID→零附录）/来源损坏如实降级——不为代码块问题禁用整份摘要。

## 5. FIX4-03｜模型输出校验围栏感知（§六）

`news_collector.validate_summary_citations`继续以`parse_news_item_references`为唯一判定基础（继承FIX3-02），最小调整三点：
1. **仅代码块内B（即使在允许集合）不得判为具备合法新闻引用**——围栏行不是新闻条目，整篇只剩围栏引用→"合法引用槽位为空"→进既有校验失败处理（一次受控重试→二次失败FIX1/FIX2确定性回退）；
2. 无引用条目行循环以`markdown_fence_map(summary)`跳过围栏行（围栏行不按"无引用条目"计）；
3. **虚构检测覆盖全文ID**: `excluded_context`围栏ID并入fictional检查集——围栏中出现不允许ID同样说明模型输出了无依据来源标记（围栏不是虚构藏匿处）。
A正常+围栏B（均∈允许集）→校验通过，A正常认证、B绝不因代码块取得来源资格。更保守的整篇拒绝未采用（允许A+围栏B共存，§6.4双向对照保持）。GLM异常安全回退/原始标题与安全派生隔离零改动。

## 6. FIX4-04｜固定真实反例（§七，D组+E2E实证）

两篇真实文章以项目规范化流程生成**真实ID**（非固定示意字符串）: A=正常新闻条目、B=仅存在于摘要Markdown代码围栏内的`- [art_B]`条目。D组断言（全部真实链路）: A/B双过`verify_archive`且都在`load_trusted_articles_since()`可信集合内（真实归档/真实文件SHA-256/逐记录摘要/ID映射——B档案存在**不构成放行理由**）；真实`load_news_summary`消费该摘要→**A正常保留+进可信附录（行首槽位+原始档案双重认证）**；B不成为正式条目/B整行不出现在输出任何位置（未被上游过滤洗白）/B URL不入附录/B不进legal_ids。E2E-A2进一步验证: 最终周报提示词中B行仅以`data_assembler`数据包"研究上下文"围栏内形态存在（每条B行都落在`markdown_fence_map`围栏区——P0-1封版既有设计，合法），来源索引附录段无B行无B URL、A URL在。

## 7. 来源档案可信链继承（§十四.10）

批次排他创建+清单事务/逐档案verify_archive/`load_trusted_articles_since`实时重建/`verify_citation_trusted`——全部零改动继承。围栏规则只决定**哪些ID有资格进入认证流程**（围栏内ID无资格），认证本身仍以原始档案为唯一可信根。

## 8. 不同围栏类型与未关闭围栏测试（§十四.8，A组7项）

A1 §4.5正向（A正常+围栏B+围栏后C→`legal_ids==[A,C]`，围栏不吞其后正常新闻）；A2 四反引号+语言标签；A3 波浪围栏（带语言）；A4 Markdown缩进边界（1空格缩进开栏有效/4空格缩进=缩进代码块**非围栏**，其内行按普通文本处理`fenced_lines==[]`）；A5 关栏匹配三态（3开4关=有效关栏/关栏更短=围栏继续/```` ``` ````关`~~~`开=不关）；A6 未关闭围栏持续到文档结束（围栏后B被排除、围栏前A保留）；A7 共享`markdown_fence_map`行级True/False与文档级独立（两文档拼接后各自状态不变）。全部走真实`parse_news_item_references`。

## 9. 周报过滤专项（§八C组5项）

C1 合法板块内围栏含合法格式ID: B整行/URL/围栏标记均不出现在输出（未洗白）+A正常认证；C2 围栏内伪造板块标题: 不经`sanitize_news`洗白成板块内容、无来源索引；C3 板块标题前围栏: 围栏内B剔除+其后真实板块内A保留；C4 跨日独立: Day1未关闭围栏只吞Day1其后内容、Day2正常B条目保留且认证`legal==[A,B]`（未关闭状态不跨文件）；C5 已关闭围栏后的正常新闻不丢失。全部真实新闻目录+真实`load_news_summary`。

## 10. 负向敏感性（§八F组3项——证明测试对退化敏感）

F1 人为去掉解析器围栏上下文（patch `markdown_fence_map`恒False）→围栏内B直接进入legal_ids且经真实周报错误认证B URL（新测试在退化代码上必败）；F2 恢复旧顺序`sanitize_news(原文)→解析`（patch `strip_code_fences`=恒等）→围栏标记被过滤丢弃、围栏内B被洗白并认证（必败）；F3 围栏ID泄入legal_ids（解析器级leak wrapper）→解析器级legal含B+双patch下真实周报把B当合法引用认证其行内URL（必败）。**不能只测复制出来的正则函数**——三项均以真实模块/真实周报链路断言。

## 11. 专项测试（§八，tests/test_p02_w3_fix4.py，35检查）

A组围栏解析7 ｜ B组模型校验4（B1仅围栏B失败/B2 A+围栏B通过/B3围栏虚构ID拒/B4真实generate两调用→受控重试→确定性回退）｜ C组周报过滤5 ｜ D组真实来源可信链2（D1双档案归档+verify+可信集合前提/D2 §7反例全断言）｜ E组历史安全回归8（E1 A行首+B正文夹带FIX3反例保持/E2两条独立合法/E3虚构ID拒/E4档案缺失不认证不虚构URL/E5档案SHA-256损坏不认证+完整性告警/E6 GLM异常一次调用即回退/E7 Finnhub全败降级不建批次/E8同秒批次不可覆盖两独立批次）｜ F组负向敏感性3 ｜ E2E 6（见§12）。全部走真实模块，零正则复制品自证。

## 12. 正式联合E2E（§九12项要点，复用FIX1~FIX3合成研究夹具）

E2E-A（成功链）: 合法采集→原始档案保存→完整性认证→GLM成功恰1次（合法A引用摘要）→摘要保存→**代码块嵌真实B ID**→周报过滤与严格位置解析（strip先行的真实顺序）→B不成为正式引用（提示词B行仅数据包围栏内形态+附录无B行无B URL+A URL在）→A正常进周报输入→Gate A PASS+Gate B PASS+published+digest==正式文件摘要→无_UNVALIDATED残留→thesis/views零污染。E2E-B（降级链）: 新闻源全部失败→exit0+GLM恰1次+published+Gate A/B PASS+无[art_]认证。外部Finnhub/RSS/GLM全Mock。

## 13. 不得重新开发清单核对（§三）

原始新闻档案Schema/批次排他创建与清单事务/可信原始来源认证/Finnhub状态机/RSS UTC/多行标题单行化/GLM安全回退/正文夹带ID合法位置检查（FIX3行首槽位语义原样保持）/金融时效策略/Gate A/B——全部保留。W3 38/38、FIX1 44/44、FIX2 26/26、FIX3 26/26零改动零回归；本轮**无任何既有测试预期变更**（不适用"说明差异"条款）。

## 14. 全量历史回归（本地45套件 + CI 44套件）

本地**45套件全部exit=0**（44离线套件+test_glm_live按契约跳过且exit=0）: W3 38/38、FIX1 44/44、FIX2 26/26、FIX3 26/26、**FIX4 35/35**、W2/FIX1~6、W1/W1-FIX1、P0-1 FIX1~11、原始14项E2E/四周/冻结14、Gate链、fact_engine、snapshot、P0/P1/P2/P4/P7、phase3/4、round3~6、datafix。CI（workflow排除test_glm_live）44套件全部exit=0。旧摘要兼容: FIX4-02只剔除围栏区域，无围栏旧摘要走原路径（E组+C组既有夹具实证）。

## 15. GitHub Actions CI（workflow_dispatch, offline-tests.yml, ref=dev/p0-2-w3）

| 轮 | Run ID | Job ID | head_sha | 结论 |
|---|---|---|---|---|
| run#1（实现Commit c5ce8d4） | 41167748498 | 124438889310 | c5ce8d4e45eb5d6a2138fe5817bdc6e326959378 | success, 44套件全部exit=0（含test_p02_w3 38/38、fix1 44/44、fix2 26/26、fix3 26/26、**fix4 35/35**;test_glm_live按workflow契约排除;逐套件清单见Git外附件） |
| run#2（最终固定Commit） | 防预写: 编号/Job ID/head_sha/逐套件退出码在最终Commit推送后运行，实证结果见Git外隔离证据附件与对话交付报告，不写入仓库 | — | 最终固定SHA（=run#2 head_sha） | 见Git外证据 |

FIX3的43套绿CI（41094628715）不作为本轮执行证据（其不含fix4专项，且FIX3验收失败原因是DEF-001未关闭而非CI缺陷）；run#2在最终固定SHA上实际运行。

## 16. 工程边界遵守（§十）

只改动: scripts/news_provenance.py（围栏识别+解析器围栏上下文+共用辅助）、scripts/news_collector.py（validate_summary_citations最小调整）、scripts/report_generator.py（load_news_summary过滤顺序）、tests/test_p02_w3_fix4.py（新增）、docs/P0_2_W3_FIX4_DELIVERY.md（本文档）。未触碰: 档案Schema、归档批次及清单事务、Finnhub状态机、RSS UTC、已通过安全标题清洗（sanitize_model_text/_fallback_headlines）、GLM回退、金融指标时效政策、Gate A/B、P0-1/W1/W2封版、既有FIX3测试（test_p02_w3_fix3.py零改动）、W4/W5/P0-3、Mac LIVE、launchd、生产data/news、正式报告与长期状态、生产密钥、真实付费GLM、main分支、force push。

## 17. 最终DEV/LIVE隔离证据（Git仓库外审计材料）

`/Users/cast/audit/IA-P0-2-W3-FIX4-POSTCOMMIT-ISOLATION-<最终SHA前7位>.txt` — 最终Commit与CI run#2之后按§十三10步执行；含核验时间/DEV Git根/HEAD/分支与工作区/远程main与dev真实SHA/DEV-LIVE realpath+inode/关键文件symlink与同inode交叉/launchd程序与工作目录/LIVE核心源码与P0-1封版50b5d13逐文件SHA-256对照/W3系全部新模块及开发测试（含fix4产物）在LIVE缺席/生产报告与长期状态只读元数据/核验限制如实标注。证据正文在对话中完整输出（脱敏，无生产密钥/真实研究正文），实际材料由用户直接交Agent 4；此后不再产生新的docs-only Commit。

## 18. 未验证事项

- 真实GLM输出中自发使用代码围栏包裹引用示例的实际频率（本轮全Mock；不要求真实付费调用）。
- 真实多源RSS/多语言标题下更复杂围栏形态（嵌套列表内围栏/引用块内围栏等超出CommonMark最小子集的形态）的覆盖面——测试锚定§4.5边界+六类围栏形态。
- FIX4交付后的Agent 4独立工程验收结论（本报告不自宣PASS）。

## 19. 结论声明

**READY FOR W3 INDEPENDENT ACCEPTANCE**——W3是否通过、P0-2是否完成由Agent 4独立工程验收决定；不自行宣布W3 PASS、不合并main、不部署Mac LIVE。

---
*回填说明: 实现Commit（代码+测试）先行推送并完成CI run#1实证后，本文档回填run#1实数形成最终固定Commit；run#2对本Commit运行，其编号按防预写纪律只入Git外审计附件与对话交付报告。此后零新提交，固定SHA不变。*
