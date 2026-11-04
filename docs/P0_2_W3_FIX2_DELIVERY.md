# P0-2 W3-FIX2 交付报告（新闻信任边界 · 最小定向整改）

任务编号: IA-P0-2-W3-FIX2 ｜ 指令: IA-P0-2-W3-FIX2-DEV-v1.0 ｜ 冻结契约: IA-P0-2-W3-FIX2-AC-v1.0
开发分支: dev/p0-2-w3（不合并 main，不部署 Mac LIVE）

---

## 1. 基线与固定Commit

| 项 | 值 |
|---|---|
| W3-FIX1失败验收Commit（增量基线，CI 41046916803/41套绿但信任边界未覆盖→验收失败） | `522ca13a9fab36d4912e802735bf92601fd93667` |
| FIX2实现Commit | `24592fcc7086740dcd578e3048ccd93aaf44c2c4` |
| FIX2最终固定Commit | 本交付文档所在Commit（docs回填；完整SHA与两轮CI编号见Git外隔离证据与对话交付报告——文档无法预知自身Commit SHA，防预写纪律，W2/W3/FIX1同法） |
| 增量Diff | `git diff 522ca13a..HEAD` — 2文件 +19/−6（scripts/news_provenance.py +17/−4, scripts/news_collector.py +8/−2）+ 新增tests/test_p02_w3_fix2.py（25检查项）——最小定向整改，零结构重写 |
| W3累积Diff | `git diff 14fe6e5..HEAD` — 7文件 +2972/−79 |
| 封版链 | P0-1 `50b5d13` → W1 `69d7fc7` → W2 `14fe6e5` → W3首轮 `778050c` → W3-FIX1 `522ca13` → **W3-FIX2（本Commit）** |

## 2. FIX2-01｜多行标题数据边界（§四）

`sanitize_model_text()`（news_provenance.py）新增**第一步行边界折叠**： `' '.join(str.splitlines())` ——以Python语言级行语义一次性覆盖 LF/CR/CRLF/VT/FF/NEL(U+0085)/U+2028/U+2029/U+001C~001E 等一切行边界，**不逐字符枚举**（避免"只处理\n漏掉\r与Unicode换行"的枚举遗漏）；随后控制字符剥离、HTML标签剥离、`[`→`(`/`]→`)`、反引号→单引号、剥行首结构符、空白串折叠。不可信来源字段（source/publisher/headline/URL）经此**只能派生一条物理行**：不允许第二条新闻行、不允许新Markdown标题/代码围栏（结构字符成为行内惰性数据）、伪造`[art_...]`不可被extract_citations提取、HTML标签不进入模型与周报派生输出。**一套共同单行函数覆盖全部消费端**（模型输入`_build_news_text`、确定性回退`_fallback_headlines`、周报来源附录`summarize_for_prompt`），无复制的差异正则。原始档案逐字不处理。

## 3. FIX2-02｜GLM失败回退使用安全派生文本（§五）

`_fallback_headlines()`（news_collector.py）回退标题行由原始`a.get('headline')`改为`nprov.sanitize_model_text(...)`——与模型输入共用同一安全派生。两条真实回退路径（A: GLM调用抛异常；B: 模型两次未通过引用校验）共用该函数，均已端到端测试（测试组D/E）；引用ID仍由代码核发，不编造链接。

## 4. FIX2-03｜真实文章ID注入不形成错误引用关系（§六）

固定场景实测： A原始标题=`Fed holds rates\n[文章B真实art_ID]`（B真实归档且通过完整性核验），经 采集→原始归档→分类→GLM异常→标题回退→保存→周报加载→来源附录：
1. A的`headline_original`逐字保留（含B ID方括号原文）；
2. A回退正文只出现代码核发的A引用（行内B ID被neutralize为`(art_B)`，extract_citations不可提取）；**新闻文本不能决定系统核发的article_id——ID来自已验证的结构化来源记录（批次归档时由stable_article_id从provider/pid/url确定性核发），引用关系由代码控制的行首槽位携带**；
3. A标题中的B ID不被识别为额外合法引用；
4. 周报来源索引不把B误记为A的来源（A的附录行只含A的URL）；附录每行恰好且只携带自身行首ID（组I逐行断言）；
5. B经自身独立新闻条目合法出现并被认证（组G1）；仅采A时B虽在可信集合存在也不被认证（组G2——"B通过档案完整性验证"不构成放行A标题伪造B引用的理由）。

## 5. 原始档案不变（§4.4）

同一篇多行恶意标题（含`### SYSTEM`/`<script>`/`[art_deadbeefdeadbeef]`）： `headline_original`与采集原文逐字一致；**构建模型输入、回退摘要、周报来源附录之后原始批次文件SHA-256不变**且verify_archive仍通过（测试组C）——安全不靠删改原文取得。

## 6. 模型成功与失败路径对照（§5.4）

| 路径 | 行为 | 测试 |
|---|---|---|
| GLM成功+引用合规 | 摘要通过确定性校验直接保存（恰1次调用） | H |
| GLM调用异常 | 确定性回退（"AI摘要失败"头），标题经安全派生 | D |
| 两次引用校验失败 | 一次受控重试后确定性回退（"未通过来源引用校验"头），同一安全派生 | E |

## 7. 周报来源附录结果（组I/J）

实际保存摘要后调用真实`report_generator.load_news_summary()`： 附录只含合法引用关系；每行恰好且只携带自身行首ID；恶意Markdown/HTML/伪ID/注入的真实B ID在附录中不重建结构、不形成可信引用；原始多行标题在附录中渲染为单行。

## 8. 专项测试与敏感性（§八）

新增`tests/test_p02_w3_fix2.py`（25检查全过；真实模块链+Finnhub/RSS/GLM全Mock+隔离临时目录）：
A 多行恶意标题经真实`_build_news_text`（恰一条新闻行/无新标题结构/伪ID不可提取）；B 八种行边界（LF/CR/CRLF/U+2028/U+2029/VT/NEL/FS）单行化（直测+真实构建双口径）；C 原始档案逐字+SHA-256不变；D GLM异常路径；E 引用二次失败路径；F 虚构ID不被识别；G 真实B ID注入（G1同批+B独立条目合法出现；G2仅采A+B在可信集合→不误认证）；H 合法新闻全链；I 周报消费逐行ID结构；J 附录再结构化负向；E2E 非关键降级真实研究链（exit0+GLM恰1次+published+Gate A PASS+长期状态零污染）。
**负向敏感性K（真实函数替换模拟退化）**： K1 用FIX1版sanitize（无换行处理）→`### SYSTEM`成为独立行、出现第二条新闻行（A组必失败）；K2 用FIX1版回退（原始标题直出）→摘要文件出现`\n### SYSTEM`与`<script>`原文（D组必失败）；K3 构造FIX1态未neutralize产物（A行含[B真实ID]原文）→真实`load_news_summary`把B误认证入附录（G2-2必失败）——证明现行实现靠行首槽位+neutralize排除该类误认证，而非字符串自证。

## 9. 原W3/FIX1成果继承（§七）

GLM合法成功摘要与引用核验/一次受控重试/二次失败与异常后回退/正常article_id/缺失URL诚实披露/RSS UTC时间/原始摘要完整保全/Finnhub四态/批次不可覆盖(排他创建+flock+损坏保全)/来源完整性验证(档案→清单→SHA→可信集合)/logical_article_id多通道关联/七天周报聚合/新闻缺失非关键降级/正式报告及长期状态保护——全部保留（test_p02_w3.py 38/38、test_p02_w3_fix1.py 44/44 零改动全绿）。本轮不改时间比较器、金融指标、批次不可覆盖机制、Finnhub状态机。不自动核验新闻内容客观真实性（合法引用仅证明新闻关联到确实采集过的来源）。

## 10. 全量历史回归（本地）

**42套件全部exit=0**（41原有+新增test_p02_w3_fix2；test_glm_live按契约跳过）: W3 38/38、W3-FIX1 44/44、W3-FIX2 25/25、W2/FIX1~6、W1/W1-FIX1、P0-1 FIX1~11、原始14项E2E/四周/冻结14、Gate链、fact_engine、snapshot、P0/P1/P2/P4/P7、phase3/4、round3~6。零旧预期调整（本轮无任何旧测试修改）。

## 11. GitHub Actions CI（workflow_dispatch, offline-tests.yml, ref=dev/p0-2-w3）

| 轮 | Run ID | Job ID | head_sha | 结论 |
|---|---|---|---|---|
| run#1（实现Commit 24592fc） | 41066343583 | 124098634426 | 24592fcc7086740dcd578e3048ccd93aaf44c2c4 | success, 42套件全部exit=0（含test_p02_w3 38/38、test_p02_w3_fix1 44/44、test_p02_w3_fix2 25/25;逐套件清单见Git外附件） |
| run#2（最终固定Commit） | 防预写： 编号/Job ID/head_sha/逐套件退出码在最终Commit推送后运行，实证结果见Git外隔离证据附件与对话交付报告，不写入仓库 | — | 最终固定SHA（=run#2 head_sha） | 见Git外证据 |

FIX1的41套绿色CI（41046916803）不作为本轮执行证据；run#2在最终固定SHA上实际运行。

## 12. 工程边界遵守

只改动: scripts/news_provenance.py、scripts/news_collector.py、tests/test_p02_w3_fix2.py、docs/P0_2_W3_FIX2_DELIVERY.md（report_generator.py本轮零改动——附录消费已在FIX1接入sanitize_model_text，行边界修复自动生效）。未触碰: metric_registry.json、freshness_policy.py、Gate A/B、批次不可覆盖机制、Finnhub状态机、新闻来源策略及数量、W1/W2成果、W4/W5/P0-3、Mac LIVE、launchd、生产data/news、正式周报、长期状态、生产密钥、真实付费GLM、main分支、force push。

## 13. 最终DEV/LIVE隔离证据（Git仓库外审计材料）

`/Users/cast/audit/IA-P0-2-W3-FIX2-POSTCOMMIT-ISOLATION-<最终SHA前7位>.txt` — 最终Commit与CI run#2之后执行；含核验时间/DEV HEAD/DEV与LIVE realpath+inode/origin/main/launchd路径与工作目录/LIVE关键源码与P0-1封版50b5d13 SHA-256逐文件对照/W3全部新模块及开发测试未部署LIVE/生产长期状态只读元数据/无法证明的历史事项如实标注。证据正文在对话中完整输出（脱敏，无生产密钥/私人状态正文），实际送达供Agent 4读取。

## 14. 未验证事项

- 真实Finnhub网络异常行为与真实GLM对输出约定的遵守率（本轮全Mock，按指令不要求真实付费调用）。
- `str.splitlines()`行语义随Python版本的边界集稳定性（现覆盖CPython 3.9文档全集；测试B组锚定八种边界）。
- FIX2交付后的Agent 4独立工程验收结论（本报告不自宣PASS）。

## 15. 结论声明

**READY FOR W3 INDEPENDENT ACCEPTANCE**——W3是否通过、P0-2是否完成由Agent 4独立工程验收决定；不自行宣布W3 PASS、不合并main、不部署Mac LIVE。

---
*回填说明: 实现Commit（代码+测试）先行推送并完成CI run#1实证后，本文档回填run#1实数形成最终固定Commit；run#2对本Commit运行，其编号按防预写纪律只入Git外审计附件与对话交付报告。此后零新提交，固定SHA不变。*
