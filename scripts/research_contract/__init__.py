# -*- coding: utf-8 -*-
"""research_contract 包 — 架构整改阶段三统一断言层(PHASE2-CONTRACT §1/§5)。

五小模块布局(禁 god-module,本包只做断言层,采集/快照/统计全保留旧路径):
  claim_factory.py     确定性六型断言工厂+谓词文法+单位代数(零模型调用)   [T4]
  claim_bundle.py      ResearchClaim v1.0 bundle 容器/schema/读写           [T4]
  claim_verifier.py    六状态确定性验证                                    [T5,未落]
  render_hook.py       确定性渲染模板+manifest(C1 载重墙)                 [T6,未落]
  text_consistency.py  数值溯源门(律8 修后版)                             [T6,未落]

纪律: 本包不 import 任何模型客户端、不读任何环境变量、零网络。
"""
