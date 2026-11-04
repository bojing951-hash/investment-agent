# P0-2 W2 FIX6 交付文档 — 诊断模式观测新鲜度如实标注(NOT_ASSESSED)

指令: IA-P0-2-W2-FIX6-DEV-v1.0 · 任务 IA-P0-2-W2-FIX6(W2-FIX5独立验收失败后的最小增量整改)
分支: dev/p0-2-w2(远程 git@github.com:bojing951-hash/investment-agent.git)
状态: **READY FOR W2 INDEPENDENT ACCEPTANCE**(本地39套件+CI run#1全绿;
run#2与最终只读隔离证据按§9/§10以Git外验收附件交付;最终验收权属Agent 4)

## 基线固定(不可变)

| 项 | 值 |
|---|---|
| P0-1封印 | 50b5d13db6c477084c6f4b3944b7bd08a8e329d6 |
| W1封印 | 69d7fc71f4ac05d3e5323cb5e270585ec48d6f97 |
| FIX5实现提交 | db586638c9d58e0ebd58c83b50d8191176f2d3ba |
| **FIX5验收失败提交(本轮基线)** | **2c36cf9bf7355d0320f14764b1bd568ff4755647** |
| FIX5 CI(38套件通过) | run 40988759640 |
| 冻结契约 | IA-P0-2-AC … IA-P0-2-W2-FIX6-AC v1.0(继承,未改动) |

## 1. 验收失败基线固定

本轮整改基线为 FIX5 最终提交 `2c36cf9`(dev/p0-2-w2,HEAD与远程一致,工作树干净)。
未重新开发W2,未删除FIX1~FIX5任何成果;FIX6为纯最小增量。

## 2. 本轮新提交

| 提交 | SHA | 内容 |
|---|---|---|
| FIX6实现提交 | e091d288cd3cff910e4894fabe2d426db7aa1475 | scripts/allocation_engine.py(+15/−6) + tests/test_p02_w2_fix6.py(新增468行) + docs/P0_2_W2_FIX6_DELIVERY.md |
| FIX6最终提交 | 即本提交(docs-only回填run#1) | run#2于本提交推送后触发,head_sha=本提交,run#/job#以Git外验收附件为准(防预写) |

- 增量差异 `2c36cf9 → FIX6实现`: `scripts/allocation_engine.py | 15 insertions(+), 6 deletions(-)` + 新增 `tests/test_p02_w2_fix6.py`(468行)。
- 累计差异 `69d7fc7 → FIX6实现`: 37文件,9952+/218−(W1封印后全部W2轮次)。

## 3. 诊断模式缺陷与修复说明(IA-P02-W2-FIX5-DEF-001)

**缺陷**: `verify_evidence_items()` 的 as_of_date=None 受限诊断路径中,
verified 条目把 `observation_freshness` 固定硬编码为 `'FRESH'`。诊断模式下
观测时效**从未被评估**(无研究截止→无法算滞后/窗口),写入 FRESH 即
"未计算却claim新鲜"。验收反例(指令§5.1): CPI 316.0/obs 2026-09-01/锚点含
as_of="2026-10-25",调用 as_of_date=None——前5步(verified非空/数值/观测日/
身份/不授予点时认证)全部正确,唯第6步新鲜度字段错误。

**修复(最小增量,仅诊断分支输出)**:
- 引入路径相关变量 `obs_fresh_status`: 正式路径 `'FRESH'`(纯观测时效已真实
  计算,usable⇒纯观测必为FRESH,语义不变);诊断路径 `'NOT_ASSESSED'`
  (未评估——不得写FRESH[未计算不得claim新鲜],亦不得写STALE[未知≠过期])。
- 诊断分支 pit.reason 重写为: `DIAGNOSTIC_ONLY: 未提供研究截止(as_of),无法
  验证观测新鲜度及点时可得性——仅数值/观测对齐+身份核验,不做时效门禁,不
  授予任何时效认证,不得作为已认证正式证据;verified.as_of仅为锚点元数据
  透传,非正式研究截止`。
- 文档字符串同步(第379行区域)。函数签名 `(verified, rejects)`、核验顺序、
  正式路径行为零改动。

**未改动项(§5.4/§十一遵守)**: freshness_policy.py、data_validator.py、
metric_registry.json、81项窗口、W1语义、P0-1来源门禁全部未触碰;
未把一处诊断字段错误扩张为重构;合法数值诊断结果保留(不因无法判时效删除)。

**下游消费审计(§八)**: 全仓扫描确认无任何脚本读取
`verified[i]['observation_freshness']`(纯披露字段);星级门槛/台账/未认证
披露全部键 off `point_time_certified`(诊断恒为False)→ NOT_ASSESSED 对下游
零行为影响,亦不会被误认为正式认证。未发现可调用绕过(诊断路径身份核验
照常,D2/D3负向测试证明)。

## 4. None与合法as_of区分(三路径,FIX6-02保持)

| 路径 | 判定 | 行为 | 本轮验证 |
|---|---|---|---|
| 受限诊断 | `as_of_date is None`(存在性判断) | 身份/数值/观测日核验照常;不做时效门禁;pit=AS_OF_UNKNOWN;certified=False;**observation_freshness=NOT_ASSESSED** | A/B/C/D/H2 |
| 正式 | 合法date或完整ISO时刻或可解析字符串 | 窗口新鲜度真实计算+点时核验+evidence_eligibility门禁+verified保留pit字段——**行为零改动** | B2/C1/C2/F1~F5/H1 |
| 显式非法 | ''/空白/0/False/[]/{}/带后缀日/非法日历/非法时刻 | 整项拒收"研究截止非法",不落诊断(真值绕过不回归) | E1/H3 |

## 5. 锚点自带as_of证据边界(§5.3)

锚点的 `as_of="2026-10-25"` 是元数据: 调用仍传 None 时**不得**提升为正式
研究截止。B1/B2证明: 诊断结果 NOT_ASSESSED,同锚点正式调用才得 FRESH
——两者可区分,证明诊断模式没有用锚点as_of偷偷计算时效;verified['as_of']
仅为锚点元数据透传,其来源与限度在 pit.reason 中明示("锚点元数据透传,
非正式研究截止")。

## 6. 真实模块反例与测试结果(固定反例,真实verify_evidence_items)

tests/test_p02_w2_fix6.py(A组,真实调用): as_of_date=None →
verified非空;数值316.0/观测日2026-09-01核验通过;身份核验通过;
`observation_freshness == 'NOT_ASSESSED'`(≠FRESH≠STALE≠PASS);
`point_in_time.status == 'AS_OF_UNKNOWN'`;`point_in_time_certified is False`;
reason含DIAGNOSTIC_ONLY+"无法验证观测新鲜度";诊断记录负面扫描无
FRESH/PASS/已认证字样。全套件 **21检查全过**。

## 7. 来源身份负向测试(诊断模式不得绕过身份核验)

D2 非法来源 `global_market.data.CPI.close` + None → 拒收"身份不可认证";
D3 未注册键 `other.data.NOPE.value` + None → 拒收(UNMAPPED);
D1 合法CPI + None → 受限诊断允许(NOT_ASSESSED)。FIX5语义原样保持。

## 8. 正式资格与长期状态回归(F/H组)

- F1 未来发布(10-29>10-25)→ 拒"点时不可得…晚于研究截止";F2 观测过期
  (滞后70>窗60)→ 拒"数据过期",适配接口纯观测lag=70/窗=60精确;
  F3 非法发布时间 → 拒"时间资格不成立(INVALID_RELEASE)";F4 混合精度
  (naive×date-only)→ UNCERTIFIED保留+certified=False;F5 合法双aware时刻
  → certified=True+INSTANT。FIX5五情形逐项保持。
- H1 正常正式研究可运行(Gate A/B无回归,exit0+GLM恰1次+四对象落盘);
  H2 真实锚点None诊断下游不误认(uncertified_note非空+星级desc
  "已认证0·未认证1");H4 已知未来发布真实链路拒(事实FAIL NOT_AVAILABLE
  →Gate A FAIL→da exit2→rg exit2+GLM 0次);H5 四对象
  (weekly_report/report_status/thesis.json/allocation_views.json)SHA-256
  全程==基线,无新报告/状态文件,published=true仅发布日,formal身份有效,
  scan不变——长期状态零触碰,无任何合成状态写入需要。

## 9. 全量CI(GitHub Actions,dev/p0-2-w2,workflow_dispatch)

**实现提交 run#1**: run `41005413020` / job `123899087846` / head_sha
`e091d288cd3cff910e4894fabe2d426db7aa1475` → **success**。逐套件exit码:
39套件全部 `exit=0`(38历史套件+新增test_p02_w2_fix6),`Traceback`计数0,
`test_glm_live: SKIPPED(真实GLM付费调用,不进CI)`。

**最终提交 run#2**: 本提交推送后触发,head_sha=本提交(验算于Git外验收附件:
run#/job#/conclusion/逐套件exit码/Traceback计数——不预写任何未发生的数字)。

## 10. 最终DEV/LIVE只读隔离证据(§十二,最终提交固定后执行)

待回填: 核查时间/DEV与LIVE realpath/DEV git root与最终HEAD/当前分支/
origin main/launchd exec路径/LIVE核心源码SHA-256 vs P0-1封印/LIVE无W2模块
证据/无生产部署。结果以Git外只读附件交付Agent 4,不写入仓库(避免改变已
固定的SHA)。

## 11. 未验证事项

- Mac LIVE生产链路未做任何写操作(禁令);LIVE侧行为未验证,仅只读证明
  其源码==P0-1封印且不含W2模块。
- 真实GLM API调用未执行(禁令;全部mock,≥500字防截断保护)。
- diagnostic record 在"外部消费者直接读observation_freshness字段"场景下
  的行为: 全仓无此类消费者(审计见§3),NOT_ASSESSED语义仅对人类读者承诺。
- W2整体PASS与否、P0-2是否关闭: 属Agent 4独立验收,本轮不判定。
