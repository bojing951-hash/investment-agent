# 离线重放报告(Audit-R28 任务4)

- 交付包: `/tmp/r32-accept/archive/r32w/20261123T235139Z_2026年11月_日本和欧元区的通胀与政策环境_两地央行当前官方政策目标利率各处`
- 完整运行 SHA: `36499bb78a18dea1ff2b027074088b0ba404c3b8`(当前重放代码 `24141c01a73daa44e56e380320f46bb0f7cbd723`)
- 归档代码 SHA: `24141c01a73daa44e56e380320f46bb0f7cbd723`(裁决后再交付包: 运行=执行印章、交付字节=归档印章;清单已声明状态面等价)
- 原问: 2026年11月,日本和欧元区的通胀与政策环境:两地央行当前官方政策目标利率各处于什么水平?最近六个月有无已决议但尚未生效的调整?两地通胀同比最新读数相比去年同月如何?请给出具体数据和各数据的公布时间。
- 裁决: UPHELD(链 1 档)
- 重渲模式: byte_equal

## 检查明细

- [PASS] manifest_present_parseable——/tmp/r32-accept/archive/r32w/20261123T235139Z_2026年11月_日本和欧元区的通胀与政策环境_两地央行当前官方政策目标利率各处/ARCHIVE_MANIFEST.json
- [PASS] completeness_files——缺件=无 裁决链缺档=无
- [PASS] verdict_chain_nonempty——链档数=1(archive 段交付门要求≥1 在案裁决)
- [PASS] copies_sha16_match——哈希不符=无 清单漏记=无
- [PASS] map_fullfile_anchor——锚=56dea8f77346d464 实测=56dea8f77346d464(旁挂锚=防单改在场文件)
- [PASS] question_verbatim_bytes——包内原问 281 字节 vs manifest.question 281 字节(逐字节)
- [PASS] frozen_inputs_present——overlay 缺件=无(root_overlay/ 布局=渲染依赖随包冻结)
- [PASS] frozen_inputs_digests——冻结件摘要不符=无
- [PASS] frozen_inputs_match_report——一致
- [PASS] run_code_sha_crosscheck——manifest=36499bb78a18dea1ff2b027074088b0ba404c3b8 report.json.run=36499bb78a18dea1ff2b027074088b0ba404c3b8(完整运行 SHA 两处一致)
- [PASS] content_digest_match——重算=db46ca7959ea8653 manifest=db46ca7959ea8653(摘要算法=manifest.digest_algorithm)
- [PASS] verdict_chain_hashes——链档异常=无
- [PASS] verdict_binding_threeway——绑定异常=无(run=归档=裁决锚三面一致;地图内容段与裁决绑定仅差审查状态短语,清单已声明)
- [PASS] code_version_match——当前=24141c01a73daa44e56e380320f46bb0f7cbd723 包=36499bb78a18dea1ff2b027074088b0ba404c3b8(当前=归档代码 24141c01a73daa44e56e380320f46bb0f7cbd723: 裁决后再交付包,清单已声明)
- [PASS] deterministic_rerender——冻结输入按当前代码重渲与归档 MAP_REPORT.md 逐字节相等(33998 字节)
- [PASS] package_untouched_postwrite——写毕复算包摘要=db46ca7959ea8653(与 manifest 一致=原档未被重放触碰)

## 结论

重放通过: 16 项检查 16 过 0 拒。
重复运行另开新档,原包未写入(post-write 摘要复核在档)。
