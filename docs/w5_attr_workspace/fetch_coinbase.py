#!/usr/bin/env python3
"""R003 任务C外部抓取(可选增强): Coinbase公开无密钥candles API只读重取。

目的:
  1. 小时线(2026-10-29T20:00Z~2026-10-30T00:00Z): 证明/证伪
     "我方78822.59 ≈ 2026-10-29 23:00 UTC时点市价"(轴⑥在途candle假设)。
  2. 日线(2026-10-26~2026-10-31): 独立复核W5首轮包DIAGNOSTIC所引Coinbase
     收盘序列(该文件属开发者自述来源,需独立重取后方可作独立证据)。

留档: 每次抓取保存 .meta.txt(URL/UTC时间/HTTP状态/响应SHA256/字节数)
      与 .body 原文于本目录,提交入DEV分支作为附录C证据。
仅归因证据,非验收口径变更。
"""
import hashlib
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

URLS = {
    "cb_btc_hourly_1029T20_1030T00Z": (
        "https://api.exchange.coinbase.com/products/BTC-USD/candles"
        "?granularity=3600&start=2026-10-29T20%3A00%3A00Z&end=2026-10-30T00%3A00%3A00Z"
    ),
    "cb_btc_daily_1026_1031": (
        "https://api.exchange.coinbase.com/products/BTC-USD/candles"
        "?granularity=86400&start=2026-10-26T00%3A00%3A00Z&end=2026-10-31T00%3A00%3A00Z"
    ),
}


def fetch(name, url):
    import datetime
    req = urllib.request.Request(url, headers={"User-Agent": "w5-attribution-audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        status = r.status
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sha = hashlib.sha256(body).hexdigest()
    body_path = os.path.join(HERE, name + "__" + now.replace(":", "") + ".body")
    with open(body_path, "wb") as f:
        f.write(body)
    with open(os.path.join(HERE, name + ".meta.txt"), "w") as f:
        f.write("url=%s\nfetched_utc=%s\nhttp_status=%d\nbody_sha256=%s\nbody_bytes=%d\nsaved=%s\n"
                % (url, now, status, sha, len(body), os.path.basename(body_path)))
    print(name, "status=%d" % status, "sha256=%s" % sha, "bytes=%d" % len(body))
    print(body.decode()[:1200])
    return body


def main():
    for name, url in URLS.items():
        try:
            fetch(name, url)
        except Exception as e:  # noqa: BLE001 - 留阻断证据
            with open(os.path.join(HERE, name + ".meta.txt"), "w") as f:
                f.write("url=%s\nerror=%r\n" % (url, e))
            print(name, "ERROR", repr(e))


if __name__ == "__main__":
    main()
