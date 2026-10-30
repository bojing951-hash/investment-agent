# P0-2 W3 交付文档 — 新闻原始来源保全(原始档案/稳定引用ID/来源索引)

指令: IA-P0-2-W3-DEV-v1.0 · 任务 IA-P0-2-W3
分支: dev/p0-2-w3(自W2封印Commit建立;远程 git@github.com:bojing951-hash/investment-agent.git)
状态: **READY FOR W3 INDEPENDENT ACCEPTANCE**(本地40套件全绿;CI实证与最终
只读隔离证据按§14顺序以Git外验收附件交付;最终验收权属Agent 4)

## 基线固定(不可变)

| 项 | 值 |
|---|---|
| P0-1封印(GitHub main) | 50b5d13db6c477084c6f4b3944b7bd08a8e329d6 |
| W1封印 | 69d7fc71f4ac05d3e5323cb5e270585ec48d6f97 |
| **W2封印(本轮基线)** | **14fe6e57004b46ede889a190952b373d51eb4f76** |
| W2最终CI(39套件) | run 41005889614 / job 123900591911 |
| 冻结契约 | IA-P0-2-AC … IA-P0-2-W3-DEV v1.0(继承,未改动) |

## 1. W3目标与预识别问题对应

指令预识别5问题 → 实现逐一对应(源码定位见各节):

| # | 指令预识别问题 | 实现处置 | 验证 |
|---|---|---|---|
| 1 | URL在save_news合并时丢失 | 采集层保留url_original→规范化记录独立字段→news_raw派生视图同步带url | B组 |
| 2 | summary [:200]截断发生在归档前 | 归档保全summary_original全文;截断只存在于derive_display派生副本 | C组 |
| 3 | RSS time.mktime本地时区污染published_parsed | 改用calendar.timegm(UTC语义);mktime禁用并留D2时区漂移敏感性对照 | D组 |
| 4 | 脱敏污染原始 | 脱敏仅作用于送GLM的派生副本;档案headline/summary保留原文 | I组 |
| 5 | 周报无法从摘要找回原始URL/来源 | [art_xxx]稳定引用ID贯穿输入→摘要→周报;来源索引确定性构造 | K/L组 |

## 2. 本轮新提交与差异范围

| 提交 | SHA | 内容 |
|---|---|---|
| W3实现提交 | c80c016d520feec841359b017c867f50038fe95b | 新增 scripts/news_provenance.py(491行) + tests/test_p02_w3.py(728行) + docs/P0_2_W3_DELIVERY.md;修改 scripts/news_collector.py(+193/−49)、scripts/report_generator.py(+24/−0,仅新闻输入) |
| W3最终提交 | 即本提交(docs-only回填run#1) | run#2于本提交推送后触发,head_sha=本提交;run#/job#以Git外验收附件为准(防预写) |

- 增量差异 `14fe6e5 → W3`: `news_collector.py | 193+/49−`、`report_generator.py | 24+/0−` + 新增 `news_provenance.py`、`test_p02_w3.py`。
- **零改动**: metric_registry.json、freshness_policy.py、fact_engine.py、
  research_provenance.py(金融事实门禁)、snapshot_builder.py(身份规则)、
  run_weekly.py、其余全部脚本与配置;周报八节结构未动;Gate A/B放行未动。
- 禁止项遵守: 未触碰LIVE、launchd、生产data/news、生产报告、生产密钥;
  未push main;未force push;无真实付费GLM(全部Mock/合成数据);未部署。

## 3. 来源档案Schema与字段保全(W3-01/W3-02)

### 3.1 规范化来源记录(18字段,显式区分不得互相代替)

`normalize_record()` 产出,关键字段语义:

```
schema_version=1 | article_id | provider('Finnhub'/'RSS') | channel
('market_news'/'company_news'/'rss') | publisher(原发布方;RSS缺发布方时
以feed_name记载,显式可追溯,不冒充Finnhub式source) | feed_name/feed_url/
entry_id(RSS Feed身份+entry.id/guid) | watch_symbol(个股新闻请求代码) |
provider_article_id | headline_original | summary_original(全文) |
url_original | published_raw(来源原始时间值原样保留) | published_at_utc |
published_status('UTC'/'UNKNOWN') | retrieved_at_utc(采集时刻,独立保存,
不与发布时间互替) | provenance_status('COMPLETE'/'PARTIAL:url,headline,…')
| record_sha256 [+ related_original如供应商提供]
```

- 采集保全: 市场新闻保留id/source/summary/url/datetime;个股新闻另带
  watch_symbol与related原文;RSS保留Feed身份、entry_id、published原文
  字符串与structured time。RSS仅摘要不宣称全文(summary_original即所采集
  的最大真实内容,永不截断、永不标注"全文")。
- 缺失处理: 缺URL/标题/发布方/发布时间 → provenance_status逐项披露,
  不以其他字段顶替;缺发布时间绝不以采集时间冒充。

### 3.2 稳定article_id(W3-03)

`art_ + SHA-256(身份键)[:16]`;身份键优先级:
`供应商文章ID > URL > (发布方+标题+原始发布时间)`(均含provider|channel前缀)。
同一文章重跑得同一ID(幂等,G组3批次→2唯一身份);同标题不同URL是两条独立
来源(F组);URL参与身份但仅作规范化比较用,原值不覆盖。

### 3.3 批次归档与双重完整性(反自我认证)

- `news_sources_{ymd}_{HHMMSS}Zr{N}.json`——同日重跑新批次,旧批次永不
  覆盖/删除(G组);先归档后分类后GLM(采集→原始保存→分类→GLM→输出),
  GLM失败原始档案仍在(J组)。
- 独立日清单 `news_sources_manifest_{ymd}.json`(追加式)记录每个档案文件
  整体SHA-256——**摘要不可自我认证**: 档案文件自改由清单SHA检出;
  记录内容篡改由逐记录record_sha256重算检出;两层独立(N组双重检出)。
- `record_sha256 = SHA-256(json(记录剔除record_sha256/batch_id/
  retrieved_at_utc, sort_keys, ensure_ascii=False, separators=(',',':')))`
  ——序列化规则文档化于`RECORD_DIGEST_EXCLUDE`,跨平台确定性。
- verify_archive只报告事实不修改文件;损坏档案不被标记为通过验证。

### 3.4 时间语义(W3-02 §6.3)

- Finnhub datetime=Unix纪元秒(UTC语义)→`datetime.fromtimestamp(epoch,
  tz=timezone.utc)`,与进程本地时区无关。
- RSS published_parsed(UTC结构化时间)→`calendar.timegm`按UTC解释。
  **time.mktime禁用**: 它按进程本地时区解释同一struct_time,D组实测
  UTC/Asia/Shanghai/America/New_York三时区产出3个不同秒值(漂移实证),
  D2保留该敏感性对照防回归。
- 缺发布时间→published_at_utc=None+published_status='UNKNOWN'(E组),
  不造假时间。

### 3.5 脱敏与原始的隔离(W3-04)

- `original ≠ sanitized_model_input`: 脱敏(sanitize_for_api+额外替换)仅
  作用于送GLM的news_text派生副本;原始档案headline_original/
  summary_original保留原文(I组: 档案留原文,prompt为代称)。
- 模型输入行格式 `- [art_x] [source] headline`;prompt规则第5条重写:
  引用编号无需复现;脱敏词无法确知时沿用代称分析,**不必猜测真实国家/
  人物**,保留不确定性(不要求模型猜测Country-A真实所指)。
- 模型输入中引用ID均为实际存在的article_id(由代码注入真实ID,虚构ID
  无法通过来源认证,K组);新闻内容含指令/HTML/Markdown控制字符按数据
  处理不执行(送摘要前仍经sanitize_for_api,且档案原文只作数据存储)。

## 4. 周报消费与来源索引(W3-05)

- `news_refs_{ymd}.json`: `{kind:'news_refs_index', integrity:{checked_
  batches,failed_batches}, articles:{aid→{article_id,provider,channel,
  publisher,headline_original,url_original,url_available,url_note,
  published_at_utc,published_status,retrieved_at_utc,provenance_status,
  batch_id}}}`;同日多批次按article_id去重(首见为准);逐批次完整性验证,
  失败批次计入integrity不标已验证。
- `load_news_summary`(W3-05唯一改动函数,report_generator.py)兼容保留:
  7天聚合/去重/9000字符截断逻辑零改动;截断**之后**追加确定性来源索引
  段`#### 来源索引(确定性代码构造,非模型生成;引用经来源档案核验)`:
  对截断文本中每个[art_x]给出发布方/渠道/原标题/URL或"无直接文章链接
  (不可提供)"/发布时间(UNKNOWN如实标注)/完整性状态;虚构ID→
  `⚠️未通过来源认证(来源索引中不存在,不得作为已引用来源)`;
  失败批次→完整性告警头。无引用→无附录(旧摘要完全向后兼容)。
- 不漏周(7天窗口聚合全部refs索引)/不旧当新/不丢引用ID/不存在来源
  不标已引用/模型摘要不冒充原始证据(索引段明示非模型生成)。
- 周报八节结构未动;news_raw_{ymd}.json仍写(派生兼容视图,现含
  article_id/url/全文summary)。

## 5. 降级与失败语义(W3-06,不改Gate A/B放行)

| 场景 | 行为 |
|---|---|
| 部分源失败 | 其余真实来源照常归档;source_status逐通道(含RSS逐Feed)披露成败 |
| 全部失败 | 不创建批次不建索引;摘要为固定降级披露文本(明示非模型生成、不含虚构条目);不阻断金融研究 |
| GLM失败 | 原始档案已先行保存;回退标题列表带[art_]引用ID可追溯,不用错误链接 |
| 档案损坏 | verify_archive双重检出(SHA+记录摘要);索引integrity告警;不标通过完整性验证 |
| 缺URL | url_available=false+url_note"来源未提供直接文章链接(不可提供,不编造)" |
| 缺发布时间 | published_status='UNKNOWN',不造假 |
| 仅旧摘要(无refs) | load_news_summary无[art_]引用→无附录,完全向后兼容 |

## 6. 专项测试(tests/test_p02_w3.py,36检查全过)

组A原始字段读回一致(18字段逐项)|B URL丢失敏感性(归档PARTIAL披露+真实
流程回归)|C截断隔离(原始1044字符全文保全+派生200)|D RSS时区(tzset三时区
UTC一致+mktime漂移敏感性对照)|E缺发布时间UNKNOWN不造假|F同标题不同URL两条
身份|G同日重跑3批次不覆盖2唯一身份幂等|H分类保留article_id(Fed入美联储
利率类)|I脱敏隔离(档案原文/prompt代称/真实ID)|J GLM失败原始保全+回退带ID|
K虚构引用认证失败|L七天周报窗口(body/附录切分计数,无URL标不可提供)|M
全败无批次无索引+部分失败逐Feed披露|N篡改双重检出(文件SHA+记录摘要)+索引
完整性告警|O安全继承(O0陈旧数据包预检exit2不调GLM+O0b真实data_assembler
重打包+O1正式研究可运行exit0/GLM恰1次/四对象落盘+O2真实新闻消费链进入
周报输入含确定性来源索引+O3正式发布/身份/长期状态无回归+O4 Gate A语义
未动PASS/事实质量全PASS)。

全部使用真实被测函数;Finnhub/RSS/GLM均为Mock(13处patch),无网络无密钥;
O组周报链的load_news_summary为**真实未Mock**实现。

## 7. 回归(§十三)

本地全量: `tests/test_*.py`除test_glm_live(显式跳过)共**40套件全部exit=0**
(39历史套件+W3专项;含P0-1 FIX1~11、W1/W1-FIX1、W2/FIX1~6、原始14项E2E、
Gate A/B、报告保护、论点观点、预测生命周期、月报季报)。未删除或弱化任何
既有测试。CI(§14)同口径。

## 8. 隔离设计(DEV/LIVE)

- 开发全部在 /Users/cast/investment-agent-dev(独立仓库,分支dev/p0-2-w3);
  LIVE(/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent)零触碰。
- 测试数据全部在tmpdir临时目录;生产data/news未写入(本机开发目录data/为
  gitignored本地副产物,非LIVE路径)。
- W3新模块news_provenance.py仅用Python标准库,不导入网络客户端/密钥,
  离线可测;news_collector/report_generator的W3改动不引入新依赖。
- 最终Commit后按§十四执行只读隔离核查并输出Git外证据附件(时间/realpath/
  inode/Git身份/launchd/LIVE核心源码SHA vs P0-1封印/W3模块在LIVE缺席)。

## 9. CI实证(防预写: run#1于实现提交推送后回填,run#2以附件为准)

- 实现提交CI run#1: **run 41034149331 / job 123990751320 / head_sha
  c80c016d520feec841359b017c867f50038fe95b / conclusion=success**,
  逐套件日志核验40套件全部exit=0(test_p02_w3含在内),零非零,glm_live跳过。
- 最终提交CI run#2: 以Git外验收附件为准(head_sha=最终提交SHA)
- workflow: .github/workflows/offline-tests.yml(workflow_dispatch,
  与W2同口径,逐tests/test_*.py执行,glm_live排除)

## 10. 未验证事项(如实披露)

1. 真实Finnhub/RSS网络采集与真实GLM付费调用未在开发中执行(§十二禁止);
   W3验证全部基于Mock与合成数据;真实通道行为差异留待LIVE部署后观察。
2. 生产LIVE data/news历史数据无news_sources档案(W3只保证W3起的新采集);
   load_news_summary对旧摘要向后兼容(L/K组覆盖)。
3. 同日重跑批次文件名HHMMSS精度: 同秒内两次批次后缀Zr{N}以记录数区分,
   记录数也相同则同文件名覆盖——该场景(同秒+同记录数)实际采集中不可达
   (采集含网络IO),G组以不同时刻重跑验证;如实记录该理论边界。
4. GitHub Actions macOS runner与本地macOS(python3.9)环境差异由CI run#2
   独立覆盖;若runner无TZ数据库D组tzset行为以CI结果为准。
5. fetch_market_news既有7天过滤对datetime=0条目的丢弃为**遗留行为**
   (W3前已存在,非本轮引入);该过滤上游使部分UNKNOWN时间条目不进入档案,
   进入档案者E组保证不造假。留待后续轮次评估是否前移。

## 11. 交付清单对照(§十四)

代码+测试(实现提交)✓|对W2封印完整Diff(§2)✓|Schema与引用规则(§3/§4)✓|
隔离设计(§8)✓|完整性证据(N组+§3.3)✓|专项测试(§6)✓|回归(§7)✓|
CI Actions Run/Job/head_sha(§9+附件)→按序|最终DEV/LIVE隔离证据(附件)→按序|
未验证事项(§10)✓|docs/P0_2_W3_DELIVERY.md(本文档)✓

---

完成后状态: **READY FOR W3 INDEPENDENT ACCEPTANCE**(不自行宣布W3 PASS,
不合并main,不部署LIVE;最终验收权属Agent 4)
