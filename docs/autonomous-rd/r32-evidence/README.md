# Audit-R32 证据包

- 链: 基线 `72dab1c`(PR #1 head=独立审计)→ a967bd2 / 5b37e73 / deabd45 / f722e3c / 19638e1 / 0f3936d /
  8f9055d → **执行印章 `36499bb`**(五工单的规划/挂接/独立审查在此印章运行;CI `45291551484` 绿)
  → `facc9a8`(裁决后交付状态面;CI `45330060557` 绿)→ `24141c0`(两印章包;CI `45337815174` 绿)
  → `37691b7`(错误转弯,已撤回;该印章下无任何交付;CI `45348011655` 红)→ **最终印章 `cf33de3`**
  (报告/归档/重放;CI `45351387852` 绿)→ 证据与报告提交 `f46fdcb`(纯文档;CI `45369284776` 绿)
  → 重放回执提交 `b7ff06b`(纯文档;CI `45373759295` 绿)→ 更正提交 `12edab8`(任务3: R31 NEW30
  入库包两份裁决件改回清单所记名——仅改名;R32 门 111/111;只动测试与文档)
  → 重放回执提交(本提交;纯文档,只多回执: 从更正提交重新下载的七包重放回执+更正提交的电池与 CI 回执)
- 报告: `../AUDIT_R32_REPORT.md`。公开清洗规则同 R31: 私有路径 `~` 归一、零键形、不含任何模型
  厂商名称(登记在 `acceptance/REDACTIONS.md`+`redactions_registry.json`;词表留仓外)
- acceptance/questions: 六问原句(A=四地地图正问/B=换问对比/T3=审计原问: 官方目标+待生效+同比/
  NEW30=裸年月+六个月窗/aug=显式 8 月时点/open=C4 残缺树问句),均经 `--question-file` 逐字输入
- acceptance/session_A_formal·session_B_formal·session_T3_formal·session_NEW30: 四个正式工单在
  最终印章交付的归档包逐字节副本(隔离路径归档: 九件套+root_overlay 三件+verdicts+ARCHIVE_MANIFEST;
  包内运行 SHA=执行印章 36499bb,清单另记归档代码 cf33de3)
- acceptance/session_C4_degraded: 残缺树草稿的运行件+归档拒绝回执(blocked=not_deliverable,零归档目录)
- acceptance/redelivery/<工单>: 执行印章运行目录移入最终印章树的逐文件 sha256 清单、最终印章的
  回执(再规划/报告/归档)与执行印章挂接回执、地图内容段一行对照、交付后包在验收树上的重放回执
  (最终印章引擎严格重放/执行印章引擎严格重放/B 包另加显式越过的披露重放)、该工单的席位台账行
- acceptance/reviews: 各印章独立席位的规程、裁决与散文全文(VERDICT/PROSE)及其复算脚本、复算点与
  中间产出(`_dir_listing.txt`=该席目录完整清单;席位的 scratch 子目录、大于 2.5 MB 的文件与早先的
  裁决稿 `.before-*` 只列清单,每轮登记的裁决=该轮最终稿)。
  目录前缀=印章: (无前缀)=执行印章 36499bb;superseded_8f9055d_ / superseded_0f3936d_ /
  superseded_19638e1_ / pre_f722e3c_=被取代印章。aborted_attempts_listing.txt=未形成裁决的
  中止尝试(仅清单)
- acceptance/builder_folds·operator_tools: 研判席修订脚本(每条替换以冻结面重算的数字与断言为据)、
  修订日志、修订后干跑校验输出,以及验收流程用到的操作者工具全文(可重跑)
- acceptance/aug_plan: 显式 8 月截止问正式 CLI 验收(提交的 11 月快照;最终印章 L1 31 行零晚观测、
  证据索引 55 条零晚引用;基线 31/31、56/56 的复现在 wave0_r32/baseline_reproduction_72dab1c)
- acceptance/cross_stamp_comparison: 同一冻结输入下各工单引擎面逐键比对(0f3936d→8f9055d: cmp_X_*;
  8f9055d→36499bb: cmp_Y_*;36499bb→24141c0: cmp_W_*;36499bb→cf33de3: cmp_V_*;冻结输入逐文件 sha 零差异)
- acceptance/engine_fix_*: 真跑与独立审查发现的六处交付/渲染缺陷各自的复现(门红档)→补丁→门绿档
  →提交说明: official_record(官方记录面读格级键)/reader_report(读者报告渲染六处)/
  lpr_publication_rule(LPR 推定公布日规则②)/post_verdict_status(裁决后交付状态面)/
  two_stamp_package(两印章再交付包)/same_render_package(同渲染包: 错误转弯与撤回更正)
- acceptance/superseded_19638e1·superseded_0f3936d·superseded_8f9055d: 被取代印章上五工单的正式
  入口回执(裁决绑定版本,不跨印章复用,故各印章都重新规划与重审)
- acceptance/superseded_36499bb·superseded_facc9a8·superseded_24141c0: 执行印章裁决之后、最终印章之前
  的三次交付(只留回执与归档清单;包在仓外隔离归档区)。37691b7 下无交付,故无对应目录
- acceptance/wave0_r32: 电池回执(只留状态/rc/文件三列,原始日志留仓外)+CI 回执+干净安装与标准
  更新入口回执(各印章;最终印章的首次运行失败回执、时间表、直接运行与同日重跑回执、守卫只读复算回执、重跑后冒烟)
  +基线复现+首次修复后对照+最终门日志;task3_correction=任务3 更正(改名干跑日志、工作树上的门
  日志、更正提交的 CI 与电池回执、重下重放链的控制台与七包重渲摘要对照);post_commit=证据提交后与
  更正提交后的复跑(phase6 29/0)
- acceptance/replays: 从更正提交 `12edab8` 重新下载实包的重放回执(R31 A4/B2/NEW30 与 R32 四包;C4
  无包=不适用): `replayed_commit.txt`=克隆的提交;逐包子目录的 `console.log`、提交树清单、各步重放
  信封与 `REPLAY_REPORT.md`;主日志;因公网取数失败中止的两次控制台留档(`console_attempt1_aborted_network.log`,
  在 A4、B2 子目录)。`superseded_f46fdcb/`=上一版回执(证据提交 `f46fdcb` 上)原样移存: 结果同上,
  唯 R31 NEW30 包因入库副本的裁决件改名缺陷被拒——更正前形态的实录(报告任务3「更正」);上一版
  首跑中止的控制台留档(`console_attempt1_aborted_*.log`)亦在其中
- 更正(报告任务3「更正」): R31 证据包 `../r31-evidence/acceptance/session_NEW30/verdicts/` 的两份
  裁决件在 R31 装包时被改存为无日目录前缀的名,清单所记名为 `20261123__VERDICT-*.json`;更正提交
  改回清单所记名(字节不变,仅改名;原始归档包逐件相同)。R32 四包不受影响
