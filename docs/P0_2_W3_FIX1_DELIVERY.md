# P0-2 W3-FIX1 交付报告（新闻原始来源保全 · 首轮验收失败增量整改）

任务编号: IA-P0-2-W3-FIX1 ｜ 指令: IA-P0-2-W3-FIX1-DEV-v1.0 ｜ 验收冻结: IA-P0-2-W3-FIX1-AC-v1.0
开发分支: dev/p0-2-w3（不合并 main，不部署 Mac LIVE）

---

## 1. 基线与固定Commit

| 项 | 值 |
|---|---|
| W3首轮失败验收Commit（FIX1起点，增量基线） | `778050cdc234573128d70b6efa1d0bbac0d20cac` |
| W3首轮失败验收CI | run 41034617752 / job 123992294827（40套件exit=0，但冻结负向场景未覆盖→验收失败） |
| FIX1实现Commit | `8cb6e9abd5161c5978563547c72c06db1130d297` |
| FIX1最终固定Commit | 本交付文档所在Commit（docs回填;完整SHA见Git外隔离证据与对话交付报告——文档无法预知自身Commit SHA，防预写纪律，W2/W3同法） |
| 增量Diff | `git diff 778050cdc234573128d70b6efa1d0bbac0d20cac..origin/dev/p0-2-w3`（HEAD=最终固定Commit） — 4文件改动+1新测试，578 insertions / 202 deletions + tests/test_p02_w3_fix1.py（44检查项） |
| W3累积Diff | `git diff 14fe6e57004b46ede889a190952b373d51eb4f76..origin/dev/p0-2-w3`（HEAD=最终固定Commit） — 5文件，2055 insertions / 79 deletions |
| 封版链 | P0-1 `50b5d13` → W1 `69d7fc7` → W2 `14fe6e5` → W3首轮 `778050c` → **W3-FIX1（本Commit）** |

## 2. 四项确定性缺陷逐条整改

### FIX1-01 / DEF-001 批次不可覆盖（§4）
- 批次身份: `HHMMSSZr{N}x{uuid4().hex[:8]}` — 时间戳+记录数之外追加不静默碰撞的UUID短段；同秒同数量两次保存身份必然不同。
- 排他创建: 档案文件以 `open(path,'x')`（O_CREAT|O_EXCL）写入；极端身份碰撞（UUID退化）→ 换新身份重试≤8次→仍碰撞→`RuntimeError` 明确失败，**不覆盖任何已有档案**。
- 清单并发安全: manifest 读-改-写在 `manifest.lock` 上 `fcntl.flock(LOCK_EX)` 排他锁内完成，tmp+`os.replace` 原子落盘；更新失败→`RuntimeError`，已写档案保留不销毁。
- 损坏清单: 无法解析时**原样保全**为 `news_sources_manifest_{ymd}.corrupt-{uuid8}.json`，新清单登记 `recovery_note`；绝不静默当作空清单覆盖。损坏后旧批次 `verify_archive` 报"清单中无此批次条目"（fail-closed），可信集合只含可验证批次。
- article_id 幂等保留: 同内容重跑产生新批次文件+清单条目，但 article_id 不变、索引不产生虚假重复来源。

### FIX1-02 / DEF-002 引用必须实际验证原始档案（§5）
- 可信根链路: 原始档案 → 清单核验 → 文件SHA-256 + 逐记录 `record_sha256` 重算 → article_id 映射 → 可信来源集合 → 周报引用。新增 `load_trusted_articles_since()`（逐档案实核验构造可信集合）与 `verify_citation_trusted()`（唯一可信认证入口）。
- `build_refs_index()` 验证门控: 坏批次记录**不得先入 articles 再只留告警**——未通过完整性验证的批次不进入索引 articles，计入 `failed_batches`。
- 消费端 `report_generator.load_news_summary()` 不再读取历史 `news_refs_*.json` JSON 作为可信依据；每次消费用 `load_trusted_articles_since` 从原始档案实时重建可信集合。即使伪造的 news_refs 声称 `integrity.failed_batches=[]`，无档案支撑的引用仍标注"⚠️未通过来源认证（原始来源档案缺失或未通过完整性验证）"，伪造 URL 不得进入输出。
- 索引存在但档案被删除/篡改（URL改动即破坏 record_sha256）→ 引用不获认证、完整性告警如实披露、部分损坏不阻断其他有效来源。
- 旧入口 `verify_citation()` 降级为**索引成员诊断**（docstring 明示不得作为原始档案认证）；既有 W3 测试依赖手工索引认证的（K组/L组/O2）改为"真实档案正向 + 无档案/伪造索引负向"，业务语义增强而非删除，变更理由已注释在 tests/test_p02_w3.py 内（FIX1-02 标注）。

### FIX1-03 / DEF-003 GLM成功摘要引用必须可追溯（§6）
- 确定性校验 `validate_summary_citations(summary, allowed_ids)`：①至少1个引用 ②引用全部∈本次允许输入集合（虚构ID逐个列出）③每条 `-` 开头且>8字符的摘要条目必须携带允许引用。
- 流程: 成功输出→校验→失败→**一次受控重试**（retry prompt 附【重要修正】+具体校验失败原因+输出约定）→二次失败→**弃用模型摘要**，`_fallback_headlines` 确定性标题回退（代码核发真实 article_id，不编造 URL）；GLM 异常→同类回退（头部"AI摘要失败"）。模型原文（无引用/虚构引用版本）不写入摘要文件。
- 允许集合 `_allowed_citation_ids` 来自各类目文章的 article_id；提示词第1/5条明确"每条'-'摘要条目必须以对应[art_xxx]开头，只能使用输入编号不得虚构"。system 角色固定，不因新闻内容改变。
- 保留: 原始档案先于GLM归档、模型输入脱敏、GLM流式、GLM失败回退、新闻分类、7天聚合、输入长度控制、原始URL、周报八节结构。未新增AI模型、未使用真实付费GLM。

### FIX1-04 / DEF-004 Finnhub采集状态必须真实（§7）
- 状态与文章集合分离: `fetch_market_news` → `(recent, status, err)`；`fetch_company_news` → `(all_news, symbol_status)`，逐 symbol 记 `{status, items, error}`。
- 四态: `OK_WITH_ITEMS` / `OK_EMPTY` / `ERROR` / `PARTIAL_ERROR`，状态来自实际请求执行结果，不再由"非None/非空数组"真值推断。市场通道三态（有效文章/成功空/异常）各自得到正确诊断；个股通道全部成功/部分失败/全部失败/成功零条/单只失败可追踪。
- `collect_all_news` 聚合: 有败有成→PARTIAL_ERROR（成功文章继续归档+失败来源明确状态+不虚构）；全败→ERROR（不创建虚假批次、不标ok、周报既定非关键降级）；全成零条→OK_EMPTY 合法空结果（明确标注"本周无新闻条目…合法空结果而非请求失败"，不制造虚假新闻、不冒充含文章档案）。
- `source_status` 含 `Finnhub/general:error` 与 `Finnhub/company_news:{SYM}` 逐键状态;RSS 逐 Feed `ok`/`fail` 词汇保留，时间/来源/字段保全不受统一诊断影响。

## 3. 跨通道同文章关联（FIX1-05 §8）
`logical_article_id(raw)` = `lart_` + SHA-256(`provider|pid:{provider_article_id}` 或 `provider|url:{url}`)[:16] — **标题不参与**。同一 Finnhub 文章（pid 9001）从 market_news 与 company_news（watch_symbol=NVDA）两通道采集: article_id 不同（通道身份保留）、logical_article_id 相同（确定性知道是同一供应商文章）；不同 pid 不同 logical（不误并）；两次采集事实、通道差异、请求证券代码、related 原文均保留在档案。article_id 规则不变→旧引用不失效，新字段纯增量（normalize_record 新增字段+_article_view 暴露），无需兼容迁移。

## 4. 伪指令与HTML标题（FIX1-06 §9）
`sanitize_model_text()`: 控制字符剥离、HTML标签剥离（`<[^>]{0,200}>`）、`[`→`(`/`]→`)`（阻断伪造 `[art_]` 注入）、反引号→单引号、剥行首结构符。应用于两条边界: ①模型输入行（news_collector `_build_news_text` 的来源/标题）②周报确定性来源附录（`summarize_for_prompt` 的 publisher/headline/URL）。安全断言口径 = `extract_citations(s)==[]`（方括号neutral化后子串仍在但不可被提取为引用）。原始标题在来源档案**逐字保存**（本机审计原始档案 ≠ 发给模型的安全派生内容）；system role 固定；新闻来源ID字符串不能替代代码核发ID；Markdown/HTML 不破坏报告结构。不要求新内容安全产品。

## 5. 原W3能力继承（不变项）
Finnhub/RSS原始字段保全、URL保全、长摘要保全、RSS UTC发布时间、原始/脱敏分离、稳定文章ID、GLM失败回退、清单SHA-256、7天聚合去重、周报八节结构、P0-1/W1/W2全部已关闭成果——均未回退。W3原38项测试语义保留（36项断言原语义+K3/L4新增负向，K组/L组/O2由"手工索引认证正向"改为"真实档案正向+无档案负向"并注明理由）。

## 6. 真实联合模块测试（FIX1-07 §十）
新增 `tests/test_p02_w3_fix1.py`（44检查项，真实模块 news_collector/news_provenance/report_generator.load_news_summary/正式研究链；Finnhub/RSS/GLM 全Mock，隔离临时目录）:
A 同秒双批次/同内容重跑/4线程并发/清单损坏保全/恒定身份敏感性（真实写入读取+SHA-256前后比较）；B 无档案假索引；C 档案篡改+删除；D GLM省略ID（恰2次调用+受控重试+确定性回退+模型原文不入文件）；E 虚构ID；F 跨通道同pid；G Finnhub异常（三态可区分）；H 全败/部分败逐symbol；I 成功空列表；J 恶意标题全链（档案逐字/输入neutral化/system固定/附录sanitized/extract_citations不可提取伪造ID）；K 合法来源采集→保存→验证→摘要→引用→周报全链（1次调用通过校验+URL/UTC入附录）；L 非关键降级（真实13-patch研究链: exit0+GLM恰1次+四对象落盘+published+Gate A PASS+长期状态零污染）。
**负向敏感性S1~S4**: 批次身份退化为常数→RuntimeError且原档案SHA不变；索引成员判断对伪造索引返回True（证明不可作认证）而可信路径返回False；无引用校验必失败；异常=ERROR与成功空=OK_EMPTY可区分——四项原始错误（无条件覆盖/索引成员即有效/GLM无引用放行/Finnhub异常记ok）任一再现，对应检查必失败。

## 7. 全量回归（本地）
41套件全部 exit=0（40原有 + 新增 test_p02_w3_fix1；test_glm_live 按约定跳过）: test_p02_w3 38/38、test_p02_w3_fix1 44/44、P0-1 FIX1~11、W1/W1-FIX1、W2/W2-FIX1~6、E2E原始14项/四周/冻结14、Gate链、fact_engine、snapshot、P0/P1/P2/P4/P7修复、phase3/4、round3~6。

## 8. GitHub Actions CI
| 轮 | Run ID | Job ID | head SHA | 结论 | 逐套件退出码 |
|---|---|---|---|---|---|
| run#1（实现Commit 8cb6e9a） | 41046409804 | 124031473076 | 8cb6e9abd5161c5978563547c72c06db1130d297 | success | 41套件全部exit=0（含test_p02_w3 38/38、test_p02_w3_fix1 44/44;逐套件清单见Git外附件） |
| run#2（最终固定Commit） | （防预写: 编号/Job ID/head_sha/逐套件退出码在最终Commit推送后运行，实证结果见Git外隔离证据附件与对话交付报告，不写入仓库） | — | 最终固定SHA（=run#2 head_sha，见Git外证据） | 见Git外证据 | 见Git外证据 |

工作流: offline-tests.yml（workflow_dispatch, ref=dev/p0-2-w3）。run#2 head_sha 必须等于最终固定Commit。本轮CI不得沿用W3首轮40套件绿作为验收依据。

## 9. 工程边界遵守
只改动: scripts/news_provenance.py、scripts/news_collector.py、scripts/report_generator.py（仅新闻部分）、tests/test_p02_w3.py、tests/test_p02_w3_fix1.py、docs/P0_2_W3_FIX1_DELIVERY.md。未触碰: 金融指标注册表、金融时效策略、fact_engine、Gate A/B正式门禁、P0-1来源身份、W1-W2成果、run_weekly新闻非关键定位、Mac LIVE、launchd、生产data/news、历史正式报告、thesis/allocation_views、生产密钥（未读取未复制）、真实付费GLM、W4/W5/P0-3、main分支、force push。

## 10. 最终DEV/LIVE隔离证据（Git仓库外审计材料）
`/Users/cast/audit/IA-P0-2-W3-FIX1-POSTCOMMIT-ISOLATION-<最终SHA前7位>.txt`（Git仓库外;最终Commit与CI run#2之后执行;完整文件名/SHA-256见对话交付报告） — 在最终Commit与CI run#2之后执行;含: 核验时间、DEV HEAD=最终SHA、DEV/LIVE realpath+inode 对照、origin/main 与 origin/dev/p0-2-w3、launchd 路径与内容、LIVE关键源码与P0-1封版`50b5d13` SHA-256逐文件对照、LIVE不存在W3/W3-FIX1新模块及开发测试、生产 data/news 无 news_sources_*/news_refs_* 新产物、生产长期状态只读检查、不可再现的历史瞬时事项如实标注"无法事后证明"。证据正文已在对话中完整输出（脱敏，无生产密钥/私人状态正文）。

## 11. 剩余未验证事项
- 真实Finnhub API在异常限流/断连下的行为（本轮全Mock；测试覆盖异常类路径但非真实网络）。
- 真实GLM对引用输出约定的实际遵守率（Mock验证确定性校验与回退;未使用真实付费GLM，按指令不要求）。
- `fcntl.flock` 在非本地文件系统（NFS等）上的语义（本机APFS验证）。
- W3-FIX1交付后的Agent 4独立工程验收结论（本报告不自宣PASS）。

## 12. 结论声明
本报告完成后仅声明: **READY FOR W3 INDEPENDENT ACCEPTANCE**。W3是否通过、P0-2是否完成，由Agent 4独立工程验收决定;开发方不自行宣布W3 PASS、不合并main、不部署Mac LIVE。

---
*回填说明: 实现Commit 8cb6e9a（代码+测试）先行推送并完成CI run#1实证（41套件exit=0）后，本文档回填run#1实数形成最终固定Commit;run#2对本Commit运行，其编号按防预写纪律只入Git外审计附件与对话交付报告。此后零新提交，固定SHA不变。*
