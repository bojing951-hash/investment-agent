# 离线重放报告(Audit-R28 任务4)

- 交付包: `/tmp/r32-accept/archive/r32v/20261123T235157Z_2026年11月_日本和欧元区最近六个月的通胀与政策环境有什么不同_哪些方面分化`
- 完整运行 SHA: `36499bb78a18dea1ff2b027074088b0ba404c3b8`(当前重放代码 `cf33de3a9942578b71cecb45077b7a505d8fca01`)
- 归档代码 SHA: `cf33de3a9942578b71cecb45077b7a505d8fca01`(裁决后再交付包: 运行=执行印章、交付字节=归档印章;清单已声明状态面等价)
- 原问: 2026年11月,日本和欧元区最近六个月的通胀与政策环境有什么不同?哪些方面分化,哪些证据不足?请给出具体数据和各数据的公布时间。
- 裁决: UPHELD(链 1 档)
- 重渲模式: byte_equal

## 检查明细

- [PASS] manifest_present_parseable——/tmp/r32-accept/archive/r32v/20261123T235157Z_2026年11月_日本和欧元区最近六个月的通胀与政策环境有什么不同_哪些方面分化/ARCHIVE_MANIFEST.json
- [PASS] completeness_files——缺件=无 裁决链缺档=无
- [PASS] verdict_chain_nonempty——链档数=1(archive 段交付门要求≥1 在案裁决)
- [PASS] copies_sha16_match——哈希不符=无 清单漏记=无
- [PASS] map_fullfile_anchor——锚=c33dc7dc8f961e22 实测=c33dc7dc8f961e22(旁挂锚=防单改在场文件)
- [PASS] question_verbatim_bytes——包内原问 175 字节 vs manifest.question 175 字节(逐字节)
- [PASS] frozen_inputs_present——overlay 缺件=无(root_overlay/ 布局=渲染依赖随包冻结)
- [PASS] frozen_inputs_digests——冻结件摘要不符=无
- [PASS] frozen_inputs_match_report——一致
- [PASS] run_code_sha_crosscheck——manifest=36499bb78a18dea1ff2b027074088b0ba404c3b8 report.json.run=36499bb78a18dea1ff2b027074088b0ba404c3b8(完整运行 SHA 两处一致)
- [PASS] content_digest_match——重算=bb7ab46162ac0f28 manifest=bb7ab46162ac0f28(摘要算法=manifest.digest_algorithm)
- [PASS] verdict_chain_hashes——链档异常=无
- [PASS] verdict_binding_threeway——绑定异常=无(run=归档=裁决锚三面一致;地图内容段与裁决绑定仅差审查状态短语,清单已声明)
- [PASS] code_version_match——当前=cf33de3a9942578b71cecb45077b7a505d8fca01 包=36499bb78a18dea1ff2b027074088b0ba404c3b8(当前=归档代码 cf33de3a9942578b71cecb45077b7a505d8fca01: 裁决后再交付包,清单已声明)
- [PASS] deterministic_rerender——冻结输入按当前代码重渲与归档 MAP_REPORT.md 逐字节相等(37004 字节)
- [PASS] package_untouched_postwrite——写毕复算包摘要=bb7ab46162ac0f28(与 manifest 一致=原档未被重放触碰)

## 结论

重放通过: 16 项检查 16 过 0 拒。
重复运行另开新档,原包未写入(post-write 摘要复核在档)。
