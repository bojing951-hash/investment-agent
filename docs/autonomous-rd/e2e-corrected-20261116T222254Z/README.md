# E2E 20261116T222254Z 修正复算包(Audit-R5 条目3)

对象: `20261116T222254Z_美国盈亏平衡通胀预期_BEI_10Y_上行阶段_黄金_GOLD_F_与美元指数_`
——第五轮审计条目3指出的三处统计错误,修正后的完整计算原件与本包重放。

## 修正内容(同版原始输入复算确认)

| # | 原文 | 修正后 | 依据 |
|---|------|--------|------|
| 1 | corr(dBEI,dBRENT)=+0.3383 解释为「约三成方差」「供给冲击先行载体」 | r²≈0.114,即约11.4%方差(含截距一元线性回归);同期统计关联,非先行关系、非因果贡献 | r=0.3383 复算吻合;r²=0.3383²≈0.1145 |
| 2 | 金方程 se_dBEI=0.678、美元方程 se_dBEI=0.256 | 0.686 / 0.259 | 经典标准误复算(df=n−k);β/R² 原值吻合;随修 t 末位 +4.5→+4.4(精确 4.4489) |
| 3 | 63日滚动最长连续非负段 55窗(2022-03-09..2022-05-26) | 终点 2022-05-25;窗末 2022-05-26 的 r=−0.0148 已转负 | 逐窗复算;两处镜像(mech-3 与 contradictions[0])同步修 |

口径披露补强: 全样本 −0.3941(n=2493)在五序列交集上;63日滚动 2449 窗在
金/美元对齐变化对(2511)上——原正文两口径未区分,已补明。

## 文件

- `research_seat_calc.py` —— 研究席实际使用的自算脚本(仓内固化版)。
  与实际运行的唯一差异 = 输入路径参数化(原为 `/Users/cast/investment-agent-dev/...`
  绝对路径;`--data` 默认本包切片,内容同版)。
- `independent_recompute.py` —— 操作者席独立复算脚本(零引用研究席/前审查席
  中间结果,自写实现),逐项判定三争点修正数值。
- `data_slice.json` —— 同版原始输入完整抽取(GOLD_F/DXY/VIX/BRENT_F +
  BEI_10Y/UST_10Y/TIPS_10Y),重放不依赖源文件在场。

## 同版证明

源文件 sha256(`data_slice.json` 内 `provenance`):

- `research_snapshot_20261112_v2.json`(GOLD_F/DXY/VIX/BRENT_F, n=2514/2515)
- `macro_20261114.json`(BEI_10Y n=2499, UST_10Y/TIPS_10Y n=2498)

## 空目录重放

克隆本仓后,仓库根一条命令(两脚本均可独立重放,输入均默认本包切片):

```
python3 docs/autonomous-rd/e2e-corrected-20261116T222254Z/independent_recompute.py
python3 docs/autonomous-rd/e2e-corrected-20261116T222254Z/research_seat_calc.py   # 研究席口径全量打印
```

依赖: 仅 Python 3 标准库。

## 修正后的审查链

内容变化 → 旧裁决(UPHELD rev1,20261117,sha 252057d984f2a63c)按摘要失配
自动失效 → 未参与修复的独立席位复审(rev2,predecessor=rev1)→ 通过后
新归档目录(旧归档 append-only 保留)。见 `AUDIT_R5_REPORT.md` 条目3。
