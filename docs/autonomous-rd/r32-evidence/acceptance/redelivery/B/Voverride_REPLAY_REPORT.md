# 离线重放报告(Audit-R28 任务4)

- 交付包: `/tmp/r32-accept/archive/r32v/20261123T235121Z_对比角度换一个_2026年11月_美国与欧元区的增长和通胀环境相比3个月前各有什`
- 完整运行 SHA: `36499bb78a18dea1ff2b027074088b0ba404c3b8`(当前重放代码 `cf33de3a9942578b71cecb45077b7a505d8fca01`)
- 归档代码 SHA: `cf33de3a9942578b71cecb45077b7a505d8fca01`(裁决后再交付包;本次为异版代码经 --allow-code-mismatch 越过版本门后的披露性重放,非录制代码)
- 原问: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- 裁决: UPHELD(链 2 档)
- 重渲模式: byte_equal

## 检查明细

- [PASS] manifest_present_parseable——/tmp/r32-accept/archive/r32v/20261123T235121Z_对比角度换一个_2026年11月_美国与欧元区的增长和通胀环境相比3个月前各有什/ARCHIVE_MANIFEST.json
- [PASS] completeness_files——缺件=无 裁决链缺档=无
- [PASS] verdict_chain_nonempty——链档数=2(archive 段交付门要求≥1 在案裁决)
- [PASS] copies_sha16_match——哈希不符=无 清单漏记=无
- [PASS] map_fullfile_anchor——锚=b9b0916548473b2c 实测=b9b0916548473b2c(旁挂锚=防单改在场文件)
- [PASS] question_verbatim_bytes——包内原问 196 字节 vs manifest.question 196 字节(逐字节)
- [PASS] frozen_inputs_present——overlay 缺件=无(root_overlay/ 布局=渲染依赖随包冻结)
- [PASS] frozen_inputs_digests——冻结件摘要不符=无
- [PASS] frozen_inputs_match_report——一致
- [PASS] run_code_sha_crosscheck——manifest=36499bb78a18dea1ff2b027074088b0ba404c3b8 report.json.run=36499bb78a18dea1ff2b027074088b0ba404c3b8(完整运行 SHA 两处一致)
- [PASS] content_digest_match——重算=6d8a36053e4224fe manifest=6d8a36053e4224fe(摘要算法=manifest.digest_algorithm)
- [PASS] verdict_chain_hashes——链档异常=无
- [PASS] verdict_binding_threeway——绑定异常=无(run=归档=裁决锚三面一致)
- [PASS] code_version_match——当前=cf33de3a9942578b71cecb45077b7a505d8fca01 包=36499bb78a18dea1ff2b027074088b0ba404c3b8(--allow-code-mismatch 披露越过)
- [PASS] deterministic_rerender——冻结输入按当前代码重渲与归档 MAP_REPORT.md 逐字节相等(33481 字节)
- [PASS] package_untouched_postwrite——写毕复算包摘要=6d8a36053e4224fe(与 manifest 一致=原档未被重放触碰)

## 结论

重放通过: 16 项检查 16 过 0 拒。
重复运行另开新档,原包未写入(post-write 摘要复核在档)。
