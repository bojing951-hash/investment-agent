# 离线重放报告(Audit-R28 任务4)

- 交付包: `/tmp/r31-accept/replay-B2/20261122T213336/pkg-miss`
- 完整运行 SHA: `ca916cdca7b749282e498d8c8f0eac8bf43b7372`(当前重放代码 `ca916cdca7b749282e498d8c8f0eac8bf43b7372`)
- 原问: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- 裁决: UPHELD(链 1 档)
- 重渲模式: byte_equal

## 检查明细

- [PASS] manifest_present_parseable——/tmp/r31-accept/replay-B2/20261122T213336/pkg-miss/ARCHIVE_MANIFEST.json
- [PASS] completeness_files——缺件=无 裁决链缺档=无
- [PASS] verdict_chain_nonempty——链档数=1(archive 段交付门要求≥1 在案裁决)
- [PASS] copies_sha16_match——哈希不符=无 清单漏记=无
- [PASS] map_fullfile_anchor——锚=10a11da6990be845 实测=10a11da6990be845(旁挂锚=防单改在场文件)
- [PASS] question_verbatim_bytes——包内原问 196 字节 vs manifest.question 196 字节(逐字节)
- [FAIL] frozen_inputs_present——overlay 缺件=['config/release_calendar.json'](root_overlay/ 布局=渲染依赖随包冻结)
- [FAIL] frozen_inputs_digests——冻结件摘要不符=['config/release_calendar.json: manifest=e44fd2aa5ced0310 actual=缺席']
- [PASS] frozen_inputs_match_report——一致
- [PASS] run_code_sha_crosscheck——manifest=ca916cdca7b749282e498d8c8f0eac8bf43b7372 report.json.run=ca916cdca7b749282e498d8c8f0eac8bf43b7372(完整运行 SHA 两处一致)
- [PASS] content_digest_match——重算=bf5440664aec3d19 manifest=bf5440664aec3d19(摘要算法=manifest.digest_algorithm)
- [PASS] verdict_chain_hashes——链档异常=无
- [PASS] verdict_binding_threeway——绑定异常=无(run=归档=裁决锚三面一致)
- [PASS] code_version_match——当前=ca916cdca7b749282e498d8c8f0eac8bf43b7372 包=ca916cdca7b749282e498d8c8f0eac8bf43b7372
- [PASS] deterministic_rerender——冻结输入按当前代码重渲与归档 MAP_REPORT.md 逐字节相等(25709 字节)
- [PASS] package_untouched_postwrite——写毕复算包摘要=bf5440664aec3d19(与 manifest 一致=原档未被重放触碰)

## 结论

重放拒绝: 16 项检查 14 过 2 拒。
重复运行另开新档,原包未写入(post-write 摘要复核在档)。
