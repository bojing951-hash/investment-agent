# 离线重放报告(Audit-R28 任务4)

- 交付包: `/tmp/r31-accept/replay-A4/20261122T213300/pkg-rewr`
- 完整运行 SHA: `ca916cdca7b749282e498d8c8f0eac8bf43b7372`(当前重放代码 `ca916cdca7b749282e498d8c8f0eac8bf43b7372`)
- 原问: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 裁决: UPHELD(链 1 档)
- 重渲模式: byte_equal

## 检查明细

- [PASS] manifest_present_parseable——/tmp/r31-accept/replay-A4/20261122T213300/pkg-rewr/ARCHIVE_MANIFEST.json
- [PASS] completeness_files——缺件=无 裁决链缺档=无
- [PASS] verdict_chain_nonempty——链档数=1(archive 段交付门要求≥1 在案裁决)
- [PASS] copies_sha16_match——哈希不符=无 清单漏记=无
- [PASS] map_fullfile_anchor——锚=811b161d05f3206b 实测=811b161d05f3206b(旁挂锚=防单改在场文件)
- [PASS] question_verbatim_bytes——包内原问 490 字节 vs manifest.question 490 字节(逐字节)
- [PASS] frozen_inputs_present——overlay 缺件=无(root_overlay/ 布局=渲染依赖随包冻结)
- [FAIL] frozen_inputs_digests——冻结件摘要不符=['config/release_calendar.json: manifest=deadbeef actual=e44fd2aa5ced0310']
- [FAIL] frozen_inputs_match_report——run.frozen_inputs=[('config/metric_registry.json', 'fa396d22175a4814'), ('config/release_calendar.json', 'e44fd2aa5ced0310'), ('data/daily/research_snapshot_20261122.json', 'eabee6b470a8e959')] manifest=[('config/metric_registry.json', 'fa396d22175a4814'), ('config/release_calendar.json', 'deadbeef'), ('data/daily/research_snapshot_20261122.json', 'eabee6b470a8e959')](渲染依赖身份三面之一;失配=包或报告被单侧改写)
- [PASS] run_code_sha_crosscheck——manifest=ca916cdca7b749282e498d8c8f0eac8bf43b7372 report.json.run=ca916cdca7b749282e498d8c8f0eac8bf43b7372(完整运行 SHA 两处一致)
- [PASS] content_digest_match——重算=73f2dd4fa532a9c6 manifest=73f2dd4fa532a9c6(摘要算法=manifest.digest_algorithm)
- [PASS] verdict_chain_hashes——链档异常=无
- [PASS] verdict_binding_threeway——绑定异常=无(run=归档=裁决锚三面一致)
- [PASS] code_version_match——当前=ca916cdca7b749282e498d8c8f0eac8bf43b7372 包=ca916cdca7b749282e498d8c8f0eac8bf43b7372
- [PASS] deterministic_rerender——冻结输入按当前代码重渲与归档 MAP_REPORT.md 逐字节相等(102180 字节)
- [PASS] package_untouched_postwrite——写毕复算包摘要=73f2dd4fa532a9c6(与 manifest 一致=原档未被重放触碰)

## 结论

重放拒绝: 16 项检查 14 过 2 拒。
重复运行另开新档,原包未写入(post-write 摘要复核在档)。
