# R003 关键命令日志(附录D来源)

会话: 执行Agent Round 003,分支 dev/p0-2-w5-attr(基点 10207929c8d505845ac30f8af9a742b124b0f4d5)
时间: 2026-11-01(UTC+8)。所有写类操作仅指向 DEV 允许路径与 /tmp/w5_attr_scratch。

## 0. 开轮自检
```
git -C /Users/cast/investment-agent-dev status                 # clean, on dev/p0-2-w5
git -C /Users/cast/investment-agent-dev rev-parse HEAD         # 10207929c8d505845ac30f8af9a742b124b0f4d5
git -C /Users/cast/investment-agent-dev ls-remote origin       # 远端分支全量实取(见卷宗差异清单)
```

## 1. 任务A 证据包核验
```
ls -la /tmp/w5-evidence/
shasum -a 256 /tmp/w5-evidence/*.zip
#   6e59f9cb9ad5580b9c2f9e75d9eaff0ed5cb61502af1e0a37ab5c310d739feeb  IA-P0-2-W5-ACCEPTANCE-EVIDENCE.zip
#   b5f070a556d359de9590b816074f36e6c8d38738af07f4b8856c63b89ec647e8  IA-P0-2-W5-FIX1-ACCEPTANCE-EVIDENCE.zip
unzip -l /tmp/w5-evidence/IA-P0-2-W5-FIX1-ACCEPTANCE-EVIDENCE.zip   # 22条目(21文件+1目录)
unzip -l /tmp/w5-evidence/IA-P0-2-W5-ACCEPTANCE-EVIDENCE.zip         # 17条目(16文件+1目录)
mkdir -p /tmp/w5_attr_scratch/fix1 /tmp/w5_attr_scratch/w5r1
unzip -q .../FIX1...zip -d /tmp/w5_attr_scratch/fix1
unzip -q .../W5-...zip  -d /tmp/w5_attr_scratch/w5r1
( cd /tmp/w5_attr_scratch/fix1 && shasum -a 256 -c SHA256SUMS )      # 20/20 OK
( cd /tmp/w5_attr_scratch/w5r1  && shasum -a 256 -c SHA256SUMS.txt ) # 15/15 OK
python3 - <<...  # real_acceptance JSON 扁平化转储到 /tmp/w5_attr_scratch/json_flat.txt(1011行)
```

## 2. 任务B 合同检索
```
# 类1: DEV git 全历史(109 commits)
git -C ... rev-list --all > /tmp/w5_attr_scratch/all_commits.txt    # 109
git -C ... log --all --oneline -S 'IA-P0-2-W5-FIX1-AC'              # 仅 4a19619
git -C ... log --all --oneline -S 'IA-P0-2-W5-FIX1-DEV'             # f1b6e42, 4a19619
git -C ... log --all --oneline -G 'W5-FIX1.*(验收条件|通过条件|冻结合同)'  # 零命中
# 逐commit树grep(python驱动 subprocess,对109个commit逐一):
git -C ... grep -l 'IA-P0-2-W5-FIX1-AC' <每个commit>
#   -> 仅 docs/P0_2_W5_FIX1_DELIVERY.md @ 4a19619,10207929
git -C ... grep -l 'IA-P0-2-W5-FIX1-DEV' <每个commit>
#   -> scripts/real_data_acceptance.py, tests/test_p02_w5_fix1.py, docs/P0_2_W5_FIX1_DELIVERY.md
git -C ... log --all --pretty=format: --name-only | sort -u | grep -iE 'AC-v1|DEV-v1|contract|IA-'
#   -> 零命中(历史中从未存在合同命名文件)
git -C ... grep -n 'IA-P0-2-W5-FIX1-AC' 10207929 -- scripts/ tests/ docs/
#   -> DELIVERY.md:3 与 :151,均为编号引用,非全文

# 类2: docs/ 现存文件
grep -rn 'IA-P0-2-W5-FIX1' docs/          # 仅 P0_2_W5_FIX1_DELIVERY.md(编号引用)
grep -rnE '验收条件|通过条件|冻结合同' docs/  # 仅 W4_FIX3 语境一处,无关
ls docs/                                  # 无任何 IA-* 合同文件

# 类3: FIX1包全部成员
grep -rn 'IA-P0-2-W5-FIX1-(AC|DEV)' /tmp/w5_attr_scratch/fix1/
#   -> README_EVIDENCE.txt:2 / P0_2_W5_FIX1_DELIVERY.md:3,均编号引用
shasum -a 256 fix1/P0_2_W5_FIX1_DELIVERY.md docs(DEV)/P0_2_W5_FIX1_DELIVERY.md
#   -> 两侧同为 4cc563624fcec3dc70dc51bac018599b168429a36a6a97a66deb103ce3bf336b(包内副本=DEV原件)

# 类4: W5首轮包全部成员
grep -rn 'IA-P0-2-W5-FIX1-(AC|DEV)' /tmp/w5_attr_scratch/w5r1/   # 零命中
grep -rnE 'IA-P0-2-W5-(AC|DEV)|契约|合同' /tmp/w5_attr_scratch/w5r1/
#   -> 仅 W5原(非FIX1)合同编号引用: README_EVIDENCE.md:3 等3处
```

## 3. 任务C 七轴归因取证
```
# LIVE只读(绝对零写入):
ls ".../investment-agent/data/daily" | grep -E '^global_2026(102[5-9]|1030|1031)'
shasum -a 256 ".../data/daily/global_20261030.json"
#   62526e8cf2995835e4caab4d22586fd167dee03f8ed4ae21e65077d0b374295d == 包内JSON所记快照sha(逐字节同源)
shasum -a 256 ".../scripts/real_data_acceptance.py"   # f9ca189c…(D5复测,不变)
python3(json解析) global_2026102[7-9]/2026103[01]/20261101.json BTC字段+series跨文件对照
# DEV只读:
grep -n 'BTC|coinbase|candle' scripts/real_data_acceptance.py   # L302-317抓取, L525-558 check_btc
sed -n '372,382p' scripts/real_data_acceptance.py               # _ours(来源透传,retrieved_at)
# LIVE采集器只读:
grep -n 'yfinance|history|auto_adjust|close|datetime.now' scripts/global_market_collector.py
#   L71 BTC->BTC-USD; L106-107 history(period,auto_adjust=True); L119/136 iloc[-1];
#   L180 close; L188 date; L194-200 文件名/time=datetime.now()
# 外部抓取(公开无密钥,留档workspace):
PYTHONDONTWRITEBYTECODE=1 python3 docs/w5_attr_workspace/fetch_coinbase.py
# 重算:
PYTHONDONTWRITEBYTECODE=1 python3 docs/w5_attr_workspace/recompute_btc_pairings.py
#   -> docs/w5_attr_workspace/recompute_btc_pairings.out.txt
# 注: 脚本已改为自包含(Coinbase包内证据经zipfile直接读 /tmp/w5-evidence/ 原zip,
#     不依赖已清理的scratch);/tmp scratch清理后复跑一次,输出与首次逐位一致。
```

## 4. 脚本一致性
```
git -C ... show 4a19619e...:scripts/real_data_acceptance.py | shasum -a 256
#   62b2ed82d7dbbcdb23566ffd5772de62c25d23fec3c9c8e9cd6f69204ba12ba1 == DEV HEAD == 正式运行JSON所记sha
```

## 5. 轮末(见自述报告)
```
shasum -a 256 /tmp/w5-evidence/*.zip        # 轮末复测=轮初
rm -rf /tmp/w5_attr_scratch                 # scratch清理(前后对照见报告)
git status / git diff --stat <基点>..HEAD   # 仅允许路径
git push origin dev/p0-2-w5-attr && git ls-remote origin | grep attr
```
