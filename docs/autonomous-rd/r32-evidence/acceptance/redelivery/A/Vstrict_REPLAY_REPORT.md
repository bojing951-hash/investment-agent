# 离线重放报告(Audit-R28 任务4)

- 交付包: `/tmp/r32-accept/archive/r32v/20261123T235103Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最`
- 完整运行 SHA: `36499bb78a18dea1ff2b027074088b0ba404c3b8`(当前重放代码 `cf33de3a9942578b71cecb45077b7a505d8fca01`)
- 归档代码 SHA: `cf33de3a9942578b71cecb45077b7a505d8fca01`(裁决后再交付包: 运行=执行印章、交付字节=归档印章;清单已声明状态面等价)
- 原问: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 裁决: UPHELD(链 1 档)
- 重渲模式: byte_equal

## 检查明细

- [PASS] manifest_present_parseable——/tmp/r32-accept/archive/r32v/20261123T235103Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最/ARCHIVE_MANIFEST.json
- [PASS] completeness_files——缺件=无 裁决链缺档=无
- [PASS] verdict_chain_nonempty——链档数=1(archive 段交付门要求≥1 在案裁决)
- [PASS] copies_sha16_match——哈希不符=无 清单漏记=无
- [PASS] map_fullfile_anchor——锚=b19b007c2ecbf1e0 实测=b19b007c2ecbf1e0(旁挂锚=防单改在场文件)
- [PASS] question_verbatim_bytes——包内原问 490 字节 vs manifest.question 490 字节(逐字节)
- [PASS] frozen_inputs_present——overlay 缺件=无(root_overlay/ 布局=渲染依赖随包冻结)
- [PASS] frozen_inputs_digests——冻结件摘要不符=无
- [PASS] frozen_inputs_match_report——一致
- [PASS] run_code_sha_crosscheck——manifest=36499bb78a18dea1ff2b027074088b0ba404c3b8 report.json.run=36499bb78a18dea1ff2b027074088b0ba404c3b8(完整运行 SHA 两处一致)
- [PASS] content_digest_match——重算=f9d761c4151a358d manifest=f9d761c4151a358d(摘要算法=manifest.digest_algorithm)
- [PASS] verdict_chain_hashes——链档异常=无
- [PASS] verdict_binding_threeway——绑定异常=无(run=归档=裁决锚三面一致;地图内容段与裁决绑定仅差审查状态短语,清单已声明)
- [PASS] code_version_match——当前=cf33de3a9942578b71cecb45077b7a505d8fca01 包=36499bb78a18dea1ff2b027074088b0ba404c3b8(当前=归档代码 cf33de3a9942578b71cecb45077b7a505d8fca01: 裁决后再交付包,清单已声明)
- [PASS] deterministic_rerender——冻结输入按当前代码重渲与归档 MAP_REPORT.md 逐字节相等(131375 字节)
- [PASS] package_untouched_postwrite——写毕复算包摘要=f9d761c4151a358d(与 manifest 一致=原档未被重放触碰)

## 结论

重放通过: 16 项检查 16 过 0 拒。
重复运行另开新档,原包未写入(post-write 摘要复核在档)。
